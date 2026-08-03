# Tasks: Default OBSERVADOR Profile on Login for Unregistered Users

- [x] 1. Backend (`src/auth/auth.py`): Reforçar que usuários autenticados via AD sem registro na tabela `usuarios` recebam estritamente `perfil_tipo: OBSERVADOR` e `groups: ["OBSERVADOR", "Users"]`.
- [x] 2. Frontend Auth Store (`frontend/src/stores/auth.ts`): Remover `perfilAtivoId` do `localStorage` ao fazer logout e chamar `fetchPerfis()` após login com sucesso.
- [x] 3. Frontend Perfis Store (`frontend/src/stores/perfis.ts`):
  - [x] 3.1 Garantir que o perfil `OBSERVADOR` seja selecionado como ativo quando o usuário não estiver cadastrado em nenhum perfil específico.
  - [x] 3.2 Alterar o fallback de seleção de perfil para que nunca recaia em `data[0]` (ADMIN), usando `OBSERVADOR` como padrão seguro.
- [x] 4. Testes e Validação:
  - [x] 4.1 Testar login de usuário não cadastrado e confirmar atribuição do perfil `OBSERVADOR`.
  - [x] 4.2 Verificar restrição de escrita/edição e seletor de perfil no frontend.
