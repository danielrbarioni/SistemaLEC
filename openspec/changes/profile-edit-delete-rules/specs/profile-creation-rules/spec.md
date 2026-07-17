## ADDED Requirements

### Requirement: Restrições de Acesso para Editar Perfil
O sistema SHALL restringir as permissões de edição de perfis com base no perfil do usuário autenticado:
- Usuários com perfil `ADMIN` SHALL poder editar perfis do tipo `ADMIN`, `GESTAO_LEC` e `ESPECIALIDADE`.
- Usuários com perfil `GESTÃO LEC` SHALL apenas poder editar perfis do tipo `ESPECIALIDADE`.
- Usuários com perfil do tipo `ESPECIALIDADE` SHALL ser bloqueados de editar qualquer perfil.

#### Scenario: Admin edita qualquer perfil
- **WHEN** um usuário autenticado com perfil `ADMIN` envia uma requisição para editar um perfil do tipo `ADMIN`, `GESTAO_LEC` ou `ESPECIALIDADE`
- **THEN** o sistema SHALL autorizar e salvar as alterações.

#### Scenario: Gestão LEC edita perfil especialidade
- **WHEN** um usuário autenticado com perfil `GESTÃO LEC` tenta editar um perfil do tipo `ESPECIALIDADE`
- **THEN** o sistema SHALL autorizar e salvar as alterações.

#### Scenario: Gestão LEC tenta editar perfil admin ou gestão lec
- **WHEN** um usuário autenticado com perfil `GESTÃO LEC` tenta editar um perfil do tipo `ADMIN` ou `GESTAO_LEC`
- **THEN** o sistema SHALL bloquear a operação e retornar erro de acesso negado.

#### Scenario: Especialidade tenta editar qualquer perfil
- **WHEN** um usuário autenticado com perfil do tipo `ESPECIALIDADE` tenta editar qualquer perfil
- **THEN** o sistema SHALL bloquear a operação e retornar erro de acesso negado.

### Requirement: Restrições de Acesso para Excluir Perfil
O sistema SHALL restringir as permissões de exclusão de perfis com base no perfil do usuário autenticado:
- Usuários com perfil `ADMIN` SHALL poder excluir perfis do tipo `ADMIN`, `GESTAO_LEC` e `ESPECIALIDADE`.
- Usuários com perfil `GESTÃO LEC` SHALL apenas poder excluir perfis do tipo `ESPECIALIDADE`.
- Usuários com perfil do tipo `ESPECIALIDADE` SHALL ser bloqueados de excluir qualquer perfil.

#### Scenario: Admin exclui qualquer perfil
- **WHEN** um usuário autenticado com perfil `ADMIN` solicita a exclusão de um perfil do tipo `ADMIN`, `GESTAO_LEC` ou `ESPECIALIDADE`
- **THEN** o sistema SHALL autorizar e realizar a exclusão.

#### Scenario: Gestão LEC exclui perfil especialidade
- **WHEN** um usuário autenticado com perfil `GESTÃO LEC` tenta excluir um perfil do tipo `ESPECIALIDADE`
- **THEN** o sistema SHALL autorizar e realizar a exclusão.

#### Scenario: Gestão LEC tenta excluir perfil admin
- **WHEN** um usuário autenticado com perfil `GESTÃO LEC` tenta excluir um perfil do tipo `ADMIN` ou `GESTAO_LEC`
- **THEN** o sistema SHALL bloquear a operação e retornar erro de acesso negado.

#### Scenario: Especialidade tenta excluir qualquer perfil
- **WHEN** um usuário autenticado com perfil do tipo `ESPECIALIDADE` tenta excluir qualquer perfil
- **THEN** o sistema SHALL bloquear a operação e retornar erro de acesso negado.
