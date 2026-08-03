# Design: Default OBSERVADOR Profile on Login for Unregistered Users

## Architecture Overview

O problema de atribuição do perfil `ADMIN` para usuários não cadastrados ocorre devido a uma combinação de fatores no frontend e no fallback de estado do `usePerfisStore`:

1. Quando a lista de perfis é obtida via `/api/perfis`, ela é ordenada (`sortPerfis`) colocando `ADMIN` no topo (`data[0]`).
2. Se o usuário não for encontrado na tabela `usuarios`, o código do frontend tenta buscar `meUser`, que retorna indefinido.
3. Como `meUser` não existe e `authStore.isAdmin` pode ser avaliado incorretamente antes do `fetchUser` completar, o código recai para `setPerfilAtivoInternal(data[0].id)`, atribuindo `ADMIN` como perfil ativo.
4. Além disso, se o navegador mantiver o valor `'ADMIN'` no `localStorage.getItem('perfilAtivoId')`, esse valor prevalece.

## Technical Changes

### 1. `frontend/src/stores/perfis.ts`
- Alterar o fallback de `fetchPerfis`:
  - Se o usuário autenticado possuir `perfil_tipo === 'OBSERVADOR'` ou se `authStore.isObservador` for verdadeiro, forçar `setPerfilAtivoInternal('OBSERVADOR')`.
  - Ao verificar a tabela de usuários (`/api/usuarios`), caso o usuário autenticado não seja encontrado como usuário cadastrado com perfil próprio e não seja `ADMIN` legítimo do backend, forçar `setPerfilAtivoInternal('OBSERVADOR')`.
  - O fallback padrão em caso de ausência de perfil ativo ou perfil inválido passa a ser `'OBSERVADOR'`, nunca `data[0]` (ADMIN).

### 2. `frontend/src/stores/auth.ts`
- No método `logout()`, executar `localStorage.removeItem('perfilAtivoId')` e redefinir o estado do `usePerfisStore`.
- No método `login()`, após autenticar e buscar as informações do usuário via `fetchUser()`, invocar explicitamente `perfisStore.fetchPerfis()` para garantir o perfil ativo correto no login imediato.

### 3. `src/auth/auth.py`
- Reforçar o retorno no fluxo de autenticação: quando o usuário autenticado via AD não for localizado na tabela SQLite `usuarios`, definir inequivocamente `user_data["groups"] = ["OBSERVADOR", "Users"]`, `user_data["perfil_tipo"] = "OBSERVADOR"` e `user_data["especialidade"] = None`.
- No payload do JWT, incluir `perfil_tipo: "OBSERVADOR"` para usuários não cadastrados.

### 4. `src/routers/perfil.py`
- Garantir que `/api/perfis` sempre retorne o perfil `OBSERVADOR` na lista de perfis disponíveis para que o frontend possa selecioná-lo de forma limpa.
