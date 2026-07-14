# user-creation Specification

## Purpose
TBD - created by archiving change profile-user-management. Update Purpose after archive.
## Requirements
### Requirement: Controle de Acesso para Criação de Usuário
O sistema SHALL permitir a criação/vínculo de usuários locais Ebserh com base no perfil do usuário autenticado atual, aplicando as seguintes restrições:
- Usuários com perfil `ADMIN` SHALL poder criar usuários de qualquer perfil.
- Usuários com perfil `GESTÃO LEC` SHALL apenas poder criar usuários dos perfis `GESTÃO LEC` ou do tipo `Especialidade`. Se o perfil selecionado for do tipo `Especialidade`, a especialidade correspondente SHALL ser fornecida.
- Usuários com perfil do tipo `Especialidade` SHALL apenas poder criar usuários vinculados à sua própria especialidade (ex: Plástica).

#### Scenario: Admin cria qualquer perfil de usuário
- **WHEN** um usuário autenticado com perfil `ADMIN` solicita a criação de um usuário com perfil `ADMIN`, `GESTÃO LEC` ou `Especialidade`
- **THEN** o sistema SHALL processar e salvar a solicitação com sucesso.

#### Scenario: Gestão LEC tenta criar um Admin
- **WHEN** um usuário com perfil `GESTÃO LEC` tenta criar um usuário com perfil `ADMIN`
- **THEN** o sistema SHALL bloquear a operação e retornar erro de permissão negada.

#### Scenario: Especialidade tenta criar usuário de outra especialidade
- **WHEN** um usuário com perfil `Especialidade` de "Plástica" tenta criar um usuário com especialidade "Oftalmologia" ou perfil "ADMIN"
- **THEN** o sistema SHALL bloquear a operação e retornar erro de permissão negada.

### Requirement: Layout e Ordem dos Campos na Criação de Usuário
A interface de gerenciamento de perfis SHALL posicionar a seção de criação de usuários ("Criar Usuário") acima da seção de criação de perfis ("Criar Novo Perfil").
O formulário de criação de usuário SHALL apresentar os seguintes campos na ordem indicada:
1. Usuário (campo de texto para o nome de usuário Ebserh)
2. Nome completo
3. Perfil de Acesso (seleção do perfil correspondente)

#### Scenario: Visualização do formulário de Criar Usuário
- **WHEN** a tela de gerenciamento de perfis é acessada
- **THEN** o formulário "Criar Usuário" é exibido no topo da página e contém os campos ordenados por: Usuário, Nome completo e Perfil de Acesso.

