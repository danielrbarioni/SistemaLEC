## Context

Precisamos atualizar a tela de gerenciamento de perfis (`Perfis.vue`) para permitir que o usuário digite o nome de uma especialidade livremente por meio de um campo de texto, mantendo o campo "Tipo" automaticamente preenchido como "Especialidade Cirúrgica" e desabilitado. Também é necessário alterar o nome de exibição do perfil de administrador no banco de dados e no mapeamento de labels de 'Administrador' para 'ADMIN'.

## Goals / Non-Goals

**Goals:**
- Ajustar os inputs no formulário "Criar Novo Perfil" em `Perfis.vue`:
  - Campo "Tipo" preenchido fixo com "Especialidade Cirúrgica" e desabilitado.
  - Campo "Especialidade Correspondente" alterado de dropdown `<select>` para caixa de texto livre `<input type="text">` rotulado como "Nome da Especialidade".
- Alterar o nome de exibição do perfil de Administrador no banco de dados SQLite para 'ADMIN' e atualizar os mapeamentos de label no frontend.

## Decisions

1. **Alteração do formulário de Perfil no Frontend (`Perfis.vue`):**
   Substituir a caixa de seleção `<select>` por um `<input type="text">` para o campo `perfilForm.especialidade`. O campo Nome do Perfil passará a ser gerado automaticamente se o usuário não preencher, ou podemos continuar salvando o nome da especialidade formatado.
   Wait, let's see how `criarPerfil` currently gets the name:
   `perfilForm.value.nome` is still used in the frontend. But the user said:
   "o primeiro campo é Tipo, e já deve estar automaticamente preenchido 'Especialidade Cirúrgica'; o campo de baixo deve pedir 'Nome da Especialidade', e o usuário deve digitar o nome (sem lista)"
   This means the form only has two fields:
   1. Tipo (disabled, prefilled with "Especialidade Cirúrgica")
   2. Nome da Especialidade (text input)
   So we should remove the "Nome do Perfil" field from the profile creation form, and let the backend or frontend automatically derive it from the specialty name!
   For example, if the user types "Plástica", the profile name will be "ESPECIALIDADE PLÁSTICA".
   Let's check `criarPerfil` in `Perfis.vue`:
   ```typescript
   await perfisStore.adicionarPerfil(
     perfilForm.value.nome,
     perfilForm.value.especialidade
   );
   ```
   If we generate `perfilForm.value.nome` automatically:
   `const nomePerfil = 'ESPECIALIDADE ' + perfilForm.value.especialidade.toUpperCase();`
   Then we can pass that `nomePerfil` to `adicionarPerfil`. This is extremely clean and matches exactly "o primeiro campo é Tipo... o campo de baixo deve pedir 'Nome da Especialidade' (sem lista)"!

2. **Renomeação do Perfil 'Administrador' para 'ADMIN':**
   - Alterar no banco de dados SQLite (via seed ou migração direta) o campo `nome` do perfil `'ADMIN'` para `'ADMIN'`.
   - No frontend `Perfis.vue`, atualizar a função `getTipoLabel` ou qualquer label correspondente.

## Risks / Trade-offs

- N/A
