# Fluxo de Disputas (Relatar Problema) - GoDrive

Este documento detalha o funcionamento técnico e de negócio do fluxo de disputa, permitindo que o aluno relate problemas em aulas e que o suporte medie a resolução.

## 1. Visão Geral
O objetivo da disputa é proteger o aluno em caso de não prestação do serviço pelo instrutor e impedir o pagamento automático (auto-complete) de aulas com problemas, garantindo a integridade financeira da plataforma.

## 2. Ciclo de Vida do Agendamento
O status `DISPUTED` é um estado de exceção no ciclo de vida de um agendamento.

```mermaid
stateDiagram-v2
    CONFIRMED --> DISPUTED: Aluno relata problema (após término)
    DISPUTED --> COMPLETED: Suporte resolve a favor do Instrutor
    DISPUTED --> CANCELLED: Suporte resolve a favor do Aluno (estorno)
    DISPUTED --> CONFIRMED: Suporte reagenda aula (novo horário)
```

## 3. Abertura da Disputa (Aluno)
### Condições para Abertura:
*   O agendamento deve estar no status `CONFIRMED`.
*   A hora de término da aula deve ter passado (`lesson_end_datetime < now`).
*   O aluno clica no botão **"Relatar Problema"** na tela de detalhes da aula.

### Fluxo no Mobile:
1.  **Botão de Ação:** Exibido apenas em aulas confirmadas que já passaram.
2.  **Motivos Pré-definidos:**
    *   Instrutor não compareceu.
    *   Problemas mecânicos no veículo.
    *   Outro (Campo de texto livre).
3.  **Campos de Contato:** O aluno deve informar um telefone e e-mail para contato.
4.  **Campo de Descrição do Ocorrido:** O aluno deve descrever o ocorrido.
5.  **Transição:** O agendamento passa para `status = 'disputed'`.

## 4. Mediação e Suporte (Admin)
Uma vez que a aula está em disputa:
*   **Bloqueio de Auto-complete:** O job de conclusão automática ignora agendamentos em disputa.
*   **Chat:** O canal de comunicação entre aluno e instrutor permanece aberto para tentativa de resolução direta.
*   **Painel Administrativo:** O suporte visualiza a descrição do problema, o histórico do chat e a telemetria (início da aula/localização).

## 5. Modelo de Dados de Disputa (Persistência)
Atualmente temos o status DISPUTED, mas precisamos de uma tabela ou extensão para guardar o histórico daquela briga. Deveríamos implementar uma entidade Dispute vinculada ao agendamento contendo:

*   **Motivo e Descrição:** O que o aluno escreveu ao abrir o problema.
*   **Notas do Administrador:** Um log interno para o suporte anotar o que foi conversado com cada parte.
*   **Status da Disputa:** OPEN, UNDER_REVIEW, RESOLVED.
*   **Histórico de Resolução:** Quem resolveu, quando e qual foi o veredito (reembolso total, parcial ou pagamento ao instrutor).

## 6. Resoluções Possíveis

### A. Favorável ao Instrutor (`COMPLETED`)
Decidido se o serviço foi prestado ou o aluno faltou sem justificativa.
*   **Ação:** O status muda para `COMPLETED`.
*   **Financeiro:** O saldo é liberado para o instrutor via split do Mercado Pago.
*   **Fluxo:** É como se a aula tivesse sido concluída normalmente, mas com uma nota interna de que passou por uma disputa.

### B. Favorável ao Aluno (`CANCELLED`)
Decidido se o instrutor faltou ou houve falha grave no serviço.
*   **Ação:** O status muda para `CANCELLED`.
*   **Financeiro:** Um reembolso (total ou parcial) é disparado para o aluno via gateway.

### C. Reagendamento Mediado (`CONFIRMED`)
Decidido em comum acordo para realizar a aula em outro momento.
*   **Ação:** O suporte define uma nova `scheduled_datetime` e o status volta para `CONFIRMED`.
*   **Financeiro:** O pagamento permanece retido na plataforma.

## 7. Implementação Técnica

### Backend
*   **Entidade `Scheduling`:** Já possui o status `DISPUTED` e o método `open_dispute()`.
*   **Novo Job/UseCase:** `ResolveDisputeUseCase` para lidar com as transições finais.
*   **Tabela `disputes`:** Para armazenar notas de auditoria e logs de decisão.

### Frontend
*   **LessonDetailsScreen:** Lógica condicional para exibir o botão de disputa.
*   **Visualização de Status:** Badge específico para `DISPUTED` indicando que o suporte está analisando.
