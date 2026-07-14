## 1. Backend API (FastAPI)

- [x] 1.1 Atualizar permissões de criação de perfil no endpoint `POST /api/perfis` em `src/routers/perfil.py` para permitir que ADMIN e GESTAO_LEC criem, e bloquear ESPECIALIDADE
- [x] 1.2 Atualizar validações de hierarquia e especialidade obrigatória no endpoint `POST /api/usuarios` em `src/routers/usuario.py`

## 2. Frontend (Vue 3)

- [x] 2.1 Reordenar a tela `Perfis.vue` para colocar a seção de criar usuário acima da seção de criar perfil
- [x] 2.2 Reorganizar campos do formulário "Criar Usuário" em `Perfis.vue` na ordem: Usuário, Nome completo, Perfil de Acesso
- [x] 2.3 Atualizar classes de cores no frontend em `Perfis.vue` (ADMIN cinza, GESTAO_LEC azul, ESPECIALIDADE verde) e remover notas antigas do sistema
- [x] 2.4 Validar o build de produção com `npm run build`
