## ADDED Requirements

### Requirement: Exibição exata do usuário Ebserh no Histórico
O Sistema LEC DEVE exibir no menu Histórico a identificação exata do usuário Ebserh (nome completo ou username cadastrado) que realizou a ação na coluna "Usuário Executor", mantendo-a distinta da coluna "Perfil Executor".

#### Scenario: Usuário executa ação e visualiza no histórico
- **WHEN** um usuário realiza a inclusão, alteração, exclusão ou troca de status de uma solicitação
- **THEN** o histórico registra o nome ou username Ebserh do usuário no campo `usuario` e exibe esse nome na coluna "Usuário Executor"
