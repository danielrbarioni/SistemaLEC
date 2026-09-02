## ADDED Requirements

### Requirement: Registro de Edição de Categorização de Profissional
O sistema SHALL registrar eventos de histórico na edição de categorizações de profissionais executadas no menu Perfis.
- Ação SHALL ser "Edição de Categorização" (estilizada com tag marrom claro e texto azul).
- Tipo de Evento SHALL ser "Execução".
- Descrição SHALL detalhar o profissional, especialidade e o novo estado das categorias.

#### Scenario: Edição de categorização registrada no histórico
- **WHEN** um usuário edita as categorias de um médico em uma especialidade
- **THEN** o sistema gera um registro no Histórico com origem "Perfis", ação "Edição de Categorização" (marrom claro com letra azul), tipo de evento "Execução" e detalhes das alterações.

### Requirement: Exibição e Filtragem por Especialidade em Ações Administrativas do Menu Perfis
O sistema SHALL preencher a coluna `especialidade` em todas as ações de perfis de especialidade (criação/exclusão de perfis com especialidade, criação/exclusão de usuários vinculados a especialidades e categorizações de profissionais).
- A tabela do Histórico SHALL exibir a especialidade na coluna "Especialidade / Procedimento" sem exigir que haja um procedimento cirúrgico.
- O filtro de especialidade no topo do Histórico SHALL filtrar corretamente esses registros administrativos pela especialidade informada.

#### Scenario: Filtro por especialidade inclui ações de perfis da especialidade
- **WHEN** o usuário seleciona uma especialidade no filtro de Especialidade do Histórico
- **THEN** o sistema exibe tanto as solicitações de procedimentos quanto as ações administrativas (criação de perfil, criação de usuário e categorizações) associadas àquela especialidade.
