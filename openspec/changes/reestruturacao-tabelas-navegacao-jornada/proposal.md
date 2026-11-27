# Proposal

## Why

A estrutura atual de 5 tabelas do módulo **Navegação da Jornada Cirúrgica** mistura, nas tabelas de agendamento/pendência (antigas Tabelas 1 e 3.1), pacientes com consultas agendadas para hoje/data futura e pacientes com consultas agendadas em data passada sem baixa/desfecho no AGHU. Separar estritamente os agendamentos futuros (`Tabela 1.1` para EPO e `Tabela 3.1` para APA) das consultas não realizadas — que passam a consolidar tanto as faltas (do paciente e do profissional) quanto os agendamentos de data passada sem desfecho (`Tabela 1.2` para EPO e `Tabela 3.2` para APA) —, além de renomear as etapas concluídas para `Tabela 2 - Consulta EPO realizada` e `Tabela 4 - APA realizada`, reflete com precisão o fluxo operacional da jornada cirúrgica e prepara cada tabela para receber ações operacionais específicas na próxima evolução.

## What Changes

- **Reestruturação dos painéis da Navegação de 5 para 6 tabelas operacionais**:
  1. **`Tabela 1.1 - Consulta EPO agendada`** (antiga Tabela 1): passa a contemplar **somente** as consultas EPO agendadas para **hoje ou data futura** (`status = 'Agendado'`, `dt_consulta >= hoje`).
  2. **`Tabela 1.2 - Consulta EPO não realizada`** (antiga Tabela 2.1): passa a contemplar tanto as **faltas** (`Falta do paciente` e `Falta do profissional`) quanto as **consultas EPO agendadas de data passada sem desfecho no AGHU** (`Agendado (Data Passada)`).
  3. **`Tabela 2 - Consulta EPO realizada`** (antiga Tabela 2.2): renomeada para remover o sufixo `+ Exames/Pré-Op` do título da aba e do cabeçalho, mantendo integralmente a exibição dos cards de exames pré-operatórios solicitados e consultas pré-operatórias (`RIS`, `PPC`, `RCI`, `OHR`, `PPO`).
  4. **`Tabela 3.1 - APA agendada`** (desmembrada da antiga Tabela 3.1): passa a contemplar **somente** as Avaliações Pré-Anestésicas (APA) agendadas para **hoje ou data futura** (`status = 'Agendado'`, `dt_consulta >= hoje`).
  5. **`Tabela 3.2 - APA não realizada`** (nova tabela desmembrada da antiga Tabela 3.1): contempla as Avaliações Pré-Anestésicas (APA) com **faltas** (`Falta do paciente` e `Falta do profissional`) e as **agendadas de data passada sem desfecho no AGHU** (`Agendado (Data Passada)`).
  6. **`Tabela 4 - APA realizada`** (antiga Tabela 3.2): renomeada para representar o 4º macroestágio da jornada cirúrgica (`status = 'Realizado'`).
- **Ajuste dos filtros modificáveis e da Busca Global**:
  - Os filtros de status de consulta passam a atuar especificamente nas tabelas de não realização (`Tabela 1.2` e `Tabela 3.2`), permitindo filtrar entre `Falta do paciente`, `Falta do profissional` e `Agendado (Data Passada / Sem Desfecho)`.
  - A Busca Global por prontuário/nome passa a pesquisar e exibir badges de localização nas **6 tabelas** (`1.1`, `1.2`, `2`, `3.1`, `3.2` e `4`).
  - Layout do seletor de abas ajustado para acomodar os 6 painéis (`lg:grid-cols-6` / `sm:grid-cols-3`).

## Capabilities

### New Capabilities
- `navegacao-jornada-cirurgica-aghu`: Reestruturação da nomenclatura e composição dos painéis da Navegação da Jornada Cirúrgica em 6 tabelas (`1.1 - Consulta EPO agendada`, `1.2 - Consulta EPO não realizada`, `2 - Consulta EPO realizada`, `3.1 - APA agendada`, `3.2 - APA não realizada` e `4 - APA realizada`).

### Modified Capabilities
<!-- Nenhuma spec principal arquivada em openspec/specs/ é impactada, pois navegacao-jornada-cirurgica-aghu ainda está em changes/ -->

## Impact

- **Backend (`src/routers/navegacao.py`)**:
  - Atualização do endpoint `GET /api/navegacao/paineis` para distribuir os pacientes nas 6 chaves de retorno (`tabela_1_1_epo_agendada`, `tabela_1_2_epo_nao_realizada`, `tabela_2_epo_realizada`, `tabela_3_1_apa_agendada`, `tabela_3_2_apa_nao_realizada`, `tabela_4_apa_realizada`), preservando as regras de progressão temporal (Opção A) e o cache TTL.
- **Frontend (`frontend/src/views/NavegacaoLec.vue`)**:
  - Atualização das abas, contadores, títulos, subtítulos, regras automáticas descritivas, filtros de status (`T1_2` e `T3_2`), filtros exclusivos da `Tabela 2` (`T2`) e Busca Global nas 6 tabelas.
