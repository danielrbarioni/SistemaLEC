## ADDED Requirements

### Requirement: Validação estrita do Médico Responsável por Especialidade
O Sistema LEC DEVE validar que o Médico Responsável inserido ou alterado no formulário do Sistema LEC (Interações LEC) pertence à lista de médicos cadastrados que possuem perfil ativo na respectiva especialidade selecionada.

#### Scenario: Médico válido cadastrado na especialidade
- **WHEN** o usuário seleciona um médico cadastrado pertencente à especialidade da solicitação
- **THEN** a solicitação é gravada com sucesso

#### Scenario: Médico inválido ou não cadastrado na especialidade
- **WHEN** o usuário tenta registrar ou alterar uma solicitação informando um nome de médico não cadastrado ou de outra especialidade
- **THEN** o sistema bloqueia o envio e exibe mensagem de erro informando que o Médico Responsável deve ser um médico cadastrado na especialidade selecionada
