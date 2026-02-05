# Plano de Experiência Visual: Minhas Aulas (ALUNO)

Este documento detalha o design e as funcionalidades das telas de gestão de aulas para o perfil **Aluno**, seguindo as diretrizes de [PROJECT_GUIDELINES.md](file:///home/carloshf/udrive/PROJECT_GUIDELINES.md) e a identidade visual em [VISUAL_IDEA.md](file:///home/carloshf/udrive/VISUAL_IDEA.md).

---

## 1. Tela: Minhas Aulas (Principal)

Esta é a tela central onde o aluno visualiza seus agendamentos ativos.

### **Header (Topo)**
- **Título:** "Minhas Aulas" (Centralizado).
- **Esquerda:** Ícone de seta "Voltar".
- **Direita:** Botão "Histórico" (Ícone de relógio).

### **Corpo (Lista de Aulas)**
Utilização de `FlatList` ou `FlashList` para performance, com os seguintes componentes por item:

#### **Lesson Card**
- **Destaque Temporal:** Data e Hora em uma coluna lateral ou badge proeminente (ex: fundo azul claro, texto azul negrito).
- **Info Instrutor:** Foto quadrada (Avatar) + Nome do Instrutor.
- **Status:** Badge colorido (`confirmed` = azul, `pending` = laranja, `canceled` = vermelho).
- **Ação:** Botão "Ver Detalhes" (Estilo secundário/outline) no rodapé do card.

---

## 2. Tela: Histórico de Aulas

Acessada através do botão no topo da tela principal.

### **Funcionalidades**
- **Lista:** Aulas com status `completed` ou `canceled`.
- **Avaliação:** Para cada aula concluída, exibir um botão "Avaliar Aula" (se ainda não avaliada).
  - Abre modal de `StarRating` (1-5 estrelas) + Comentário.

---

## 3. Tela: Detalhes da Aula

Exibe informações exaustivas sobre um agendamento específico.

### **Estrutura da Tela**
1.  **Informações Gerais:**
    - Data, Horário e Duração.
    - Status atual da aula.
2.  **Bloco do Instrutor:**
    - Perfil resumido (Foto, Nome, Avaliação).
    - **Link:** "Ver Perfil Completo" (Redireciona para o perfil do instrutor).
    - **Ação:** Botão "Chat com Instrutor" (Abre tela de chat via `shared-features/chat`).
3.  **Ações da Aula (Rodapé Fixo):**
    - **Botão Iniciar/Concluir:** Botão de concluir visualmente apagado se não tiver passado 60 minutos desde o clique em iniciar.
    - **Botão Cancelar:** Segue a regra de negócio, ao clicar abre modal de confirmação (Reembolso 100% > 24h, Multa 50% < 24h).

---

## Diretrizes de Implementação (UX/UI)

- **Cores:** Manter o Azul Primário (`#2563EB`) para ações principais e Branco para o fundo dos cards.
- **Feedback:** Utilizar `LoadingState` (Skeletons) durante o carregamento das listas via TanStack Query.
- **Navegação:** Implementada dentro de `features/student-app/scheduling/`.

> [!TIP]
> Use micro-animações no clique dos cards para uma sensação premium (Soft UI).
