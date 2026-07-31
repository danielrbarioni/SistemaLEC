## Why

Usuários Ebserh autenticados via Active Directory que ainda não foram cadastrados em um perfil específico (ADMIN, GESTÃO LEC ou ESPECIALIDADE) estão recebendo acesso ilimitado de ADMIN ao fazer login. Isso representa um risco de segurança e permissões inadequadas. O objetivo desta mudança é garantir que usuários sem perfil atribuído recebam automaticamente o perfil padrão **OBSERVADOR**, permitindo a visualização dos dados e módulos do sistema sem concessão de permissões para criar, editar, aprovar, rejeitar ou excluir registros.

## What Changes

- **Perfil Padrão de Autenticação (Fallback):** Alteração da atribuição padrão durante o login/criação de sessão JWT. Se o usuário Ebserh não possuir perfil pré-cadastrado na tabela de usuários, será atribuído o perfil `OBSERVADOR`.
- **Acesso Somente Leitura (Observador):** O perfil `OBSERVADOR` terá permissão exclusivamente de leitura (GET) nas rotas do sistema. Ações mutativas (POST, PUT, DELETE, aprovação/rejeição de solicitações) serão bloqueadas com status 403 Forbidden para o perfil `OBSERVADOR`.
- **Interface do Usuario (Frontend):** O frontend Vue identificará o perfil `OBSERVADOR` e ocultará/desabilitará botões de ação (ex: "Nova Solicitação", "Aprovar", "Rejeitar", "Editar", "Excluir") nas telas do sistema.

## Capabilities

### New Capabilities
- `perfil-observador-padrao`: Define a atribuição automática do perfil OBSERVADOR como fallback de login e restringe suas permissões no backend e frontend a ações somente leitura.

### Modified Capabilities

## Impact

- `src/auth/auth.py`: Ajuste na lógica de autenticação e atribuição do perfil token JWT na ausência de registro explícito no banco.
- `src/controllers/` e `src/routers/`: Validação de permissões em rotas mutativas para negar acesso ao perfil OBSERVADOR.
- `frontend/src/`: Atualização da navegação, lojas Pinia (`perfis.ts`, `auth.ts`) e componentes Vue para tratar o perfil OBSERVADOR exibindo dados apenas em modo leitura.
