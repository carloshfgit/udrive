# Plano de Desenvolvimento Mobile - GoDrive (UDrive)

> **Target:** React Native (Expo) + NativeWind  
> **Escopo:** Interfaces para **Aluno** e **Instrutor**

> [!IMPORTANT]
> Este plano segue as diretrizes de separação por tipo de usuário definidas no `PROJECT_GUIDELINES.md`.
> Telas exclusivas do aluno ficam em `student-app/`, do instrutor em `instructor-app/`, e compartilhadas em `shared-features/`.

---

## Análise Visual de Referência

As imagens de referência estabelecem um padrão visual consistente que deve ser seguido em todas as telas:

### Elementos de Design Identificados

| Elemento | Especificação |
|----------|---------------|
| **Paleta de Cores** | Azul primário (`#2563EB`), Branco (`#FFFFFF`), Cinza suave (`#F3F4F6`), Laranja para destaques de progresso |
| **Tipografia** | Sans-serif moderna, hierarquia clara (títulos grandes, subtítulos médios, texto de corpo menor) |
| **Cards** | Bordas arredondadas (`rounded-2xl`), sombra suave, padding consistente |
| **Ícones** | Outline style, tamanho consistente, cor azul primário |
| **Botões Primários** | Azul sólido, texto branco, cantos bem arredondados |
| **Botões Secundários** | Outline azul, fundo branco ou transparente |
| **Tabs/Segmented Control** | Indicador de seleção com sublinhado ou fundo destacado |
| **Bottom Tab Bar** | 4-5 itens, ícones + labels, item ativo em azul |
| **Progress Bars** | Barras coloridas (azul para legislação, laranja para mecânica), texto de percentual |
| **Tags/Chips** | Fundo azul claro com texto azul, cantos arredondados |

### Padrões de Layout

- **Header**: Seta de voltar à esquerda, título centralizado, ícone de ação à direita (quando aplicável)
- **Listas**: Cards empilhados verticalmente com espaçamento consistente
- **Seções**: Título de seção com link "Ver tudo" alinhado à direita
- **Navegação**: Bottom Tab Bar fixa com 4-5 opções principais

---

## Fase M1: Design System e Componentes Base

**Objetivo:** Estabelecer o Design System unificado e componentes reutilizáveis seguindo o estilo visual das referências.

### Etapa M1.1: Tokens e Tema Global

- [ ] Atualizar `tailwind.config.js` com paleta de cores completa
  - Azul primário e variantes (50-900)
  - Cores de estado (success, warning, error, info)
  - Cores neutras expandidas
- [ ] Definir tipografia customizada
  - Fonte: Inter ou similar via `expo-google-fonts`
  - Escalas de tamanho: xs, sm, base, lg, xl, 2xl, 3xl
  - Pesos: regular (400), medium (500), semibold (600), bold (700)
- [ ] Configurar espaçamentos e bordas padrão
- [ ] Criar arquivo `theme.ts` com constantes exportáveis

### Etapa M1.2: Componentes Shared Adicionais

**Estrutura:** `mobile/src/shared/components/`

- [ ] **Card.tsx** - Container base com variantes (elevated, outlined, filled)
- [ ] **Avatar.tsx** - Foto de perfil com badge de câmera para edição
- [ ] **Badge.tsx** - Tags e chips (ex: "Categoria B", "RECOMENDADO")
- [ ] **ProgressBar.tsx** - Barra de progresso com label de percentual
- [ ] **StarRating.tsx** - Exibição de nota com ícones de estrela
- [ ] **ListItem.tsx** - Item de lista com ícone, título, subtítulo e chevron
- [ ] **SectionHeader.tsx** - Título de seção com botão "Ver tudo"
- [ ] **EmptyState.tsx** - Estado vazio com ilustração e mensagem
- [ ] **LoadingState.tsx** - Skeleton loaders para cards e listas
- [ ] **BottomSheet.tsx** - Modal deslizante inferior para filtros
- [ ] **TabSegment.tsx** - Controle de abas (Lista/Mapa, Próximas/Histórico)
- [ ] **SearchBar.tsx** - Barra de busca com ícone e placeholder
- [ ] **FilterChip.tsx** - Chips de filtro selecionáveis (Categoria, Preço, Avaliação)

### Etapa M1.3: Navegação por Tipo de Usuário

**Estrutura:** `mobile/src/navigation/` e `mobile/src/features/*/navigation/`

