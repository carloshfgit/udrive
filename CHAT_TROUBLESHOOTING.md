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

| Gap | Impacto |
|-----|---------|
| **PubSub callback com dupla indireção** | O callback `on_pubsub_message` no `chat_handler.py` recebe dados do Redis e re-entrega via `manager.send_to_user`. Porém, o **sender já publica via PubSub E o callback do receptor também chama `send_to_user`**, gerando potencial duplicação ou perda dependendo do timing |
| **Sem detecção de pong timeout** | Se a rede cair silenciosamente (ex: WiFi → célula), o cliente continua achando que está conectado por até 30s+ sem perceber que a conexão está morta |
| **Sem rehydration após reconexão** | Ao reconectar, o sistema invalida queries mas não tem certeza de que todas as mensagens perdidas serão recuperadas no gap |

---

## 4. Possíveis Causas do Problema

### 🔴 Causa Principal Mais Provável

#### 4.1 Problema no Callback do Redis PubSub — Dupla Serialização/Deserialização

O callback `on_pubsub_message` no `chat_handler.py` (linhas 337-358) trata o `payload_data` com múltiplos branches:

```python
async def on_pubsub_message(payload_data: dict) -> None:
    if isinstance(payload_data, dict) and "data" in payload_data:
        message_str = payload_data["data"]
        if isinstance(message_str, bytes):
            message_str = message_str.decode("utf-8")
        if isinstance(message_str, str):
            parsed_data = json.loads(message_str)
            await manager.send_to_user(user_id, parsed_data)
        else:
            await manager.send_to_user(user_id, message_str)
    else:
        await manager.send_to_user(user_id, payload_data)
```

**Problema**: O `redis_pubsub.py` já faz `json.loads(message["data"])` na linha 162 antes de chamar o callback. Portanto, o `payload_data` que chega ao callback **já é um dict parseado**. Mas o callback espera um dict com chave `"data"` dentro (formato do Redis raw), gerando **conflito de formato**.

Se o `RedisPubSubService._listen()` já parseia o JSON:
```python
data = json.loads(message["data"])
await callback(data)
```

Então o `payload_data` que chega ao `on_pubsub_message` é:
```python
{"type": "new_message", "data": {"id": "...", "sender_id": "...", ...}}
```

Neste caso, `payload_data["data"]` é o **dict interno da mensagem**, não uma string JSON. O código tenta fazer `json.loads()` em um dict, o que falha com `TypeError`, caindo no fallback que pode enviar dados incompletos ou no formato errado.

### 🟡 Outras Causas Possíveis

#### 4.2 Conexão WebSocket não Estabelecida (ngrok + Expo)

**Cenário**: Usando ngrok com Expo para testes, a URL do WebSocket precisa ser `wss://` (não `ws://`) e o ngrok pode ter limitações:
- ngrok free tier pode ter latência alta ou timeouts
- A URL ngrok muda a cada reinício, e o app pode estar usando uma URL antiga
- O ngrok pode não manter WebSocket connections por muito tempo

**Verificar**: A variável `EXPO_PUBLIC_API_URL` está apontando para o ngrok correto com `https://`?

#### 4.3 Token JWT Expirado Durante Conexão

**Cenário**: Se o token JWT expira enquanto o WebSocket está conectado:
- O backend **não detecta** expiração mid-connection (o token é validado apenas no handshake)
- A conexão permanece ativa, mas se o backend reiniciar ou a conexão cair, a reconexão pode falhar
- O código verifica close codes de auth, mas o real fechamento por ngrok pode vir como `1006` (abnormal) sem reason text

#### 4.4 Sem Detecção de Pong Timeout (Conexão "Morta Silenciosa")

**Cenário**: O cliente envia ping a cada 30s, mas **nunca verifica se o pong chegou**:
```typescript
// websocket.ts, linhas 323-328
private startPing(): void {
    this.stopPing();
    this.pingInterval = setInterval(() => {
        this.send({ type: 'ping' });
    }, this.pingIntervalMs);
}
```

Se a conexão caiu (ex: ngrok timeout, troca de rede), o cliente continua enviando pings sem perceber que ninguém os recebe. O estado `isConnected` permanece `true`, impedindo o fallback de polling.

#### 4.5 Problema com Multi-Device e PubSub Subscribe

**Cenário**: Quando um usuário conecta de dois dispositivos:
- Cada dispositivo subscreve no mesmo canal Redis `user:{user_id}`
- **Porém**, `RedisPubSubService._callbacks` é um **dict simples** (1 callback por canal)
- Na segunda conexão, o callback do segundo dispositivo **sobrescreve** o do primeiro

