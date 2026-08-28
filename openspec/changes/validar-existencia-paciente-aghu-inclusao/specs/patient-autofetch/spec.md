## MODIFIED Requirements

### Requirement: Busca automática de dados do paciente
O sistema SHALL retornar o nome completo e dados cadastrais do paciente a partir do banco de dados quando o usuário consultar um prontuário válido, e retornar erro HTTP 404 sem dados fictícios caso o prontuário não exista.

#### Scenario: Autopreenchimento com sucesso
- **WHEN** o usuário consultar um prontuário válido no formulário de novas solicitações
- **THEN** o sistema preenche automaticamente os campos de identificação do paciente (Nome Completo, Data de Nascimento, Nome da Mãe) a partir dos dados retornados da API

#### Scenario: Paciente não encontrado
- **WHEN** o usuário consultar um prontuário que não existe no banco de dados (AGHU ou local)
- **THEN** o endpoint de consulta retorna status HTTP 404 Not Found, o sistema mantém os campos de identificação limpos e exibe um alerta informando que o paciente não foi encontrado no AGHU (Cadastro de Pacientes)