- [x] Criar `RootNavigator.tsx` em `navigation/`
  - Verificar `user.userType` após autenticação
  - Redirecionar para `StudentTabNavigator` ou `InstructorTabNavigator`

- [x] Criar `StudentTabNavigator.tsx` em `features/student-app/navigation/`
  - Tab "Início" (Home)
  - Tab "Buscar" (Search/Map)
  - Tab "Aprender" (Learning)
  - Tab "Aulas" (Scheduling)
  - Tab "Perfil" (Profile)

- [x] Criar `InstructorTabNavigator.tsx` em `features/instructor-app/navigation/`
  - Tab "Dashboard" (Home)
  - Tab "Agenda" (Schedule)
  - Tab "Alunos" (Students)
  - Tab "Perfil" (Profile)

- [ ] Configurar ícones e labels das tabs para ambos os navigators
- [ ] Implementar navegação aninhada (Stack dentro de cada Tab)
- [ ] Garantir que `App.tsx` use `RootNavigator` como ponto de entrada

---

## Fase M2: Tela Inicial (Home) e Busca de Instrutores

**Objetivo:** Implementar a experiência principal de descoberta de instrutores.

### Etapa M2.1: Tela Home do Aluno

**Estrutura:** `mobile/src/features/student-app/home/`

- [ ] **Criar feature `home/`**
  - `screens/HomeScreen.tsx`
  - `components/`
  - `hooks/`
  - `api/`

- [ ] **Componentes da HomeScreen:**
  - Header com saudação personalizada e avatar
  - Card de resumo de próxima aula agendada
  - Seção "Instrutores Próximos" (horizontal scroll)
  - Seção "Continue seu progresso" (cursos em andamento)
  - Seção "Simulados Recomendados"

### Etapa M2.2: Tela de Busca de Instrutores

**Estrutura:** `mobile/src/features/student-app/search/`

- [ ] **Criar feature `search/`**
  - `screens/InstructorSearchScreen.tsx`
  - `components/InstructorCard.tsx`
  - `components/FilterModal.tsx`
  - `components/MapView.tsx`
  - `hooks/useInstructorSearch.ts`
  - `api/searchApi.ts`

- [ ] **InstructorSearchScreen.tsx:**
  - SearchBar no topo
  - Linha de FilterChips (Categoria, Preço, Avaliação)
  - TabSegment para alternar Lista/Mapa
  - Lista de InstructorCards ou visualização em mapa

- [ ] **InstructorCard.tsx:**
  - Layout conforme imagem de referência
  - Avatar à direita
  - Nome, avaliação (estrela + número), veículo, categoria
  - Preço por hora em destaque
  - Botão "Ver Perfil"

- [ ] **Integração com Backend:**
  - Hook `useInstructorSearch` com TanStack Query
  - Filtros como parâmetros de query
  - Paginação infinita para lista

### Etapa M2.3: Integração com Mapa

**Estrutura:** `mobile/src/features/student-app/map/`

- [ ] Configurar `react-native-maps` com estilo customizado
- [ ] Criar marcadores personalizados para instrutores
- [ ] Implementar busca por região visível do mapa
- [ ] Cluster de marcadores para muitos instrutores próximos
- [ ] Modal de preview ao tocar em marcador

---

## Fase M3: Perfil do Instrutor e Agendamento

**Objetivo:** Permitir ao aluno visualizar detalhes do instrutor e iniciar agendamento.

### Etapa M3.1: Tela de Perfil do Instrutor (Visualização pelo Aluno)

**Estrutura:** `mobile/src/features/student-app/instructor-view/`

> [!NOTE]
> Esta feature é a visualização do perfil do instrutor **pelo aluno**. Não confundir com `instructor-app/` que contém as telas **do instrutor**.

- [ ] **Criar feature `instructor/`**
  - `screens/InstructorProfileScreen.tsx`
  - `components/ProfileHeader.tsx`
  - `components/ServicesList.tsx`
  - `components/ReviewsList.tsx`
  - `components/VehicleGallery.tsx`
  - `components/AvailabilityCalendar.tsx`
  - `hooks/useInstructorProfile.ts`
  - `api/instructorApi.ts`

- [ ] **InstructorProfileScreen.tsx:**
  - Foto grande no topo com gradiente overlay
  - Informações: nome, avaliação, categoria, veículo
  - Seção "Sobre" com biografia
  - Seção "Veículo" com galeria de fotos
  - Seção "Disponibilidade" com calendário inline
  - Seção "Avaliações" com lista de reviews
  - Botão fixo no rodapé "Agendar Aula"

