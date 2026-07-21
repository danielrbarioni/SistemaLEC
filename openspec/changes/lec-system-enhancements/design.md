## Context

This change introduces four usability and business logic enhancements requested for Pacientes, Histórico, and Sistema LEC modules.

## Goals / Non-Goals

**Goals:**
- **Pacientes**: Filter `pacientesProcessados` in `Pacientes.vue` to match `perfisStore.perfilAtivo.especialidade` when active profile is `ESPECIALIDADE`.
- **Histórico**: Add "Usuário" table header and column cell in `Historico.vue`.
- **Standby Management**: Calculate remaining standby days using date math (`tempo_standby - Math.floor((now - data_aprovacao) / (1000 * 60 * 60 * 24))`). In `InteracoesLec.vue` (Solicitar Standby tab), if an active Standby exists, display remaining days, input for updating standby time, and button for cancellation request.
- **Tracking Table Description Column**: Add a "Descrição" column in `InteracoesLec.vue` tracking tables with an interactive icon/button that opens a detail modal showing the full justification text.

## Decisions

1. **Pacientes Specialty Filter**:
   - In `Pacientes.vue`, compute `especialidadeFiltroObrigatoria`. If active profile is `ESPECIALIDADE`, force `filtroEspecialidade` to that specialty and disable the dropdown. Filter patient procedures to only include those under that specialty.

2. **Histórico User Column**:
   - Render `solic.usuario || solic.user || '—'` in a new `<th>` and `<td>` in `Historico.vue`.

3. **Dynamic Standby Calculation & UI**:
   - Compute `diasRestantesStandby(s)` based on `s.tempo_standby` and `s.data_acao` / `s.data_criacao`.
   - In `InteracoesLec.vue` Standby tab, check if the loaded patient procedure has an active Standby.
   - If active: show badge with remaining days, offer options: "Alterar tempo de standby" or "Cancelar standby".

4. **Description Modal**:
   - Add state `modalDescricao = ref<{ aberto: boolean, titulo: string, texto: string }>()`.
   - In tracking table, add column `Descrição` with a button to trigger `abrirModalDescricao(solic)`.

## Risks / Trade-offs

- **[Risk]** Date format differences when computing elapsed standby days.
  → **Mitigation**: Parse dates safely using ISO strings or `Date.parse()`, defaulting to original `tempo_standby` if parsing fails.
