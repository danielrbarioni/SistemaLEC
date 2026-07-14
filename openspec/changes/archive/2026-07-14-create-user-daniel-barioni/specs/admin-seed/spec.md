## ADDED Requirements

### Requirement: Cadastro de Administrador Daniel Barioni
O sistema SHALL possuir o usuário `daniel.barioni` cadastrado com perfil `ADMIN` no banco de dados SQLite local.

#### Scenario: Usuário daniel.barioni existe e possui privilégios de ADMIN
- **WHEN** o banco de dados local SQLite é consultado pelo username `daniel.barioni`
- **THEN** o sistema SHALL retornar o registro correspondente com o nome `Daniel Barioni` e perfil vinculado `ADMIN`.
