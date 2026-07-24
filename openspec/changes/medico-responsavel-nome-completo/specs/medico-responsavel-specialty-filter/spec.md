## MODIFIED Requirements

### Requirement: Exibição e Seleção do Médico Responsável em Nome Completo
O sistema SHALL exibir e utilizar o nome completo do médico responsável em todas as listagens, cartões, formulários de edição e filtros do menu Pacientes e do menu Comunicação LEC, convertendo logins Ebserh legados para o nome completo correspondente.

#### Scenario: Visualização do médico responsável no menu Pacientes e Comunicação LEC
- **WHEN** o usuário visualiza um paciente ou solicitação cujo médico responsável no banco de dados esteja registrado pelo login Ebserh
- **THEN** o sistema exibe o nome completo do médico nas telas e cartões.

#### Scenario: Edição de médico responsável sem falsa alteração
- **WHEN** o usuário abre a aba de Solicitar Edição para um paciente cujo médico cadastrado é o login Ebserh e seleciona o nome completo do mesmo médico
- **THEN** o sistema reconhece que se trata da mesma pessoa e não marca o campo médico responsável como alterado indevidamente.
