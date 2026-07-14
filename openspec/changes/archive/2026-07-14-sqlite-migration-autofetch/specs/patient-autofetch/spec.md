## ADDED Requirements

### Requirement: Busca automática de dados do paciente
O sistema SHALL retornar o nome completo do paciente a partir do banco de dados quando o usuário inserir um prontuário válido na interface do cliente.

#### Scenario: Autopreenchimento com sucesso
- **WHEN** o usuário digitar um prontuário válido no formulário de novas solicitações
- **ENTÃO** o sistema consulta o backend e preenche automaticamente o campo de Nome Completo do paciente

#### Scenario: Paciente não encontrado
- **WHEN** o usuário digitar um prontuário que não existe no banco de dados (AGHU ou local)
- **ENTÃO** o sistema mantém o campo de Nome Completo limpo e exibe um alerta informando que o prontuário não foi encontrado
