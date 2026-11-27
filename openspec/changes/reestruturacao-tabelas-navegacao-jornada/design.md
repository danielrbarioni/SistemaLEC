# Design

## Context

Veja `proposal.md` para a motivação e o escopo funcional. No estado atual (`src/routers/navegacao.py` e `frontend/src/views/NavegacaoLec.vue`), a função `_mapear_status_consulta` já distingue consultas marcadas no AGHU (`ret_seq` 9 ou 20) em dois status:
- `"Agendado"` quando `dt_consulta.date() >= hoje_date` (hoje ou data futura);
- `"Agendado (Data Passada)"` (`status_detalhe = "Agendado (Data Passada / Sem Desfecho)"`) quando `dt_consulta.date() < hoje_date`.

Entretanto, a distribuição atual agrupa `"Agendado"` e `"Agendado (Data Passada)"` na antiga `Tabela 1` (para EPO) e mistura `"Agendado"`, `"Agendado (Data Passada)"`, `"Falta do paciente"` e `"Falta do profissional"` na antiga `Tabela 3.1` (para APA). Com a nova organização solicitada, os estágios de EPO e APA passam a ter simetria completa entre agendamentos futuros (`1.1` e `3.1`), não realizações (`1.2` e `3.2`) e realizações (`2` e `4`).

## Goals / Non-Goals

**Goals:**
- Estruturar o retorno do endpoint `GET /api/navegacao/paineis` nas 6 listas:
  1. `tabela_1_1_epo_agendada` (`status == "Agendado"`)
  2. `tabela_1_2_epo_nao_realizada` (`status in ("Falta do paciente", "Falta do profissional", "Agendado (Data Passada)")`)
  3. `tabela_2_epo_realizada` (`status == "Realizado"`, enriquecida com `exames_solicitados` e `consultas_preop`)
  4. `tabela_3_1_apa_agendada` (`status == "Agendado"`)
  5. `tabela_3_2_apa_nao_realizada` (`status in ("Falta do paciente", "Falta do profissional", "Agendado (Data Passada)")`)
  6. `tabela_4_apa_realizada` (`status == "Realizado"`)
- Atualizar a interface `NavegacaoLec.vue` para exibir os 6 cards/abas de seleção com as nomenclaturas exatas:
  - `Tabela 1.1` — `Consulta EPO agendada`
  - `Tabela 1.2` — `Consulta EPO não realizada`
  - `Tabela 2` — `Consulta EPO realizada` (sem `+ Exames/Pré-Op` no título)
  - `Tabela 3.1` — `APA agendada`
  - `Tabela 3.2` — `APA não realizada`
  - `Tabela 4` — `APA realizada`
- Manter os filtros de status de consulta nas tabelas de não realização (`Tabela 1.2` e `Tabela 3.2`), onde coexistem `Agendado (Data Passada)`, `Falta do paciente` e `Falta do profissional`.

**Non-Goals:**
- Não alterar a lógica de progressão temporal entre os macroestágios EPO e APA (Opção A: `dt_apa.date() >= dt_epo.date()` avança o paciente para o estágio APA `3.1`/`3.2`/`4`).
- Não implementar ainda as ações operacionais dentro das linhas das tabelas (que serão especificadas e incluídas na etapa seguinte, após a validação desta estrutura).

## Decisions

### 1. Critério de Particionamento entre Tabelas `.1` (Agendadas) e `.2` (Não Realizadas)
- **Decisão**:
  - **Estágio EPO** (`not em_estagio_apa`):
    - `item_epo["status"] == "Agendado"` (ou seja, consulta agendada para **hoje ou data futura**) → **`Tabela 1.1 - Consulta EPO agendada`** (`tabela_1_1_epo_agendada`).
    - `item_epo["status"] in ("Agendado (Data Passada)", "Falta do paciente", "Falta do profissional")` → **`Tabela 1.2 - Consulta EPO não realizada`** (`tabela_1_2_epo_nao_realizada`).
    - `item_epo["status"] == "Realizado"` → **`Tabela 2 - Consulta EPO realizada`** (`tabela_2_epo_realizada`).
  - **Estágio APA** (`em_estagio_apa`):
    - `item_apa["status"] == "Agendado"` (ou seja, APA agendada para **hoje ou data futura**) → **`Tabela 3.1 - APA agendada`** (`tabela_3_1_apa_agendada`).
    - `item_apa["status"] in ("Agendado (Data Passada)", "Falta do paciente", "Falta do profissional")` → **`Tabela 3.2 - APA não realizada`** (`tabela_3_2_apa_nao_realizada`).
    - `item_apa["status"] == "Realizado"` → **`Tabela 4 - APA realizada`** (`tabela_4_apa_realizada`).
- **Racional**: Garante que `Tabela 1.1` e `Tabela 3.1` mostrem apenas a agenda viva (hoje/futuro), enquanto `Tabela 1.2` e `Tabela 3.2` concentram todos os casos que exigem resgate/tratativa por não terem sido realizados na data prevista (seja por falta registrada ou por ausência de baixa de atendimento em data pretérita).

### 2. Ordenação de cada uma das 6 Tabelas
- **Decisão**:
  - Todas as 6 tabelas (`Tabela 1.1`, `Tabela 1.2`, `Tabela 2`, `Tabela 3.1`, `Tabela 3.2` e `Tabela 4`): ordenadas da data de consulta **mais antiga para a mais recente** (`ASC`).

## Risks / Trade-offs

- **[Risk] Cache em memória do backend com estrutura antiga de 5 chaves durante atualização** → **Mitigação**: O deploy reinicia o serviço `sistemalec.service` (limpando `_NAVEGACAO_PAINEIS_CACHE`), e o frontend inicializa com fallback seguro `|| []` para cada uma das 6 listas.
