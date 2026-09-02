## ADDED Requirements

### Requirement: Correção da Origem de Menu para Solicitações LEC
O sistema SHALL exibir "Solicitações LEC" como origem e identificador de menu para todas as solicitações, edições, standbys e exclusões geradas a partir do menu Solicitações LEC (`InteracoesLec.vue`), substituindo a denominação anterior "Sistema LEC".

#### Scenario: Visualização e filtragem por origem Solicitações LEC
- **WHEN** o usuário acessa o menu Histórico ou filtra pelo campo "Origem / Menu"
- **THEN** a opção exibida é "Solicitações LEC" e os registros gerados nesse menu aparecem com a tag de origem "Solicitações LEC".

### Requirement: Padronização das nomenclaturas das ações de procedimentos no Histórico
O sistema SHALL exibir as ações do menu Solicitações LEC com nomes completos e descritivos mantendo o esquema de cores original:
- "Inclusão de Procedimento" (verde) para solicitações e ações do tipo `INSERIR`.
- "Edição de Procedimento" (azul) para solicitações e ações do tipo `EDITAR`.
- "Standby de Procedimento" (amarelo) para solicitações e ações do tipo `STANDBY`.
- "Exclusão de Procedimento" (vermelho) para solicitações e ações do tipo `EXCLUIR`.

#### Scenario: Visualização dos tipos de ação de procedimentos
- **WHEN** o usuário visualiza a coluna "Ação" no Histórico para eventos do menu Solicitações LEC
- **THEN** as ações aparecem identificadas como "Inclusão de Procedimento", "Edição de Procedimento", "Standby de Procedimento" ou "Exclusão de Procedimento" com suas respectivas cores mantidas.
