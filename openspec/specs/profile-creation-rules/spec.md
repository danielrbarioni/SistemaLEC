# profile-creation-rules Specification

## Purpose
TBD - created by archiving change profile-user-management. Update Purpose after archive.
## Requirements
### Requirement: Restrições de Acesso para Criar Perfil
O sistema SHALL restringir a criação de novos perfis apenas para usuários autenticados com os perfis `ADMIN` e `GESTÃO LEC`. Usuários com perfil do tipo `Especialidade` SHALL ser bloqueados de criar novos perfis.

#### Scenario: Usuário Especialidade tenta criar perfil
- **WHEN** um usuário com perfil `Especialidade` (ex: Plástica) tenta acessar a funcionalidade ou enviar uma requisição para criar perfil
- **THEN** o sistema SHALL bloquear a operação e retornar erro de acesso não autorizado.

### Requirement: Regras de Negócio na Criação de Perfil
O sistema SHALL permitir a criação de perfis apenas do tipo `Especialidade`. 
O formulário de criação de perfil no frontend SHALL possuir a seguinte estrutura:
1. O primeiro campo deve ser o "Tipo", preenchido automaticamente como "Especialidade Cirúrgica" e desabilitado para edição.
2. O segundo campo deve ser do tipo texto livre rotulado como "Nome da Especialidade".
3. A paleta de cores SHALL ser omitida no frontend durante a criação, e a cor de qualquer especialidade criada SHALL ser definida automaticamente como verde.
As cores dos perfis do sistema SHALL ser atribuídas da seguinte forma:
- Perfil `ADMIN` (cujo nome de exibição no sistema e no banco de dados SHALL ser 'ADMIN' em vez de 'Administrador') SHALL possuir a cor cinza.
- Perfil `GESTÃO LEC` SHALL possuir a cor azul.
- Perfil `ESPECIALIDADE` SHALL possuir a cor verde.

#### Scenario: Criação de perfil com parâmetros válidos
- **WHEN** um usuário com perfil `ADMIN` ou `GESTÃO LEC` preenche o campo de texto livre com o nome de uma especialidade (ex: "Urologia") e envia o formulário
- **THEN** o perfil do tipo `ESPECIALIDADE` correspondente à especialidade fornecida é criado com sucesso com a cor padrão definida automaticamente como verde.

