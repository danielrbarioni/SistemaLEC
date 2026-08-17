## MODIFIED Requirements

### Requirement: Montagem da lista de procedimentos por paciente sem duplicatas decorrentes da resposta
Ao processar solicitações aprovadas para reconstruir a lista de procedimentos de um paciente no menu Pacientes e no controller backend, o sistema DEVE desconsiderar registros de resposta que possuem `evento_tipo = "RESPOSTA"`, evitando que a inclusão ou alteração de um procedimento aprovado seja contabilizada duas vezes (na solicitação original e na resposta).

#### Scenario: Visualização de procedimento aprovado no menu Pacientes
- **WHEN** uma solicitação de inclusão de procedimento é aprovada pela Gestão LEC (gerando um registro de resposta em solicitações)
- **THEN** a lista de procedimentos do paciente no menu Pacientes exibe apenas 1 ocorrência do procedimento incluído
- **THEN** o menu Histórico continua exibindo ambas as linhas (a solicitação original e a resposta de aprovação)
