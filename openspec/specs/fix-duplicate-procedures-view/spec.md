# fix-duplicate-procedures-view Specification

## Purpose
TBD - created by archiving change fix-duplicate-procedures-view. Update Purpose after archive.
## Requirements
### Requirement: Exibição apenas de procedimentos reais na visualização do paciente
O sistema SHALL exibir apenas procedimentos válidos obtidos de solicitações ou cadastros reais, eliminando registros vazios ou fictícios ("Procedimento não informado").

#### Scenario: Visualizar ficha do paciente com solicitações aprovadas
- **WHEN** o usuário acessar a tela de Pacientes
- **THEN** o sistema SHALL mostrar na ficha de cada paciente apenas os procedimentos oriundos de solicitações aprovadas
- **THEN** o sistema SHALL NOT exibir procedimentos fantasmas ou em branco adicionais

