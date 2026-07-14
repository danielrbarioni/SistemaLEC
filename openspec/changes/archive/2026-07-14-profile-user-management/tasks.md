## 1. Banco de Dados e Modelos

- [x] 1.1 Remover a coluna `password_hash` do modelo `User` em `src/models/user.py`
- [x] 1.2 Atualizar as tabelas do SQLite gerando e executando uma nova migração Alembic

## 2. API Backend (FastAPI)

- [x] 2.1 Ajustar o schema de criação `UserCreate` em `src/routers/usuario.py` para remover a senha
- [x] 2.2 Reverter o método `authenticate_user` de `src/auth/auth.py` para autenticar primeiro via AD/Mock e depois enriquecer o perfil usando o SQLite

## 3. Frontend (Vue 3)

- [x] 3.1 Ajustar o formulário "Criar Usuário" em `Perfis.vue` para remover a senha e rotular como vinculação de usuário AD
- [x] 3.2 Validar build do frontend com `npm run build`
