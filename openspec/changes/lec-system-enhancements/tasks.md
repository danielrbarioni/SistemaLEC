## 1. Pacientes Module Enhancements

- [x] 1.1 In `frontend/src/views/Pacientes.vue`, enforce mandatory specialty filtering for `ESPECIALIDADE` profile users and filter both patients and their procedures.

## 2. Histórico Module Enhancements

- [x] 2.1 In `frontend/src/views/Historico.vue`, add a "Usuário" column displaying the user who performed each action.

## 3. Standby Lifecycle & Management Enhancements

- [x] 3.1 Implement dynamic standby countdown logic (`tempo_standby` reduced by elapsed days) in `InteracoesLec.vue` and `Pacientes.vue`.
- [x] 3.2 In `InteracoesLec.vue` ("Solicitar Standby" tab), detect if an active Standby exists for the selected patient procedure and display remaining time, input to modify duration, and option to request Standby cancellation.

## 4. Sistema LEC Tracking Table Enhancements

- [x] 4.1 In `InteracoesLec.vue`, add a "Descrição" column to tracking tables (pending & completed) with a button that opens a modal displaying the full justification text.

## 5. Verification & Testing

- [x] 5.1 Verify all changes across Pacientes, Histórico, and Sistema LEC modules.
