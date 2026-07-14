## ADDED Requirements

### Requirement: Controle de Acesso para Criação de Usuário
O sistema SHALL permitir a criação de novos usuários com base no perfil do usuário autenticado atual, aplicando as seguintes restrições:
- Usuários com perfil `ADMIN` SHALL poder criar usuários de qualquer perfil.
- Usuários com perfil `GESTÃO LEC` SHALL apenas poder criar usuários dos perfis `GESTÃO LEC` ou do tipo `Especialidade`.
- Usuários com perfil do tipo `Especialidade` SHALL apenas poder criar usuários da sua própria especialidade (ex: Plástica).

#### Scenario: Admin cria qualquer perfil de usuário
- **WHEN** um usuário autenticado com perfil `ADMIN` solicita a criação de um usuário com perfil `ADMIN`, `GESTÃO LEC` ou `Especialidade`
- **THEN** o sistema SHALL processar e salvar a solicitação com sucesso.

#### Scenario: Gestão LEC tenta criar um Admin
- **WHEN** um usuário com perfil `GESTÃO LEC` tenta criar um usuário com perfil `ADMIN`
- **THEN** o sistema SHALL bloquear a operação e retornar erro de permissão negada.

#### Scenario: Especialidade tenta criar usuário de outra especialidade
- **WHEN** um usuário com perfil `Especialidade` de "Plástica" tenta criar um usuário com especialidade "Oftalmologia" ou perfil "ADMIN"
- **THEN** o sistema SHALL bloquear a operação e retornar erro de permissão negada.