### Etapa M3.2: Fluxo de Agendamento

**Estrutura:** `mobile/src/features/shared-features/scheduling/`

> [!NOTE]
> Agendamento é uma feature compartilhada: alunos fazem booking, instrutores confirmam/gerenciam.

- [ ] **Telas do fluxo:**
  - `screens/SelectDateTimeScreen.tsx` - Seleção de data e horário
  - `screens/ConfirmBookingScreen.tsx` - Resumo e confirmação
  - `screens/BookingSuccessScreen.tsx` - Confirmação visual

- [ ] **Componentes:**
  - `components/CalendarPicker.tsx` - Seletor de data visual
  - `components/TimeSlotPicker.tsx` - Grid de horários disponíveis
  - `components/BookingSummary.tsx` - Resumo do agendamento

- [ ] **Hooks e API:**
  - `hooks/useAvailability.ts` - Buscar disponibilidade
  - `hooks/useCreateBooking.ts` - Mutation para criar agendamento
  - `api/schedulingApi.ts` - Endpoints de agendamento

---

## Fase M4: Centro de Aprendizado

**Objetivo:** Implementar área de cursos teóricos e simulados para o aluno.

### Etapa M4.1: Tela Principal do Centro de Aprendizado

**Estrutura:** `mobile/src/features/student-app/learning/`

- [ ] **Criar feature `learning/`**
  - `screens/LearningCenterScreen.tsx`
  - `screens/CourseDetailScreen.tsx`
  - `screens/LessonScreen.tsx`
  - `screens/SimuladoScreen.tsx`
  - `screens/SimuladoResultScreen.tsx`
  - `components/`
  - `hooks/`
  - `api/`

- [ ] **LearningCenterScreen.tsx:**
  - Seção "Meus Cursos" com cards de progresso conforme imagem
  - Link "Ver tudo" para lista completa de cursos
  - Cards de curso com:
    - Ícone representativo
    - Nome do curso
    - Barra de progresso com percentual
    - Contador de aulas (ex: "12 de 15 aulas concluídas")
  - Seção "Simulados" com card destacado "RECOMENDADO"
  - Grid 2x2 de tópicos de simulado:
    - Sinalização
    - Direção Defensiva
    - Primeiros Socorros
    - Meio Ambiente

### Etapa M4.2: Telas de Curso e Aulas

- [ ] **CourseDetailScreen.tsx:**
  - Header com progresso geral
  - Lista de módulos/aulas com status (concluído, em progresso, bloqueado)
  - Botão "Continuar de onde parou"

- [ ] **LessonScreen.tsx:**
  - Conteúdo da aula (texto, imagens)
  - Navegação entre aulas (anterior/próxima)
  - Marcação de aula como concluída

### Etapa M4.3: Sistema de Simulados

- [ ] **SimuladoScreen.tsx:**
  - Timer de 60 minutos
  - Questões com alternativas
  - Navegação entre questões
  - Barra de progresso de questões respondidas
  - Botão "Finalizar Simulado"

- [ ] **SimuladoResultScreen.tsx:**
  - Porcentagem de acerto
  - Detalhamento por categoria
  - Correção das questões erradas
  - Botões "Refazer" e "Ver Correção"

---

## Fase M5: Gestão de Aulas (Aluno)

**Objetivo:** Permitir ao aluno gerenciar suas aulas agendadas.

### Etapa M5.1: Tela de Minhas Aulas

**Estrutura:** `mobile/src/features/scheduling/`

- [ ] **Atualizar feature `scheduling/`**
  - `screens/MyLessonsScreen.tsx`
  - `screens/LessonDetailScreen.tsx`
  - `components/LessonCard.tsx`
  - `components/LessonStatusBadge.tsx`

- [ ] **MyLessonsScreen.tsx:**
  - TabSegment "Próximas" / "Histórico"
  - Lista de LessonCards

- [ ] **LessonCard.tsx:**
  - Data e hora em destaque
  - Nome e foto do instrutor
  - Localização com link para mapa
  - Status (confirmada, pendente, concluída, cancelada)
  - Ações: cancelar, reagendar, avaliar

### Etapa M5.2: Detalhes da Aula

- [ ] **LessonDetailScreen.tsx:**
  - Todas as informações da aula
  - Informações do instrutor com link para perfil
  - Mapa com localização do ponto de encontro
  - Ações contextuais baseadas no status
  - Chat com instrutor (link)

