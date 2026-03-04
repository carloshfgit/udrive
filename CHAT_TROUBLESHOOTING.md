# 🔧 Chat em Tempo Real — Troubleshooting & Análise

> **Data**: 04/03/2026  
> **Problema**: Mensagens do chat não estão chegando em tempo real entre dois dispositivos de teste (Expo).

---

## Sumário

1. [Melhores Práticas da Indústria](#1-melhores-práticas-da-indústria)
2. [Arquitetura Atual do Sistema](#2-arquitetura-atual-do-sistema)
3. [Comparação: Melhores Práticas vs. Sistema Atual](#3-comparação-melhores-práticas-vs-sistema-atual)
4. [Possíveis Causas do Problema](#4-possíveis-causas-do-problema)
5. [Recomendações de Correção](#5-recomendações-de-correção)

---

## 1. Melhores Práticas da Indústria

### 1.1 Arquitetura WebSocket

| Prática | Descrição |
|---------|-----------|
| **Conexão persistente bidirecional** | WebSocket mantém conexão TCP aberta, permitindo envio/recebimento instantâneo sem overhead HTTP |
| **Abordagem híbrida REST + WebSocket** | REST para operações CRUD (histórico, auth), WebSocket para tempo real |
| **PubSub para multi-instância** | Redis/Kafka para distribuir mensagens entre múltiplas instâncias do backend (scaling horizontal) |
| **Gerenciamento de sessão distribuído** | Mapeamento `user_id → gateway_node` para rotear mensagens ao servidor correto |

### 1.2 Heartbeat & Keepalive

| Prática | Descrição |
|---------|-----------|
| **Ping/Pong periódico** | Intervalos de 10-30s para detectar conexões "mortas silenciosas" |
| **Timeout de pong** | Se o pong não chega em X segundos após o ping, a conexão é considerada morta |
| **Heartbeat ao nível de aplicação** | Além do ping/pong do protocolo WebSocket, implementar heartbeat no nível da app para maior controle |

### 1.3 Reconexão Automática

| Prática | Descrição |
|---------|-----------|
| **Backoff exponencial com jitter** | Delay crescente + aleatoriedade para evitar "thundering herd" |
| **Limite de tentativas** | Máximo de N tentativas antes de desistir e alertar o usuário |
| **Recuperação de estado** | Após reconectar: re-subscrever canais, buscar mensagens perdidas, deduplicar |
| **Detecção de transição de rede** | Reconectar ao mudar entre WiFi ↔ celular |

### 1.4 Entrega Confiável de Mensagens

| Prática | Descrição |
|---------|-----------|
| **Persistência antes de ACK** | Salvar no banco antes de confirmar ao sender |
| **IDs únicos para deduplicação** | Cada mensagem tem UUID, permitindo deduplicação no cliente |
| **Mensagens offline** | Armazenar e entregar quando o destinatário reconectar |
| **Push notifications como fallback** | Quando o destinatário está offline, push notification alerta sobre a nova mensagem |
| **Confirmação de entrega (ACK)** | O servidor confirma ao sender que a mensagem foi persistida |

### 1.5 Considerações Mobile

| Prática | Descrição |
|---------|-----------|
| **Gerenciamento de AppState** | Desconectar ou reduzir atividade quando em background |
| **Reconexão no foreground** | Reconectar imediatamente ao voltar para foreground |
| **Cache local** | Armazenar mensagens localmente para exibição instantânea |
| **Otimismo na UI** | Exibir mensagem imediatamente ao enviar, antes da confirmação do servidor |
| **Fallback de polling** | Se WebSocket falhar, polling periódico como último recurso |

---

## 2. Arquitetura Atual do Sistema

### 2.1 Visão Geral

```
┌──────────────────┐     WebSocket (wss)    ┌──────────────────┐
│  Mobile (Expo)   │◄─────────────────────► │  FastAPI Backend │
│                  │                         │                  │
│  websocket.ts    │                         │  chat_handler.py │
│  useWebSocket.ts │                         │  conn_manager.py │
│  useMessages.ts  │                         │                  │
└──────────────────┘                         └────────┬─────────┘
                                                      │
                                              Redis PubSub
                                                      │
                                             ┌────────┴─────────┐
                                             │  redis_pubsub.py │
                                             └──────────────────┘
```

### 2.2 Fluxo de Envio de Mensagem

1. **Cliente A** envia `{type: "send_message", receiver_id, content}` via WebSocket
2. **Backend** executa `SendMessageUseCase`:
   - Valida usuários e agendamento ativo
   - Filtra conteúdo proibido
   - Persiste no banco de dados
3. **Backend** envia `{type: "message_sent", data}` ao **Cliente A** (confirmação)
4. **Backend** publica via Redis PubSub no canal `user:{receiver_id}`
5. O callback `on_pubsub_message` do **receptor** entrega a mensagem ao ConnectionManager
6. **ConnectionManager** envia `{type: "new_message", data}` ao **Cliente B** via WebSocket
7. **Cliente B** recebe no `useWebSocket.handleMessage` → atualiza React Query cache

### 2.3 Componentes Backend

| Arquivo | Responsabilidade |
|---------|-----------------|
| `chat_handler.py` | Endpoint WebSocket `/ws/chat`, handlers para cada tipo de mensagem, loop principal |
| `connection_manager.py` | Gerencia conexões ativas em memória, suporta multi-device (até 5/user) |
| `redis_pubsub.py` | PubSub Redis para comunicação entre instâncias, listener em background |
| `send_message_use_case.py` | Validação de negócio + persistência |
| `chat_notification_decorators.py` | Dispara push notification após envio da mensagem |
| `auth.py` | Autenticação JWT via query string |
| `message_types.py` | Constantes de tipos de mensagem do protocolo |

### 2.4 Componentes Frontend (Mobile/Expo)

| Arquivo | Responsabilidade |
|---------|-----------------|
| `websocket.ts` | Singleton `WebSocketService` — gerencia conexão, reconexão, ping/pong |
| `websocketStore.ts` | Zustand store com status da conexão (`connected`/`reconnecting`/`disconnected`) |
| `useWebSocket.ts` | Hook React no nível do app — conecta/desconecta, despacha eventos para React Query |
| `useMessages.ts` | Hook específico do chat — carrega histórico, envia mensagens, fallback REST |
| `chatApi.ts` | Funções REST para fallback (envio, histórico, conversas) |
| `ChatRoomScreen.tsx` | Tela de conversa — FlatList invertida, ChatBubble, ChatInput |

---

## 3. Comparação: Melhores Práticas vs. Sistema Atual

### ✅ Práticas Já Adotadas

| Prática | Implementação |
|---------|--------------|
| Conexão WebSocket persistente | ✅ `websocket.ts` cria conexão persistente com backend |
| REST + WebSocket híbrido | ✅ REST para auth/histórico, WebSocket para tempo real |
| Redis PubSub | ✅ `redis_pubsub.py` para comunicação entre instâncias |
| Multi-device | ✅ `ConnectionManager` suporta até 5 conexões/user |
| Ping/Pong keepalive | ✅ A cada 30s (`pingIntervalMs = 30000`) |
| Backoff exponencial | ✅ 1s → 2s → 4s → ... → 30s (max) |
| Limite de reconexão | ✅ Max 10 tentativas |
| Auth por token JWT | ✅ Token na query string, refresh automático |
| Fallback REST | ✅ `useMessages.ts` tem polling de 5s quando WS desconecta |
| Push notifications | ✅ `NotifyOnSendMessage` envia push quando offline |
| Gerenciamento AppState | ✅ Detecta foreground/background via `AppState` |
| Persistência antes de ACK | ✅ Mensagem salva no banco antes de confirmar ao sender |
| Confirmação ao sender | ✅ `message_sent` enviado de volta ao remetente |
| UUID de mensagens | ✅ IDs únicos para deduplicação |

### ⚠️ Práticas Parciais ou com Problemas

| Prática | Status | Observação |
|---------|--------|------------|
| Timeout de Pong | ⚠️ **Não implementado** | O cliente envia ping mas **não valida** se recebeu pong. Conexão "morta silenciosa" não é detectada |
| Jitter no backoff | ⚠️ **Não implementado** | Backoff sem randomização — dois dispositivos reconectando podem colidir |
| Recuperação de mensagens perdidas | ⚠️ **Parcial** | `invalidateQueries` no `useWebSocket` força refetch, mas **não há mecanismo de sincronização** de mensagens perdidas durante desconexão |
| Detecção de transição de rede | ⚠️ **Não implementado** | A detecção é apenas por `AppState` (foreground/background), não monitora mudanças de rede WiFi → Celular |
| Otimismo na UI | ⚠️ **Não implementado** | Mensagem só aparece após confirmação do servidor (race condition possível) |
| Cache local persist | ⚠️ **Parcial** | React Query cache em memória, não há persistência local (SQLite/AsyncStorage) |

### ❌ Principais Gaps

| Gap | Impacto | Status |
|-----|---------|--------|
| **PubSub callback com bug de parsing** | O callback no `chat_handler.py` tentava re-parsear dados já parseados, falhando silenciosamente | ✅ **Corrigido** |
| **Sobrescrita de callbacks PubSub** | Em multi-device, apenas o último dispositivo conectado recebia mensagens | ✅ **Corrigido** |
| **Sem detecção de pong timeout** | Conexões mortas silenciosas não eram detectadas, impedindo reconexão | ✅ **Corrigido** |

---

## 4. Possíveis Causas do Problema (Status: Resolvido)

Todas as causas críticas identificadas foram corrigidas. A combinação do bug de parsing no PubSub com a sobrescrita de callbacks era de fato a raiz do problema de mensagens não chegarem em tempo real.

---

## 5. Recomendações de Correção (Status: Implementado)

As recomendações de **Prioridade Alta** foram totalmente implementadas e validadas.

---

## 6. Soluções Aplicadas

### 6.1 Correção do Callback PubSub (Back end)
**Onde**: `backend/src/interface/websockets/chat_handler.py`

Removida a lógica complexa de dupla deserialização. Como o `RedisPubSubService` já entrega o payload como um dicionário Python parseado, o callback agora apenas encaminha esse dicionário diretamente ao `ConnectionManager`. Isso eliminou erros de `TypeError` e `JSONDecodeError` que ocorriam silenciosamente durante a entrega.

### 6.2 Suporte a Múltiplos Callbacks por Canal (Back end)
**Onde**: `backend/src/infrastructure/external/redis_pubsub.py`

Alterada a estrutura interna `_callbacks` de um dicionário simples para um mapeamento de `canal -> lista de callbacks`.
- Ao conectar um novo dispositivo, seu callback é **adicionado** à lista.
- Ao desconectar, apenas aquele callback específico é removido.
- Isso permite que mensagens enviadas via Redis sejam distribuídas para **todos** os dispositivos conectados do usuário simultaneamente, resolvendo o problema de um dispositivo "desativar" o outro.

### 6.3 Implementação de Heartbeat com Pong Timeout (Front end)
**Onde**: `mobile/src/lib/websocket.ts`

Implementada detecção ativa de conexão morta:
1. O cliente mantém uma flag `_pongReceived`.
2. Antes de enviar um novo `ping` (a cada 30s), o sistema verifica se o `pong` do ciclo anterior foi recebido.
3. Caso não tenha sido recebido, a conexão é forçada a fechar (`ws.close()`), o que dispara o ciclo de reconexão automática e ativa o fallback de polling temporário.

### 6.4 Correção de Marcação de Leitura Indesejada (Front end)
**Onde**: `mobile/src/features/shared-features/chat/hooks/useMessages.ts`

**Problema**: Mensagens eram marcadas como lidas automaticamente assim que chegavam via WebSocket, mesmo que o usuário não estivesse na tela de chat (desde que a tela permanecesse montada na pilha de navegação).

**Solução**:
- Integrado o hook `useIsFocused()` do React Navigation.
- O efeito automático de `mark_as_read` agora possui um guarda adicional: `if (!isFocused) return;`.
- Agora as mensagens são marcadas como lidas **apenas** quando a tela de chat está visível e focada pelo usuário.

---

## Conclusão Final

Com a implementação destas correções, o sistema de chat atingiu o comportamento esperado: mensagens chegam instantaneamente em múltiplos dispositivos, a conexão é resiliente a quedas silenciosas e a marcação de leitura respeita a presença real do usuário na tela.


