## 1. Backend Authentication & Permissions

- [x] 1.1 Atualizar `src/auth/auth.py` para atribuir o perfil `OBSERVADOR` como fallback no token JWT caso o usuário Ebserh autenticado não possua perfil cadastrado na tabela de usuários.
- [x] 1.2 Atualizar as dependências de permissão/autorização em `src/routers/` e `src/controllers/` para bloquear requisições mutativas (POST, PUT, DELETE) para o perfil `OBSERVADOR` com HTTP 403 Forbidden.

## 2. Frontend Adaptation

- [x] 2.1 Atualizar as stores Pinia (`perfis.ts` e `auth.ts`) para incluir a definição do perfil `OBSERVADOR` e helpers de verificação (`isObservador`).
- [x] 2.2 Atualizar as telas Vue do frontend para ocultar/desabilitar botões de ação e modais de alteração quando o perfil ativo for `OBSERVADOR`.

## 3. Verification & Validation

- [x] 3.1 Testar login com usuário sem perfil cadastrado e verificar se recebe perfil `OBSERVADOR`.
- [x] 3.2 Testar se chamadas de API mutativas (POST/PUT/DELETE) retornam HTTP 403 para o perfil `OBSERVADOR`.
- [x] 3.3 Testar se a navegação do sistema funciona em modo leitura para o perfil `OBSERVADOR`.
