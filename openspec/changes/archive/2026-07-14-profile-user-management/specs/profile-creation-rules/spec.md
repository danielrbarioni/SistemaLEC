## ADDED Requirements

### Requirement: Restrições de Acesso para Criar Perfil
O sistema SHALL restringir a criação de novos perfis apenas para usuários autenticados com os perfis `ADMIN` e `GESTÃO LEC`. Usuários com perfil do tipo `Especialidade` SHALL ser bloqueados.

#### Scenario: Usuário Especialidade tenta criar perfil
- **WHEN** um usuário com perfil `Especialidade` (ex: Plástica) tenta acessar a funcionalidade ou enviar uma requisição para criar perfil
- **THEN** o sistema SHALL bloquear a operação e retornar erro de acesso não autorizado.

### Requirement: Regras de Negócio na Criação de Perfil
O sistema SHALL permitir apenas a criação de perfis do tipo `Especialidade`. A paleta de cores SHALL ser omitida no frontend, e a cor do novo perfil criado SHALL ser definida automaticamente como verde.

#### Scenario: Criação de perfil com parâmetros válidos
- **WHEN** um usuário com perfil `ADMIN` cria um perfil do tipo `Especialidade`
- **THEN** o perfil é criado com sucesso com a cor padrão definida automaticamente como verde, sem que o usuário precise selecionar a cor.
