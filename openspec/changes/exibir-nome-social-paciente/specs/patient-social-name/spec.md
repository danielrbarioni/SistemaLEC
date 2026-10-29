# Spec Delta

## Purpose

Garante que o Nome Social do paciente cadastrado no AGHU seja priorizado e exibido em substituição ao nome civil original em todos os módulos, formulários, tabelas, modais e exportações do sistema Comunicação Cirúrgica, com indicação explícita de que se trata de Nome Social.

## ADDED Requirements

### Requirement: Priorização do Nome Social nas consultas de pacientes do AGHU
O sistema SHALL consultar o campo de nome social do paciente no banco de dados do AGHU e, quando preenchido e não vazio, utilizá-lo como nome principal do paciente acompanhado da indicação `(Nome Social)`, omitindo o nome civil original.

#### Scenario: Paciente com nome social cadastrado no AGHU
- **WHEN** o sistema consultar um prontuário no AGHU que possua nome social cadastrado e não vazio
- **THEN** o sistema SHALL retornar o nome do paciente no formato `<NOME SOCIAL> (Nome Social)` e o indicador `possui_nome_social: true`, em vez do nome civil original

#### Scenario: Paciente sem nome social cadastrado no AGHU
- **WHEN** o sistema consultar um prontuário no AGHU cujo campo de nome social seja nulo ou vazio
- **THEN** o sistema SHALL retornar o nome civil cadastrado originalmente sem a indicação de nome social

### Requirement: Exibição e indicação de Nome Social no menu Solicitações LEC
O sistema SHALL exibir o nome social (com indicação de que se trata do nome social) em todos os campos de nome do paciente no menu Solicitações LEC, incluindo o formulário de inclusão/edição/standby/exclusão, a tabela de acompanhamento e os modais de detalhes, rejeição e cancelamento.

#### Scenario: Busca de prontuário com nome social em Solicitar Inclusão
- **WHEN** o usuário digitar um prontuário de paciente que possui nome social no AGHU e acionar a busca na aba Solicitar Inclusão (ou Editar, Standby, Excluir)
- **THEN** o campo de nome do paciente SHALL ser preenchido com o nome social acompanhado da indicação `(Nome Social)` e exibir um selo visual indicando tratar-se de Nome Social

#### Scenario: Visualização na tabela de acompanhamento e modais de Solicitações LEC
- **WHEN** uma solicitação pertencer a um paciente que possui nome social no AGHU
- **THEN** a tabela de acompanhamento e os modais de detalhes, rejeição e cancelamento SHALL apresentar o nome social com a indicação de Nome Social em vez do nome original

### Requirement: Exibição e indicação de Nome Social nos menus Pacientes e Histórico
O sistema SHALL exibir o nome social (com indicação de que se trata do nome social) para todos os pacientes que o possuírem no AGHU tanto no menu Pacientes quanto no menu Histórico (incluindo modais de detalhes e exportação Excel).

#### Scenario: Listagem e modal de detalhes no menu Pacientes
- **WHEN** o usuário visualizar a tabela de pacientes ou abrir o modal de detalhes de um paciente que possui nome social no AGHU
- **THEN** o sistema SHALL exibir o nome social com a indicação `(Nome Social)` em substituição ao nome original

#### Scenario: Listagem, modal de detalhes e exportação no menu Histórico
- **WHEN** o usuário consultar o menu Histórico, abrir o modal de detalhes de uma ação ou exportar o relatório para Excel
- **THEN** todos os registros referentes a pacientes com nome social no AGHU SHALL apresentar o nome social com a indicação `(Nome Social)`

