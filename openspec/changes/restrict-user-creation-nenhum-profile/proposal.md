# Proposal: Restringir Criação de Usuários para o Perfil NENHUM

## Summary
Impedir que usuários com perfil `NENHUM` (ou sem perfil específico atribuído) solicitem criação de usuários. A criação de usuários só poderá ser solicitada ou realizada por usuários com perfis válidos associados (`ADMIN`, `GESTAO_LEC`, `ESPECIALIDADE`). Além disso, não deve ser permitido criar nem solicitar a criação de um usuário escolhendo o perfil `NENHUM`, pois este é um perfil padrão de sistema exclusivo para quem ainda não possui usuário cadastrado.

## Why
Garantir a integridade do fluxo de gerenciamento de acessos do Sistema LEC:
1. O perfil `NENHUM` representa a ausência de um usuário pré-cadastrado no sistema local. Um usuário `NENHUM` não deve ser capaz de criar ou solicitar criação de novos usuários no sistema.
2. O perfil `NENHUM` não deve ser uma opção selecionável ao criar/solicitar criação de usuários por outros perfis (`ADMIN`, `GESTAO_LEC`, `ESPECIALIDADE`), pois a finalidade da criação de usuário é justamente associar uma pessoa a um perfil real de atuação no sistema.

## Key Changes
1. **Bloqueio de Criação/Solicitação pelo Perfil `NENHUM`**:
   - No frontend (`Perfis.vue`), ocultar totalmente o formulário de solicitar criação de usuário se o perfil ativo for `NENHUM` (ou `OBSERVADOR`).
   - No backend (`usuario.py`), rejeitar requisições de criação de usuário ou de solicitação de criação vindas de usuários com perfil `NENHUM` (HTTP 403 Forbidden).
2. **Proibição de Selecionar o Perfil `NENHUM` na Criação**:
   - No frontend (`Perfis.vue`), remover a opção `NENHUM` dos selects de perfil ao cadastrar ou solicitar novos usuários.
   - No backend (`usuario.py`), negar criação ou solicitação de usuário caso o `perfil_id` enviado seja `NENHUM` ou `OBSERVADOR` (HTTP 400 Bad Request).

## Impact & Scope
- Form de Usuários e Solicitação em `Perfis.vue`.
- Validadores nos endpoints de usuários e solicitações em `src/routers/usuario.py`.
