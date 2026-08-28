## ADDED Requirements

### Requirement: Validação de Existência do Paciente no AGHU para Inclusão
O sistema SHALL validar a existência do paciente no AGHU (Cadastro de Pacientes) antes de permitir a submissão de uma solicitação de inclusão de procedimento cirúrgico.

#### Scenario: Submissão de inclusão para prontuário inexistente no AGHU bloqueada no frontend
- **WHEN** o usuário tentar submeter o formulário de inclusão com um prontuário que não foi validado no AGHU
- **THEN** o sistema SHALL impedir o envio da solicitação e exibir uma mensagem de erro orientando o usuário a buscar e localizar um prontuário válido no AGHU

#### Scenario: Submissão de inclusão para prontuário inexistente rejeitada pelo backend
- **WHEN** uma requisição POST de inclusão (`tipo = INSERIR`) for enviada com prontuário inexistente ou nome de paciente fictício/em branco
- **THEN** o backend SHALL rejeitar a solicitação com status HTTP 400 Bad Request informando que o paciente não foi encontrado no AGHU (Cadastro de Pacientes)

#### Scenario: Invalidação de dados ao alterar número do prontuário
- **WHEN** o usuário modificar o número do prontuário no campo de formulário após uma busca anterior
- **THEN** o sistema SHALL invalidar a validação anterior e limpar os campos de dados do paciente (nome, data de nascimento, nome da mãe)
