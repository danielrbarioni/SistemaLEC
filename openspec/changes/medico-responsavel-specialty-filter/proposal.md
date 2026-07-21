## Why

In the "Sistema LEC" module (`InteracoesLec.vue`), when filling out a request form (inclusion, edit, etc.), the "Médico Responsável" field allows picking or searching for a doctor. Currently, if an specialty is not yet selected or defined, the field allows arbitrary typing or lists all doctors without filtering. 

Requiring an specialty to be defined before enabling the "Médico Responsável" field, disabling it with a placeholder message when undefined, and filtering the autocomplete list to only show users with function "Médico" registered under that specific specialty in the Perfis module ensures data consistency and prevents invalid entries.

## What Changes

- **Field Disabling & Placeholder**:
  - If no specialty is selected or pre-defined in the form, the "Médico Responsável" input field remains disabled (greyed out) with placeholder text `"Selecione a especialidade primeiro"`.
  - Once an specialty is selected or pre-defined (e.g., when the active profile is an ESPECIALIDADE or an specialty is selected from the dropdown), the field becomes enabled.
- **Dynamic Doctor List Filtering**:
  - The selectable/searchable list of doctors for "Médico Responsável" will dynamically filter registered users (`/api/usuarios`) who have `funcao == 'Médico'` and whose `especialidade` matches the selected/active specialty.

## Capabilities

### New Capabilities
- `medico-responsavel-specialty-filter`: Restricts and filters the "Médico Responsável" field in Sistema LEC based on the selected specialty and registered doctors.

### Modified Capabilities
<!-- None -->

## Impact

- **Frontend**:
  - `frontend/src/views/InteracoesLec.vue`: Update form binding, input disabled state, placeholder string, and compute filtered doctor list based on `form.especialidade` (or active profile specialty) and registered users with function "Médico".
