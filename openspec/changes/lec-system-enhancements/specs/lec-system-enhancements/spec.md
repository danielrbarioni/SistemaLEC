## ADDED Requirements

### Requirement: Mandatory specialty filter in Pacientes module
When logged in with an `ESPECIALIDADE` profile type, the Pacientes module SHALL restrict displayed patients and procedures strictly to that active specialty.

#### Scenario: User logged in as ESPECIALIDADE profile
- **WHEN** a user with profile type `ESPECIALIDADE` (e.g., "Plástica") views the Pacientes view
- **THEN** only patients and procedures for "Plástica" are visible and the specialty filter dropdown is locked to "Plástica".

### Requirement: User column in Histórico module
The Histórico view SHALL render a dedicated "Usuário" column indicating which user executed or submitted each historical action.

#### Scenario: Viewing history table
- **WHEN** an authenticated user views the Histórico table
- **THEN** each row displays the username/name of the user responsible for that entry under the "Usuário" column.

### Requirement: Dynamic Standby countdown and active Standby management
Standby duration SHALL decrease dynamically as calendar days elapse. In the "Solicitar Standby" tab of Sistema LEC, if an active Standby exists for the selected patient procedure, the system SHALL display the updated remaining days, provide an input to modify the duration, and provide an option to request Standby cancellation.

#### Scenario: Viewing active Standby status
- **WHEN** a patient procedure with an active 70-day Standby is selected 10 days after approval
- **THEN** the system shows 60 remaining days, allows updating the duration, and offers a Standby cancellation request button.

### Requirement: Description column and modal viewer in Sistema LEC tracking
The tracking table in Sistema LEC SHALL include a "Descrição" column with a button to view the full justification provided for the request.

#### Scenario: Clicking description button in tracking table
- **WHEN** a user clicks the description/justification button on a request row in Sistema LEC
- **THEN** a modal opens displaying the complete justification text for that request.