```python
# redis_pubsub.py, linha 116
self._callbacks[channel] = callback  # Sobrescreve o anterior!
```

**Resultado**: Apenas o **último dispositivo conectado** recebe mensagens via PubSub. O primeiro dispositivo fica "surdo".

#### 4.6 Race Condition: Mensagem Chega Antes do Subscribe

**Cenário**: No `chat_handler.py` (linhas 332-360):
1. O usuário conecta (`manager.connect`)
2. O PubSub subscreve (`pubsub.subscribe`)

Se uma mensagem chegar entre os passos 1 e 2, ela é perdida porque o canal ainda não está subscrito.

#### 4.7 Desconexão Background no Mobile sem Reconexão Adequada

**Cenário**: Quando o app vai para background:
- iOS mata WebSocket connections após ~30s
- Android pode matar após algum tempo
- O sistema detecta `_isAppInBackground = true` e **não reconecta**
- Quando volta para foreground, deveria reconectar, mas:
  - Se `_isIntentionalClose` ficou como `true` (bug de estado), não reconecta
  - Se o token expirou durante o background, a reconexão falha silenciosamente

---

## 5. Recomendações de Correção

### 🔴 Prioridade Alta (Provavelmente Causando o Bug)

#### 5.1 Corrigir o Callback do PubSub

O callback `on_pubsub_message` precisa ser simplificado, já que `RedisPubSubService._listen()` já parseia o JSON:

```python
async def on_pubsub_message(payload_data: dict) -> None:
    """Callback para mensagens do PubSub."""
    try:
        await manager.send_to_user(user_id, payload_data)
    except Exception as e:
        logger.error("pubsub_message_error", user_id=str(user_id), error=str(e))
```

#### 5.2 Corrigir Multi-Device PubSub Overwrite

Modificar `RedisPubSubService` para suportar múltiplos callbacks por canal:

```python
# Mudar de:
self._callbacks: dict[str, Callable] = {}

# Para:
self._callbacks: dict[str, list[Callable]] = {}
```

Ou, melhor: manter um **único subscribe** por canal `user:{user_id}` no nível do `ConnectionManager`, e não por conexão WebSocket individual.

#### 5.3 Implementar Pong Timeout

```typescript
private pongReceived = true;

private startPing(): void {
    this.stopPing();
    this.pingInterval = setInterval(() => {
        if (!this.pongReceived) {
            // Conexão morta detectada
            this.ws?.close(4000, 'Pong timeout');
            return;
        }
        this.pongReceived = false;
        this.send({ type: 'ping' });
    }, this.pingIntervalMs);
}

// No handler de mensagens:
private notifyListeners(message: WSMessage): void {
    if (message.type === 'pong') {
        this.pongReceived = true;
        return;
    }
    // ... resto
}
```

### 🟡 Prioridade Média

#### 5.4 Detecção de Mudança de Rede

Usar `@react-native-community/netinfo` para detectar mudanças WiFi ↔ celular:
```typescript
NetInfo.addEventListener(state => {
    if (state.isConnected && !wsService.isConnected) {
        wsService.reconnect();
    }
});
```

#### 5.5 Adicionar Jitter ao Backoff

```typescript
const jitter = Math.random() * 1000; // 0-1s de aleatoriedade
const delay = Math.min(
    this.baseReconnectDelay * Math.pow(2, this.reconnectAttempts) + jitter,
    this.maxReconnectDelay
);
```

#### 5.6 Sincronização de Mensagens Perdidas

Após reconectar, buscar mensagens mais recentes que a última recebida usando um timestamp:
```typescript
// Após reconexão bem-sucedida:
queryClient.invalidateQueries({ queryKey: ['chat-messages'] });
```
Já é feito parcialmente, mas deveria ser feito explicitamente no `onopen` do WebSocket.

### 🟢 Prioridade Baixa

- Implementar UI otimista (exibir mensagem antes do ACK)
- Persistência local com AsyncStorage/SQLite
- Rate limiting no frontend para evitar spam de mensagens
- Logging estruturado no frontend para debug em produção

---

## Conclusão

O problema mais provável é uma **combinação das causas 4.1 e 4.5**:

1. **O callback do PubSub tem um bug de parsing** que pode causar falha silenciosa na entrega da mensagem ao destinatário
2. **A sobrescrita de callbacks no PubSub** faz com que, em cenários multi-device, apenas o último dispositivo conectado receba mensagens

Adicionalmente, **a falta de detecção de pong timeout** (causa 4.4) faz com que, se a conexão cair silenciosamente (comum com ngrok), o app continue achando que está conectado e não ative o fallback de polling.
