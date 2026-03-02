# 🚀 Guia Completo: Push Notifications (Expo SDK 53+)

Este guia detalha como configurar notificações push remotas para Android, agora que o suporte foi removido do **Expo Go** no SDK 53.

> [!IMPORTANT]
> **Atenção:** Todos os comandos e configurações abaixo devem ser executados **dentro do diretório `mobile/`** do projeto.

---


## 📋 Pré-requisitos
- Conta no [Expo](https://expo.dev/)
- Projeto no [Firebase Console](https://console.firebase.google.com/)
- Dispositivo Android físico (altamente recomendado)

---

## 1. Configuração do EAS (Expo Application Services)
O Expo agora exige um `projectId` para gerenciar as credenciais de notificação.

1. Instale o EAS CLI globalmente:
   ```bash
   npm install -g eas-cli
   ```
2. Faça login na sua conta Expo:
   ```bash
   eas login
   ```
3. Vincule seu projeto local ao projeto no dashboard do Expo:
   ```bash
   eas project:init
   ```
   *Isso criará automaticamente o campo `extra.eas.projectId` no seu `app.json`.*

---

## 2. Configuração do Firebase (Android)
O Android utiliza o Firebase Cloud Messaging (FCM) para entregar as notificações.

1. No [Firebase Console](https://console.firebase.google.com/), crie um novo projeto (ou use um existente).
2. Adicione um app **Android**:
   - O `package name` deve ser exatamente o mesmo definido no seu `app.json` (ex: `com.seuusuario.godrive`).
3. Baixe o arquivo `google-services.json`.
4. Mova este arquivo para a raiz da pasta `mobile/` do seu projeto.
5. No `app.json`, aponte para o arquivo:
   ```json
   "android": {
     "googleServicesFile": "./google-services.json",
     "package": "com.seuusuario.godrive"
   }
   ```

---

## 3. Credenciais de Notificação
O Expo precisa de permissão para enviar mensagens ao Firebase em seu nome.

1. No Firebase Console, vá em **Configurações do Projeto** > **Contas de Serviço**.
2. Clique em **Gerar nova chave privada**. Isso baixará um arquivo `.json`.
3. No terminal da pasta `mobile/`, rode:
   ```bash
   eas credentials
   ```
4. Selecione `Android` > `development` (ou `production`).
5. Siga as instruções para configurar as **Push Notifications** enviando o arquivo JSON da chave privada que você baixou.

---

## 4. Criando o Development Build
Como o Expo Go não suporta mais notificações remotas no Android, você precisa criar seu próprio "Expo Go personalizado".

1. Instale o cliente de desenvolvimento:
   ```bash
   npx expo install expo-dev-client
   ```
2. Gere e instale o build no dispositivo:
   - **Opção A (Local - Requer Android Studio/SDK):**
     ```bash
     npx expo run:android
     ```
   - **Opção B (EAS Cloud - Gera um APK):**
     ```bash
     eas build --profile development --platform android
     ```
     *Após o build, baixe o APK e instale no celular.*

---

## 5. Testando as Notificações
Com o aplicativo instalado no dispositivo (o ícone do seu app, não o do Expo Go):

1. Inicie o servidor de desenvolvimento:
   ```bash
   npx expo start --dev-client
   ```
2. Abra o app no celular. Se o login estiver configurado, ele deve registrar o token no backend.
3. Pegue o token gerado (veja os logs do terminal) e teste no [Expo Push Tool](https://expo.dev/notifications).

---

## 🛠️ Resumo de Comandos Rápidos
| Ação | Comando |
| :--- | :--- |
| Instalar Ferramentas | `npm install -g eas-cli` |
| Vincular Projeto | `eas project:init` |
| Configurar Chaves | `eas credentials` |
| Rodar App (Dev Build) | `npx expo run:android` |

> [!IMPORTANT]
> Lembre-se: Notificações remotas **NÃO** funcionam no Expo Go oficial (Play Store) a partir do SDK 53. Use sempre o build gerado por você.
