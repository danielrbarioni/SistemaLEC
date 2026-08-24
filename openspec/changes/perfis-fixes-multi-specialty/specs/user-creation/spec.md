## MODIFIED Requirements

### Requirement: Controle de Acesso para Criação de Usuário
O sistema SHALL permitir a criação/vínculo de usuários locais Ebserh com base no perfil do usuário autenticado atual, aplicando as seguintes restrições:
- Usuários com perfil `ADMIN` SHALL poder criar usuários de qualquer perfil.
- Usuários com perfil `GESTÃO LEC` SHALL apenas poder criar usuários dos perfis `GESTÃO LEC` ou do tipo `Especialidade`. Se o perfil selecionado for do tipo `Especialidade`, a especialidade correspondente SHALL ser fornecida.
- Usuários com perfil do tipo `Especialidade` SHALL apenas poder criar usuários vinculados à sua própria especialidade (ex: Plástica).
- O sistema SHALL permitir que o mesmo `username` seja vinculado a mais de um perfil diferente, impedindo apenas a duplicidade do par exato `(username, perfil_id)`.

#### Scenario: Admin cria qualquer perfil de usuário
- **WHEN** um usuário autenticado com perfil `ADMIN` solicita a criação de um usuário com perfil `ADMIN`, `GESTÃO LEC` ou `Especialidade`
- **THEN** o sistema SHALL processar e salvar a solicitação com sucesso.

#### Scenario: Gestão LEC tenta criar um Admin
- **WHEN** um usuário com perfil `GESTÃO LEC` tenta criar um usuário com perfil `ADMIN`
- **THEN** o sistema SHALL bloquear a operação e retornar erro de permissão negada.

#### Scenario: Especialidade tenta criar usuário de outra especialidade
- **WHEN** um usuário com perfil `Especialidade` de "Plástica" tenta criar um usuário com especialidade "Oftalmologia" ou perfil "ADMIN"
- **THEN** o sistema SHALL bloquear a operação e retornar erro de permissão negada.

#### Scenario: Criação de múltiplos perfis para o mesmo usuário Ebserh
- **WHEN** um usuário com permissão cadastra um mesmo `username` em especialidades distintas
- **THEN** o sistema SHALL salvar ambos os vínculos com sucesso.
