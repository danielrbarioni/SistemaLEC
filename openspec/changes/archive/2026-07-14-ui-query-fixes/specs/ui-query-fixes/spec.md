## ADDED Requirements

### Requirement: Filtro de listagem e busca de pacientes
O sistema SHALL retornar dados de pacientes filtrando pela coluna prontuário do AGHU e listar apenas pacientes ativos no LEC.

#### Scenario: Listar apenas pacientes com movimentações
- **WHEN** o usuário acessar a tela de Pacientes
- **THEN** o sistema exibe apenas pacientes que possuem alguma solicitação ou status local no LEC

#### Scenario: Buscar por prontuário no AGHU
- **WHEN** o usuário buscar um paciente pelo número do prontuário
- **THEN** o sistema SHALL consultar o AGHU mapeando pela coluna prontuário
