## MODIFIED Requirements

### Requirement: Restrições de Acesso para Criar Perfil
O sistema SHALL restringir a criação de novos perfis apenas para usuários autenticados com os perfis `ADMIN` e `GESTÃO LEC`. Usuários com perfil do tipo `Especialidade` SHALL ser bloqueados de criar novos perfis.

#### Scenario: Usuário Especialidade tenta criar perfil
- **WHEN** um usuário com perfil `Especialidade` (ex: Plástica) tenta acessar a funcionalidade ou enviar uma requisição para criar perfil
- **THEN** o sistema SHALL bloquear a operação e retornar erro de acesso não autorizado.

### Requirement: Regras de Negócio na Criação de Perfil
O sistema SHALL permitir a criação de perfis apenas do tipo `Especialidade`. A paleta de cores SHALL ser omitida no frontend durante a criação, e a cor de qualquer especialidade criada SHALL ser definida automaticamente como verde.
As cores dos perfis do sistema SHALL ser atribuídas da seguinte forma:
- Perfil `ADMIN` SHALL possuir a cor cinza.
- Perfil `GESTÃO LEC` SHALL possuir a cor azul.
- Perfil `ESPECIALIDADE` SHALL possuir a cor verde.

#### Scenario: Criação de perfil com parâmetros válidos
- **WHEN** um usuário com perfil `ADMIN` ou `GESTÃO LEC` cria um perfil do tipo `Especialidade`
- **THEN** o perfil é criado com sucesso com a cor padrão definida automaticamente como verde.
