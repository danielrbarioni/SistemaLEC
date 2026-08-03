# Proposal: Default OBSERVADOR Profile on Login for Unregistered Users

## Why
Atualmente, quando um usuário não cadastrado na tabela `usuarios` faz login na aplicação, a autenticação backend define corretamente o `perfil_tipo` como `OBSERVADOR`. No entanto, na camada de frontend (especialmente no `usePerfisStore`), se o usuário não possuir um cadastro específico ou se o `localStorage` contiver um `perfilAtivoId` anterior (como `ADMIN`), o sistema recai para `data[0]` da lista de perfis ordenados (que é o perfil `ADMIN`), ou mantém o perfil antigo do `localStorage`. Isso permite que usuários sem perfil cadastrado entrem acidentalmente com o perfil `ADMIN` ativo na interface.

## What
Garantir de forma estrita que qualquer usuário não cadastrado em um perfil específico (ou com perfil `OBSERVADOR`) receba e mantenha o perfil `OBSERVADOR` como perfil ativo no login, limpando ou sobrescrevendo o `perfilAtivoId` do `localStorage`, além de bloquear a alternância manual para perfis privilegiados no frontend e reforçar a validação de permissões no backend.

- **Backend (`src/auth/auth.py`, `src/routers/perfil.py`)**: Garantir que o perfil `OBSERVADOR` esteja sempre presente na lista de perfis retornada por `/api/perfis` e que o token/resposta do usuário declare `OBSERVADOR` quando o usuário não estiver cadastrado.
- **Frontend (`frontend/src/stores/perfis.ts`, `frontend/src/stores/auth.ts`)**:
  - No login e no carregamento da aplicação (`fetchPerfis`), se o usuário logado for `OBSERVADOR` ou não possuir cadastro em `usuarios`, definir o `perfilAtivoId` obrigatoriamente como `OBSERVADOR` (ou o ID do perfil observador).
  - Limpar ou sincronizar o `perfilAtivoId` no `localStorage` durante o `login` e `logout`.
  - Impedir que usuários não-ADMIN vejam ou alternem para o perfil ADMIN no seletor de perfis.

## Impact
- **Backend**: `src/auth/auth.py`, `src/routers/perfil.py`
- **Frontend**: `frontend/src/stores/perfis.ts`, `frontend/src/stores/auth.ts`, `frontend/src/views/Perfis.vue`, `frontend/src/components/Header.vue` (ou navbar)
