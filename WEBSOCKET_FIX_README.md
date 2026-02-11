# Correção do WebSocket - App Background/Foreground

## 🐛 Problema Identificado

O WebSocket perdia conexão quando o app ia para segundo plano e não reconectava ao voltar. Os erros eram:

1. **Code 1006** (abnormal closure) quando o app ia para background - comportamento normal no mobile
2. O código tratava **1006 como falha de autenticação**, tentando fazer refresh desnecessário
3. Tentava refresh mesmo com token válido, recebia o mesmo token e desistia
4. Não detectava quando o app voltava do background

## ✅ Soluções Implementadas

### 1. **websocket.ts** - Correções principais

#### a) Removido 1006 da lista de erros de autenticação
```typescript
// ANTES - tratava 1006 como erro de auth
const AUTH_FAILURE_CODES = [1008, 4401, 4403];
const isAuthFailure = AUTH_FAILURE_CODES.includes(event.code) || event.code === 1006;

// DEPOIS - 1006 é tratado como desconexão normal
const AUTH_FAILURE_CODES = [1008, 4401, 4403];
const isAuthFailure = AUTH_FAILURE_CODES.includes(event.code) ||
    event.reason?.toLowerCase().includes('unauthorized');
```

#### b) Adicionado controle de app state
```typescript
private _isAppInBackground = false;

setAppInBackground(isBackground: boolean): void {
    this._isAppInBackground = isBackground;
    
    if (!isBackground && !this.isConnected && this.token) {
        // App voltou do background - reconectar
        this.reconnectAttempts = 0;
        this.attemptReconnect();
    }
}
```

#### c) Melhorada lógica de refresh de token
```typescript
// ANTES - desistia se recebia o mesmo token
if (newToken && newToken !== this.token) {
    this.token = newToken;
    this.createConnection();
} else {
    console.warn('Não foi possível obter token renovado.');
}

// DEPOIS - aceita qualquer token válido
if (newToken) {
    this.token = newToken;
    this.createConnection();
} else {
    console.warn('Não foi possível obter token válido.');
}
```

#### d) Prevenção de reconexões em background
```typescript
// Não tenta reconectar se app está em background
if (this._isAppInBackground) {
    console.log('[WebSocket] Não reconectando - app em background');
    return;
}
```

### 2. **useWebSocket.ts** - Novo hook com AppState

Gerencia automaticamente:
- Conexão/desconexão baseada em autenticação
- Detecção de background/foreground via `AppState`
- Refresh de token quando necessário
- Status de conexão em tempo real

## 📦 Como Usar

### Instalação

1. Substitua os arquivos:
   - `websocket.ts` → arquivo corrigido
   - Adicione `useWebSocket.ts` → novo hook

### Uso Básico

```typescript
import { useWebSocket } from './hooks/useWebSocket';

function ChatScreen() {
    const { isConnected, status, sendMessage, onMessage } = useWebSocket(isAuthenticated);

    // Escutar mensagens
    useEffect(() => {
        const unsubscribe = onMessage((message) => {
            console.log('Mensagem recebida:', message);
            
            if (message.type === 'chat_message') {
                // Processar mensagem de chat
            }
        });

        return unsubscribe;
    }, [onMessage]);

    // Enviar mensagem
    const handleSend = () => {
        if (isConnected) {
            sendMessage({
                type: 'chat_message',
                data: { text: 'Olá!' }
            });
        }
    };

    // Mostrar status
    return (
        <View>
            <Text>Status: {status}</Text>
            {/* ... resto da UI */}
        </View>
    );
}
```

### Uso Simplificado (apenas receber mensagens)

```typescript
import { useWebSocketMessages } from './hooks/useWebSocket';

function NotificationListener() {
    useWebSocketMessages((message) => {
        if (message.type === 'notification') {
            showNotification(message.data);
        }
    });

    return null;
}
```

## 🔄 Fluxo de Reconexão

### Cenário 1: App vai para background
```
1. Sistema fecha conexão WebSocket (code 1006)
2. WebSocket detecta _isAppInBackground = true
3. NÃO tenta reconectar (economiza bateria)
4. Status muda para 'disconnected'
```

### Cenário 2: App volta para foreground
```
1. AppState.addEventListener detecta 'active'
2. setAppInBackground(false) é chamado
3. WebSocket verifica: !isConnected && token existe
4. Reseta reconnectAttempts e reconecta imediatamente
5. Status muda para 'reconnecting' → 'connected'
```

### Cenário 3: Token expirou (erro 4401/4403)
```
1. WebSocket fecha com código de auth (4401/4403)
2. handleAuthFailureReconnect() é chamado
3. tokenGetter(true) força refresh via HTTP interceptor
4. Recebe novo token e reconecta
5. Se refresh falhar após 2 tentativas, desconecta
```

### Cenário 4: Erro de rede normal
```
1. WebSocket fecha (qualquer código != auth)
2. attemptReconnect() com backoff exponencial
3. Busca token atual (sem forçar refresh)
4. Tenta reconectar até 10 vezes
5. Delay: 1s → 2s → 4s → 8s → 16s → 30s (max)
```

## 🎯 Principais Mudanças

| Aspecto | Antes | Depois |
|---------|-------|--------|
| Code 1006 | Tratado como erro de auth | Tratado como desconexão normal |
| Token válido | Rejeitado se igual ao anterior | Aceito e usado para reconexão |
| App background | Tentava reconectar inutilmente | Pausa reconexões |
| App foreground | Não detectava retorno | Reconecta automaticamente |
| Gestão de estado | Manual, sem hook | Hook React com AppState |
| Refresh de token | Sempre forçado | Só quando necessário |

## 🧪 Como Testar

1. **Teste de background/foreground:**
   ```
   - Abra o app e conecte
   - Coloque em background (botão home)
   - Aguarde 5 segundos
   - Volte para o app
   - ✅ Deve reconectar automaticamente
   ```

2. **Teste de token expirado:**
   ```
   - Deixe o app aberto até o token expirar (~15min)
   - ✅ Deve fazer refresh e reconectar automaticamente
   ```

3. **Teste de erro de rede:**
   ```
   - Ative modo avião por 3 segundos
   - Desative modo avião
   - ✅ Deve reconectar com backoff exponencial
   ```

## 📝 Notas Importantes

- O hook `useWebSocket` deve ser usado **uma vez** no componente raiz (ex: `App.tsx`)
- Outros componentes podem usar `useWebSocketMessages` para escutar mensagens
- O status de conexão é propagado via callback, não precisa passar por props
- O WebSocketService é singleton - apenas uma instância existe
- Tokens são gerenciados pelo `tokenManager` do axios.ts

## 🔧 Configurações Opcionais

Você pode ajustar os parâmetros no `WebSocketService`:

```typescript
private maxReconnectAttempts = 10;      // Máximo de tentativas
private maxAuthRetries = 2;             // Tentativas de refresh de token
private baseReconnectDelay = 1000;      // Delay inicial (1s)
private maxReconnectDelay = 30000;      // Delay máximo (30s)
private pingIntervalMs = 30000;         // Intervalo de ping (30s)
```

## 🐛 Debug

Para ver logs detalhados, procure por:
- `[WebSocket]` - Logs do WebSocketService
- `[useWebSocket]` - Logs do hook React
- `[Axios]` - Logs do refresh de token

Exemplo de log saudável:
```
[WebSocket] App foi para background
[WebSocket] Desconectado (code: 1006, reason: Software caused connection abort)
[WebSocket] Não reconectando - app em background
[WebSocket] App voltou para foreground
[WebSocket] Reconectando após retorno do background...
[WebSocket] Conectado
```
