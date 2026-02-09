# Planejamento de Implementação: Chat Instrutor

Este documento descreve o plano de etapas para a implementação do sistema de chat entre instrutores e alunos, com foco na interface e regras de negócio para o **Instrutor**.

## 1. Visão Geral
O chat permitirá a comunicação direta entre instrutores e alunos que possuam vínculos ativos no GoDrive. Para garantir a segurança e a integridade do marketplace, o sistema contará com filtros de conteúdo e restrições de visibilidade.

---

## 2. Requisitos de Regra de Negócio

### Visibilidade das Conversas
- **Filtro de Atividade:** O instrutor só verá conversas com alunos que possuam pelo menos um agendamento nos status: `PENDING` (Pendente), `CONFIRMED` (Confirmado) ou `RESCHEDULE_REQUESTED` (Reagendamento Solicitado).
- **Inatividade:** Agendamentos `CANCELLED` (Cancelados) ou `COMPLETED` (Concluídos) não devem originar ou manter um card de conversa visível na aba principal de mensagens do instrutor.
- **Unicidade:** Deve aparecer exatamente um card por aluno (mesmo que haja múltiplos agendamentos ativos com o mesmo aluno).

### Restrição de Conteúdo (Keyword Filter)
Para evitar desvios da plataforma (transações por fora), o chat deve bloquear palavras-chave e padrões que envolvam contato externo:
- **E-mails:** Padrões contendo `@` e domínios.
- **Telefones:** Sequências numéricas longas (8 a 11 dígitos).
- **Plataformas Externas:** `whatsapp`, `zap`, `wpp`, `telegram`, `instagram`, `facebook`, `insta`, `fb`, `celular`, `telefone`.
- **Pagamentos Externos:** `pix`, `transferência`, `depósito`, `conta bancária`.

### Detalhes do Aluno
- Dentro da tela de chat, haverá um botão para visualizar detalhes do aluno.
- Ao clicar, será exibida uma lista com **todos** os agendamentos (passados, presentes e futuros) que o aluno possui com o instrutor logado.

---

## 3. Etapas de Implementação

### Etapa 1: Backend - Camada de Domínio e Infraestrutura
- [ ] **Entidade `Message`:** Criar entidade em `domain/entities/message.py` com campos: `id`, `sender_id`, `receiver_id`, `content`, `timestamp`, `is_read`.
- [ ] **Modelo SQL:** Criar `infrastructure/db/models/message_model.py`.
- [ ] **Repositório:** Definir interface `imessage_repository.py` e implementação `message_repository_impl.py`.
- [ ] **Migração:** Criar migration Alembic para a tabela `messages`.

### Etapa 2: Backend - Casos de Uso (Application Layer)
- [ ] **`SendMessageUseCase`:** Implementar a lógica de envio.
  - Validar se existe agendamento ativo entre as partes.
  - **Filtro de Palavras-chave:** Implementar serviço de limpeza ou bloqueio de mensagens que contenham padrões proibidos.
- [ ] **`GetInstructorConversationsUseCase`:**
  - Query otimizada para buscar alunos com agendamentos ativos (`PENDING`, `CONFIRMED`, `RESCHEDULE_REQUESTED`).
  - Retornar o aluno acompanhado da última mensagem (se houver).
- [ ] **`GetStudentLessonsForInstructorUseCase`:** Retornar histórico completo de aulas entre o instrutor e um aluno específico.

### Etapa 3: Backend - Interface (API)
- [ ] **Chat Router:** Criar `/api/v1/shared/chat.py` para endpoints de listagem de conversas e mensagens.
- [ ] **Instructor Router:** Atualizar `/api/v1/instructor/schedule.py` ou criar específico para detalhes do aluno.

### Etapa 4: Mobile - Camada de Dados
- [ ] **API Tooling:** Criar `features/shared-features/chat/api/chatApi.ts`.
- [ ] **TanStack Query Hooks:** 
  - `useInstructorConversations`: Para carregar a lista de chats.
  - `useMessages`: Para carregar o histórico de uma conversa.
  - `useSendMessage`: Mutation para enviar novas mensagens.

### Etapa 5: Mobile - Interface do Usuário (UI)
- [ ] **Navegação:** Adicionar a aba "Mensagens" no `InstructorTabNavigator.tsx`.
- [ ] **Lista de Conversas:** Implementar `InstructorChatListScreen.tsx`.
  - Usar `FlatList` com `ConversationCard`.
  - Exibir estado vazio caso não haja agendamentos ativos.
- [ ] **Sala de Chat:** Implementar `ChatRoomScreen.tsx`.
  - Componente de mensagens (balões `MessageBubble`).
  - Campo de input fixo.
  - Botão de "Detalhes do Aluno" no Header ou Action Bar.
- [ ] **Histórico do Aluno:** Implementar `StudentLessonHistoryScreen.tsx` exibindo a lista completa de aulas.

### Etapa 6: Validação e Segurança
- [ ] Testar filtro de palavras-chave no backend.
- [ ] Garantir que o instrutor não consiga enviar mensagens para alunos sem agendamento ativo via API (segurança).
- [ ] Validar tempo de carregamento com TanStack Query (cache e otimização).

---

## 4. Referência de Arquitetura
A implementação deve seguir estritamente o `PROJECT_GUIDELINES.md`:
- Código em Inglês, comentários em Português.
- Frontend em `mobile/src/features/shared-features/chat` pelo fato de ser uma funcionalidade compartilhada (usada por alunos em breve).
- Backend seguindo Clean Architecture (Domain -> Application -> Infrastructure -> Interface).
