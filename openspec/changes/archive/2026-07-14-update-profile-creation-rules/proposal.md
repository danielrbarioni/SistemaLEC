## Why

Desejamos renomear o nome de exibição do perfil de 'Administrador' para 'ADMIN' na listagem e na base de dados para manter consistência, e também ajustar o formulário "Criar Novo Perfil" para que o primeiro campo seja o Tipo (preenchido como "Especialidade Cirúrgica" e desabilitado) e o segundo campo seja de texto livre ("Nome da Especialidade").

## What Changes

- **Banco de Dados (SQLite):**
  - Renomear o nome do perfil ADMIN de 'Administrador' para 'ADMIN' na tabela `perfis`.
- **Interface do Usuário (Frontend):**
  - No formulário "Criar Novo Perfil", o primeiro campo será o "Tipo" (preenchido com "Especialidade Cirúrgica" e desabilitado).
  - O segundo campo será do tipo texto livre rotulado como "Nome da Especialidade".
  - Garantir que a nota do sistema na parte inferior permaneça ocultada.
- **Backend (FastAPI):**
  - Ajustar o endpoint de criação de perfil para salvar o nome fornecido em maiúsculas (ou como enviado) e o ID amigável.

## Capabilities

### New Capabilities

### Modified Capabilities
- `profile-creation-rules`: Modificar a estrutura do formulário de criação de perfis e a nomeação do perfil de administrador padrão.

## Impact

- Afeta `Perfis.vue` no frontend (estruturação do formulário de perfil).
- Banco de dados SQLite local (tabela `perfis`, registro do ADMIN).
- Lógica de mapeamento no backend `/api/perfis`.
