# Spec Delta

## MODIFIED Requirements

### Requirement: Busca automática de dados do paciente
O sistema SHALL retornar o nome do paciente a partir do banco de dados quando o usuário inserir um prontuário válido na interface do cliente, priorizando o nome social (acrescido da indicação de Nome Social) sobre o nome civil original sempre que existir nome social cadastrado no AGHU.

#### Scenario: Autopreenchimento com sucesso
- **WHEN** o usuário digitar um prontuário válido de paciente sem nome social no formulário de novas solicitações
- **THEN** o sistema consulta o backend e preenche automaticamente o campo de Nome Completo do paciente com o nome cadastrado

#### Scenario: Autopreenchimento com sucesso para paciente com nome social
- **WHEN** o usuário digitar um prontuário válido de paciente que possui nome social no AGHU no formulário de solicitações
- **THEN** o sistema consulta o backend e preenche automaticamente o campo de nome do paciente com o nome social e a indicação `(Nome Social)`

#### Scenario: Paciente não encontrado
- **WHEN** o usuário digitar um prontuário que não existe no banco de dados (AGHU ou local)
- **THEN** o sistema mantém o campo de Nome Completo limpo e exibe um alerta informando que o prontuário não foi encontrado