### Etapa M5.3: Ações e Fluxos

- [ ] **Cancelamento:**
  - Modal de confirmação com aviso sobre multa (se < 24h)
  - Feedback visual após cancelamento

- [ ] **Avaliação:**
  - Modal/Tela de avaliação pós-aula
  - Seleção de nota (1-5 estrelas)
  - Campo de comentário opcional
  - Submissão e confirmação

---

## Fase M6: Perfil do Aluno

**Objetivo:** Implementar área de perfil e configurações do aluno.

### Etapa M6.1: Tela de Perfil Principal

**Estrutura:** `mobile/src/features/shared-features/profile/`

> [!NOTE]
> Perfil é uma feature compartilhada com algumas variações entre aluno e instrutor.

- [ ] **ProfileScreen.tsx (Atualizar conforme imagem de referência):**
  - Header com avatar grande (com badge de câmera para editar foto)
  - Nome do aluno
  - Tag de categoria (ex: "Categoria B")
  - Lista de opções com ícones:
    - Informações Pessoais
    - Meus Agendamentos
    - Histórico de Aulas
    - Pagamentos
    - Configurações
  - Botão "Sair da Conta" em destaque (outline vermelho)
  - Versão do app no rodapé

### Etapa M6.2: Sub-telas do Perfil

- [ ] **PersonalInfoScreen.tsx:**
  - Edição de dados pessoais
  - Campos: nome, telefone, CPF, data de nascimento
  - Localização (importante para o mapa e busca de instrutores próximos)

- [ ] **PaymentMethodsScreen.tsx:**
  - Lista de cartões salvos
  - Adicionar novo cartão (Stripe SDK)
  - Definir cartão padrão
  - Remover cartão

- [ ] **PaymentHistoryScreen.tsx:**
  - Lista de transações
  - Filtro por período
  - Detalhes de cada transação

- [ ] **SettingsScreen.tsx:**
  - Notificações (toggles)
  - Termos de uso
  - Política de privacidade
  - Exportar meus dados (LGPD)
  - Excluir conta (LGPD)

### Etapa M6.3: Edição de Foto de Perfil

- [ ] **Hook `useImagePicker.ts`:**
  - Integrar `expo-image-picker`
  - Opções: câmera ou galeria
  - Crop circular
  - Upload para API

---

## Fase M7: Integrações e Polimento

**Objetivo:** Integrar todas as features e polir a experiência.

### Etapa M7.1: Notificações Push

- [ ] Configurar `expo-notifications`
- [ ] Handlers para diferentes tipos:
  - Lembrete de aula
  - Confirmação de agendamento
  - Promoções e novidades
- [ ] Deep linking a partir de notificações

### Etapa M7.2: Estados de Loading e Erro

- [ ] Implementar Skeleton loaders para todas as listas
- [ ] Estados de erro com opção de retry
- [ ] Pull-to-refresh em listas principais
- [ ] Feedback visual para ações (toasts/snackbars)

### Etapa M7.3: Performance e Otimização

- [ ] Memoização de componentes pesados (`React.memo`, `useMemo`, `useCallback`)
- [ ] Virtualização de listas longas (`FlashList`)
- [ ] Lazy loading de imagens
- [ ] Otimização de bundles

### Etapa M7.4: Acessibilidade

- [ ] Labels para screen readers
- [ ] Contraste adequado de cores
- [ ] Tamanhos de toque mínimos (44x44)
- [ ] Suporte a fontes do sistema (acessibilidade)

## Fase M8: Interface do Instrutor (instructor-app)

**Objetivo:** Implementar todas as telas exclusivas do instrutor.

> [!IMPORTANT]
> Todas as telas desta fase ficam em `mobile/src/features/instructor-app/`

### Etapa M8.1: Dashboard do Instrutor

**Estrutura:** `mobile/src/features/instructor-app/screens/`

- [x] **InstructorDashboardScreen.tsx:**
  - Resumo de ganhos do mês
  - Próximas aulas agendadas
  - Estatísticas (total de alunos, avaliação média)
  - Alertas de pendências (aulas a confirmar)

### Etapa M8.2: Gestão de Agenda

**Estrutura:** `mobile/src/features/instructor-app/screens/`

- [ ] **InstructorScheduleScreen.tsx:**
  - Calendário visual com aulas marcadas
  - Lista de aulas do dia selecionado
  - Ações: confirmar, cancelar, reagendar

