## ADDED Requirements

### Requirement: Título do Menu Histórico
O título da página no menu Histórico SHALL ser exibido como "Histórico de Solicitações/Respostas".

#### Scenario: Visualização do novo título
- **WHEN** o usuário acessa o menu Histórico
- **THEN** o título da página exibido no topo é "Histórico de Solicitações/Respostas"

### Requirement: Discriminação de Solicitação ou Resposta no Histórico
A coluna "Solicitação ou Resposta" (6ª coluna) SHALL indicar claramente se o evento registrado corresponde a uma solicitação enviada ou a uma resposta efetuada.

#### Scenario: Exibição do tipo de evento (Solicitação vs. Resposta)
- **WHEN** uma linha de histórico é renderizada
- **THEN** a coluna exibe um badge identificador ("Solicitação" ou "Resposta") junto do texto de detalhe/justificativa

### Requirement: Usuário Executor no Formato Ebserh
A coluna "Perfil Executor / Usuário Executor" (8ª coluna) SHALL exibir o nome de usuário (usuário Ebserh, ex: `nome.sobrenome`) correspondente ao executor da ação.

#### Scenario: Exibição do username Ebserh do executor
- **WHEN** o usuário visualiza o executor de um registro de histórico
- **THEN** a coluna exibe o identificador do usuário Ebserh (ex: `joao.silva`)
