## ADDED Requirements

### Requirement: Disable Médico Responsável input until specialty is defined
In the Sistema LEC form, the "Médico Responsável" field SHALL be disabled (greyed out) with placeholder `"Selecione a especialidade primeiro"` whenever no specialty is selected or active.

#### Scenario: Specialty is not selected
- **WHEN** the user opens the Sistema LEC form and no specialty is selected
- **THEN** the "Médico Responsável" input is disabled and displays placeholder `"Selecione a especialidade primeiro"`.

#### Scenario: Specialty is selected
- **WHEN** an specialty is selected or active
- **THEN** the "Médico Responsável" input becomes enabled with placeholder `"Selecione ou digite o médico..."`.

### Requirement: Filter candidate doctors by selected specialty and Médico function
The options/datalist for "Médico Responsável" SHALL strictly include users registered in the Perfis module who have `funcao == "Médico"` and belong to the selected specialty.

#### Scenario: Selecting doctor for active specialty
- **WHEN** the user searches or selects a doctor in "Médico Responsável" for specialty X
- **THEN** only registered users with function "Médico" belonging to specialty X appear in the dropdown/datalist.
