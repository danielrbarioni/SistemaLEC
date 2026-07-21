## ADDED Requirements

### Requirement: Coluna de Origem/Menu no Histórico
O Sistema LEC DEVE incluir no menu Histórico uma coluna intitulada "Origem / Menu" posicionada logo no início da tabela, imediatamente após a coluna "Data / Hora", indicando o módulo/menu de onde partiu a solicitação ou ação (ex: "Sistema LEC", "Navegação").

#### Scenario: Visualização da coluna Origem / Menu
- **WHEN** o usuário acessa a tela de Histórico
- **THEN** a tabela exibe a coluna "Origem / Menu" entre "Data / Hora" e "Prontuário / Paciente" informando o menu de origem de cada registro

### Requirement: Exibição de Respostas de Ações no Histórico
O Sistema LEC DEVE registrar e exibir no Histórico as ações de resposta (aprovação, rejeição, cancelamento) efetuadas por gestores ou administradores, detalhando quem respondeu, qual perfil utilizou e em qual menu a resposta ocorreu.

#### Scenario: Resposta a solicitação registrada no histórico
- **WHEN** um usuário com perfil ADMIN ou GESTÃO LEC aprova ou rejeita uma solicitação
- **THEN** o sistema gera/exibe a ação de resposta no histórico contendo o usuário executor da resposta, seu perfil e a origem da ação
