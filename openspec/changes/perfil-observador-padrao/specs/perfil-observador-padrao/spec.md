## ADDED Requirements

### Requirement: Atribuição Automática do Perfil OBSERVADOR
O sistema backend MUST atribuir o perfil `OBSERVADOR` durante a autenticação/emissão de token JWT para qualquer usuário autenticado via Active Directory que não possua um perfil pré-cadastrado na tabela de usuários.

#### Scenario: Login de usuário sem perfil cadastrado
- **WHEN** um usuário Ebserh sem perfil registrado realiza login com credenciais válidas do AD
- **THEN** o sistema gera um token JWT com `perfil` igual a `"OBSERVADOR"` e concede acesso em modo leitura ao sistema.

#### Scenario: Login de usuário com perfil cadastrado
- **WHEN** um usuário com perfil `ADMIN`, `GESTÃO LEC` ou `ESPECIALIDADE` cadastrado realiza login com credenciais válidas do AD
- **THEN** o sistema gera um token JWT mantendo o perfil correspondente cadastrado na tabela de usuários.

### Requirement: Restrição de Operações Mutativas para OBSERVADOR
O sistema backend MUST rejeitar qualquer tentativa de criação, alteração, aprovação, rejeição ou exclusão realizada por um usuário com perfil `OBSERVADOR`, retornando erro HTTP 403 Forbidden.

#### Scenario: Tentativa de criação/edição por perfil OBSERVADOR
- **WHEN** um usuário com perfil `OBSERVADOR` tenta enviar uma requisição mutativa (POST, PUT, DELETE) para os endpoints do sistema
- **THEN** o backend bloqueia a ação e retorna HTTP 403 Forbidden com mensagem explicativa.

#### Scenario: Visualização de dados por perfil OBSERVADOR
- **WHEN** um usuário com perfil `OBSERVADOR` acessa rotas de consulta de dados (GET)
- **THEN** o backend responde normalmente com a lista de solicitações, pacientes e relatórios disponíveis.

### Requirement: Interface em Modo Leitura para OBSERVADOR
O frontend Vue MUST identificar o perfil `OBSERVADOR` no estado de autenticação e desabilitar ou ocultar todos os controles de ação de escrita/alteração de dados.

#### Scenario: Exibição de telas para perfil OBSERVADOR
- **WHEN** um usuário com perfil `OBSERVADOR` navega pelas telas do Sistema LEC
- **THEN** o sistema exibe os dados normalmente, porém oculta ou desabilita botões como "Nova Solicitação", "Aprovar", "Rejeitar", "Editar" e "Excluir".
