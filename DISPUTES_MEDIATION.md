Evoluir do CRUD genérico do `sqladmin` para um **Centro de Mediação de Disputas** dedicado.

Como seria essa interface:

### 1. Layout Triple-Pane (Painel de Três Colunas)

Em vez de uma tabela simples, teríamos uma visão 360º da aula:

- **Coluna Esquerda (Contexto):** Mini-perfis do Aluno e Instrutor (com foto, nota e histórico de outras disputas), detalhes do veículo e mapa de telemetria mostrando onde ambos estavam no horário da aula.
- **Coluna Central (Evidências):** O histórico completo do chat daquela aula, destacando mensagens em que houve conflito, e uma galeria de fotos/prints que o aluno anexou ao abrir o problema.
- **Coluna Direita (Resolução):** Um "Wizard" de decisão interactivo.

### 2. Decision Wizard (Assistente de Decisão)

Em vez de digitar `favor_student`, você teria botões visuais:

- **Botão "Dar ganho ao Aluno" (Vermelho/Estorno):** Ao clicar, ele abriria sub-opções visuais como "Estorno Total 100%" ou "Estorno Parcial 50%".
- **Botão "Dar ganho ao Instrutor" (Verde/Liberar):** Um clique que já dispararia a liberação do split do Mercado Pago.
- **Botão "Reagendar" (Azul/Prorrogar):** Abriria um calendário para você escolher a nova data em comum acordo.

### 3. Feedback Visual de Status

- **Timeline do Evento:** Uma linha do tempo visual mostrando: `Agendado` -> `Aula Terminada` -> `Disputa Aberta pelo Aluno` -> `Análise Iniciada pelo Admin`.
- **Live Preview Financeiro:** Um resumo dizendo: "Ao clicar aqui, R$ 150,00 serão devolvidos ao cartão do aluno final 4242".

### 4. Como poderíamos construir isso?

1. **Custom Page no SQLAdmin:** Criaríamos um template customizado em HTML/JinJa2 dentro do backend que consome os mesmos endpoints, mas com uma roupagem de dashboard moderno.