- [ ] **InstructorAvailabilityScreen.tsx:**
  - Configuração de dias e horários disponíveis
  - Bloqueio de datas específicas
  - Horário de início e fim de expediente

### Etapa M8.3: Gestão de Alunos

**Estrutura:** `mobile/src/features/instructor-app/screens/`

- [ ] **InstructorStudentsScreen.tsx:**
  - Lista de alunos atendidos
  - Filtro por status (ativos, concluídos)
  - Histórico de aulas por aluno

- [ ] **StudentDetailScreen.tsx:**
  - Informações do aluno
  - Histórico de aulas realizadas
  - Notas e observações

### Etapa M8.4: Dashboard Financeiro

**Estrutura:** `mobile/src/features/instructor-app/screens/`

- [ ] **InstructorEarningsScreen.tsx:**
  - Resumo de ganhos (semana, mês, total)
  - Gráfico de evolução
  - Lista de transações
  - Informações de repasse (Stripe Connect)

### Etapa M8.5: Perfil do Instrutor (Edição)

**Estrutura:** `mobile/src/features/instructor-app/screens/`

- [x] **InstructorProfileScreen.tsx:**
  - Visualização do perfil público
  - Link para edição

- [ ] **InstructorEditProfileScreen.tsx:**
  - Edição de dados profissionais
  - Foto de perfil e galeria do veículo
  - Biografia e experiência
  - Categoria de CNH
  - Valor da hora/aula
  - Dados do veículo (modelo, ano, placa)

---

## Resumo de Arquivos e Estrutura Final

```text
mobile/src/
├── app/                              # Expo Router
├── features/
│   ├── auth/                         # ✅ Compartilhado (login, registro)
│   │   ├── screens/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── navigation/
│   ├── student-app/                  # 🎓 Telas exclusivas do ALUNO
│   │   ├── home/                     # HomeScreen
│   │   ├── search/                   # InstructorSearchScreen
│   │   ├── map/                      # MapView
│   │   ├── learning/                 # LearningCenterScreen
│   │   ├── instructor-view/          # Visualização do perfil do instrutor
│   │   └── navigation/
│   │       └── StudentTabNavigator.tsx
│   ├── instructor-app/               # 🚗 Telas exclusivas do INSTRUTOR
│   │   ├── screens/                  # Dashboard, Agenda, Alunos, Ganhos
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── navigation/
│   │       └── InstructorTabNavigator.tsx
│   └── shared-features/              # 🔄 Features COMPARTILHADAS
│       ├── scheduling/               # Agendamento (booking e confirmação)
│       ├── profile/                  # Perfil (aluno e instrutor)
│       └── chat/                     # Mensagens (futuro)
├── shared/
│   ├── components/                   # UI components reutilizáveis
│   ├── hooks/                        # Hooks compartilhados
│   └── theme.ts                      # Tokens de design
├── lib/                              # Configs (axios, query, zustand)
└── navigation/
    └── RootNavigator.tsx             # Ponto de entrada (decide por user_type)
```

---

## Cronograma Estimado

| Fase | Descrição | Duração | Dependências |
|------|-----------|---------|--------------|
| M1 | Design System e Componentes | 1-2 semanas | - |
| M2 | Home e Busca (Aluno) | 2-3 semanas | M1 |
| M3 | Perfil Instrutor e Agendamento | 2-3 semanas | M2, Backend |
| M4 | Centro de Aprendizado | 2-3 semanas | M1 |
| M5 | Gestão de Aulas (Aluno) | 1-2 semanas | M3 |
| M6 | Perfil do Aluno | 1-2 semanas | M1 |
| M7 | Integrações e Polimento | 2 semanas | M1-M6 |
| **M8** | **Interface do Instrutor** | **3-4 semanas** | M1, Backend |

**Total estimado: 14-21 semanas**

---

## Referências Visuais

As imagens de referência foram usadas para definir o estilo visual:

1. **Perfil do Aluno** - Layout de perfil com avatar, tags e lista de opções
2. **Busca de Instrutores** - Cards de instrutor com filtros e tabs Lista/Mapa
3. **Centro de Aprendizado** - Cursos com barras de progresso e grid de simulados

---

> **Nota:** Este plano deve ser executado em conjunto com o backend já desenvolvido até a Fase 5. A integração com APIs deve seguir os padrões de TanStack Query definidos no `PROJECT_GUIDELINES.md`.
