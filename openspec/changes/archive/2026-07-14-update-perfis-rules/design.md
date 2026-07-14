## Context

Precisamos ajustar e reorganizar a interface e as regras de negócio de usuários e perfis locais no backend (FastAPI) e frontend (Vue 3).

## Goals / Non-Goals

**Goals:**
- Reordenar as seções na visualização do frontend (`Perfis.vue`) para posicionar "Criar Usuário" acima de "Criar Novo Perfil".
- Definir cores dos perfis: ADMIN como cinza, GESTÃO LEC como azul e ESPECIALIDADE como verde.
- Organizar campos do formulário "Criar Usuário": 1. Usuário, 2. Nome completo, 3. Perfil de Acesso.
- Atualizar permissões de criação de usuário no backend e frontend:
  - ADMIN pode criar qualquer perfil.
  - GESTÃO LEC pode criar GESTÃO LEC e ESPECIALIDADE (com especialidade correspondente).
  - ESPECIALIDADE pode criar apenas usuários de sua própria especialidade.
- Atualizar permissões de criação de perfil:
  - ADMIN e GESTÃO LEC podem criar perfis de novas especialidades.
  - ESPECIALIDADE não pode criar perfis.

**Non-Goals:**
- Sincronização em tempo real de usuários Ebserh/AD com provedores externos (login já funciona via Mock/AD).

## Decisions

1. **Alteração do Layout e Hierarquia Visual no Frontend (`Perfis.vue`):**
   Moveremos fisicamente o bloco de template HTML `<Card>` contendo o formulário de cadastro de usuário para cima do `<Card>` de cadastro de perfis.

2. **Ajuste nas Cores e Remoção de Notas:**
   - Atualizar a função `getCorClass` e o mapeamento de classes para garantir que ADMIN seja cinza (ex: `bg-gray-400`), GESTÃO LEC seja azul (ex: `bg-blue-500`) e ESPECIALIDADE verde (ex: `bg-green-500`).
   - Remover a caixa de nota/lembrete do sistema em `Perfis.vue` que fala sobre cores de perfis e regras legadas.

3. **Backend (`src/routers/usuario.py` e `src/routers/perfil.py`):**
   - No `usuario.py`, ajustar a lógica de validação no endpoint `POST /api/usuarios` para respeitar as novas regras de hierarquia e exigir que a especialidade seja informada se o perfil de destino for ESPECIALIDADE.
   - No `perfil.py`, validar no endpoint `POST /api/perfis` que apenas `ADMIN` e `GESTAO_LEC` podem criar novos perfis do tipo `ESPECIALIDADE`.

## Risks / Trade-offs

- N/A
