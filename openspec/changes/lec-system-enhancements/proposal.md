## Why

Enhance usability, filtering, auditability, and standby lifecycle management across the Sistema LEC web application:
1. Restrict patient/procedure visibility in the Pacientes module when logged into an Especialidade profile.
2. Display the user who performed each action in the Histórico module.
3. Dynamically calculate remaining Standby days based on elapsed time and allow extending, reducing, or requesting cancellation of an active Standby.
4. Add a "Descrição" column with a modal viewer button in the Sistema LEC tracking table (for both pending and completed requests).

## What Changes

- **Pacientes Module - Mandatory Specialty Filter**:
  - When the active profile is an `ESPECIALIDADE`, force filtering in `Pacientes.vue` to only show patients and procedures belonging to that specific specialty.
- **Histórico Module - User Column**:
  - Add a "Usuário" column in `Historico.vue` displaying the username or name of the user who performed/approved the action.
- **Standby Lifecycle & Management**:
  - Automatically calculate remaining Standby days dynamically (`diasTotais - diasDecorridos`).
  - In `InteracoesLec.vue` under the "Solicitar Standby" tab: if an active Standby exists for the patient's procedure, show the current remaining days, a field to modify/extend the standby duration, and a button to request Standby cancellation.
- **Sistema LEC Tracking Table - Description Column**:
  - Add a "Descrição" column in `InteracoesLec.vue` (for all tabs and statuses). Clicking the description button opens a modal showing the full justification text.

## Capabilities

### New Capabilities
- `lec-system-enhancements`: Provides mandatory specialty filtering in Pacientes, user audit column in Histórico, dynamic Standby countdown and management, and justification description modal viewer in tracking table.

### Modified Capabilities
<!-- None -->

## Impact

- **Frontend**: `Pacientes.vue`, `Historico.vue`, `InteracoesLec.vue`
- **Backend**: Ensure user info is preserved and exposed in request and history responses if needed.
