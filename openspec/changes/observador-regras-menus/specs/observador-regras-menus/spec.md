## ADDED Requirements

### Requirement: Exibição Específica do Menu Comunicação LEC para OBSERVADOR
O sistema frontend MUST ocultar o formulário de cadastro de novas solicitações no menu Comunicação LEC quando o perfil ativo for `OBSERVADOR`, exibindo unicamente o painel de Acompanhamento das Solicitações.

#### Scenario: Visualização do menu Comunicação LEC por OBSERVADOR
- **WHEN** um usuário com o perfil `OBSERVADOR` ativo acessa o menu Comunicação LEC
- **THEN** o sistema não exibe o formulário superior de envio e exibe diretamente a seção "Acompanhamento das Solicitações" com filtros funcionais e sem botões de aprovação/rejeição.

### Requirement: Exibição Específica do Menu Navegação LEC para OBSERVADOR
O sistema frontend MUST permitir a consulta e navegação por especialidades e uso de filtros no menu Navegação LEC, mas ocultar/desabilitar ações de solicitação de APA.

#### Scenario: Visualização do menu Navegação LEC por OBSERVADOR
- **WHEN** um usuário com o perfil `OBSERVADOR` ativo acessa o menu Navegação LEC
- **THEN** o sistema permite selecionar especialidades e aplicar filtros, mas oculta o botão de solicitar APA.

### Requirement: Exibição Específica do Menu Perfis para OBSERVADOR
O sistema frontend MUST exibir a lista de perfis e a tabela de usuários cadastrados no menu Perfis, mas ocultar formulários e botões de adição/edição de usuários para o perfil `OBSERVADOR`.

#### Scenario: Visualização do menu Perfis por OBSERVADOR
- **WHEN** um usuário com o perfil `OBSERVADOR` ativo acessa o menu Perfis
- **THEN** o sistema exibe os perfis e os usuários cadastrados em modo leitura, ocultando botões de adição e formulários de edição.

### Requirement: Exibição de Consulta nos Menus Pacientes e Histórico para OBSERVADOR
O sistema frontend MUST exibir os dados e permitir o uso normal de filtros nos menus Pacientes e Histórico para o perfil `OBSERVADOR`.

#### Scenario: Visualização dos menus Pacientes e Histórico por OBSERVADOR
- **WHEN** um usuário com o perfil `OBSERVADOR` ativo acessa os menus Pacientes ou Histórico
- **THEN** o sistema renderiza as tabelas de dados e possibilita a utilização de todos os filtros de pesquisa normalmente.
