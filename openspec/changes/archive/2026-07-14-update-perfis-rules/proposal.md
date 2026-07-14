## Why

Precisamos reestruturar o layout e as regras do módulo de Perfis para melhorar a usabilidade e alinhar com a governança real do Sistema LEC. As mudanças incluem reordenar as seções, ajustar o mapeamento visual de cores por perfil, reorganizar o formulário de cadastro de usuários (que agora passa a ser rotulado como "Criar Usuário" mantendo a vinculação AD/Ebserh sem campo de senha), e refinar as permissões de criação de usuários e perfis para cada nível de acesso.

## What Changes

- **Interface do Usuário (Frontend):**
  - Reordenar a tela `Perfis.vue` para exibir a seção "Criar Usuário" acima de "Criar Novo Perfil".
  - Alterar a paleta de cores dos perfis para: ADMIN como cinza, GESTÃO LEC como azul, e ESPECIALIDADE como verde.
  - Remover a nota do sistema sobre a restrição de cor verde fixa na criação de perfis.
  - No formulário de cadastro de usuário, alterar o título de "Vincular Usuário AD" para "Criar Usuário", ordenando os campos em: 1. Usuário (usuário Ebserh), 2. Nome completo, 3. Perfil de Acesso.
- **Regras de Negócio e Permissões (Backend & Frontend):**
  - Perfil `ADMIN`: pode criar usuários para qualquer perfil de acesso e pode criar perfis para novas especialidades.
  - Perfil `GESTÃO LEC`: pode criar usuários para os perfis `GESTAO_LEC` e `ESPECIALIDADE` (sendo obrigatório informar a especialidade no cadastro do usuário se for do tipo especialidade); pode criar perfis para novas especialidades.
  - Perfil `ESPECIALIDADE`: pode criar usuários apenas para sua própria especialidade (ex: Plástica) e não tem permissão para criar perfis.

## Capabilities

### New Capabilities

### Modified Capabilities
- `profile-creation-rules`: Ajustar permissões de criação de perfil para permitir que ADMIN e GESTÃO LEC criem especialidades, e impedir ESPECIALIDADE de criar.
- `user-creation`: Ajustar permissões hierárquicas, ordem dos campos, layout e títulos na criação/vínculo de usuários locais Ebserh.

## Impact

- Tela do frontend `Perfis.vue` (HTML, inputs, layout, classes de cores).
- Roteadores e controllers de Usuários e Perfis no backend FastAPI (regras de validação hierárquica e validações de input).
