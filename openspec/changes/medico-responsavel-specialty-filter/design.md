## Context

Currently, in `frontend/src/views/InteracoesLec.vue`, `medicosConhecidos` is populated with a generic list of doctor names or historical values. The input for "Médico Responsável" is enabled regardless of whether an specialty has been chosen in the form.

## Goals / Non-Goals

**Goals:**
- Make the "Médico Responsável" input field disabled and greyed out when `especialidadeForm` (or selected specialty) is empty/undefined, showing placeholder `"Selecione a especialidade primeiro"`.
- When an specialty is defined, enable the input field.
- Filter candidate doctors from registered users (`/api/usuarios`) who have `funcao === 'Médico'` and whose `especialidade` matches the form's active specialty.

**Non-Goals:**
- Changing backend database models or endpoints (users already contain `funcao` and `especialidade`).

## Decisions

1. **Computed Property `especialidadeForm`**:
   - Determine current specialty in form: if active profile is `ESPECIALIDADE`, use `perfisStore.perfilAtivo.especialidade`. Otherwise, use `form.value.especialidade`.

2. **Computed Property `medicosEspecialidadeFiltrados`**:
   - Filter `usuariosList.value` where `u.funcao === 'Médico'` and `u.especialidade === especialidadeForm.value`. Extract `u.nome`.

3. **Template Input Bindings**:
   - `:disabled="camposEdicaoBloqueados || !especialidadeForm"`
   - `:placeholder="!especialidadeForm ? 'Selecione a especialidade primeiro' : 'Selecione ou digite o médico...'"`
   - Bind datalist or select dropdown to `medicosEspecialidadeFiltrados`.

## Risks / Trade-offs

- **[Risk]** No doctors registered for a specialty yet.
  → **Mitigation**: If no users are registered with function `Médico` for that specialty, allow manual typing (free text input with datalist) so users are not blocked.
