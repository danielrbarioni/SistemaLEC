## Context

Atualmente, o Sistema LEC gerencia perfis no frontend e utiliza autenticação híbrida (Active Directory em produção, mock estático local para desenvolvimento). Não existe suporte para cadastrar novos usuários ou perfis persistidos no banco de dados local SQLite.

## Goals / Non-Goals

**Goals:**
- Implementar controle de acesso na criação de perfis: apenas usuários ADMIN e GESTÃO LEC podem criar perfis do tipo Especialidade, com cor padrão verde e sem escolha de cor no formulário.
- Implementar a funcionalidade de Criação de Usuários salvando-os no banco de dados local (SQLite).
- Restringir a criação de usuários com base no perfil do criador:
  - ADMIN pode criar qualquer perfil.
  - GESTÃO LEC pode criar apenas GESTÃO LEC e Especialidades.
  - ESPECIALIDADE pode criar apenas usuários de sua própria especialidade.
- Permitir login dos usuários criados localmente (SQLite) quando o provedor correspondente for utilizado.

**Non-Goals:**
- Sincronização automática com servidores AD externos (a criação de usuários locais servirá como cadastro complementar/local).

## Decisions

1. **Modelo de Dados (Tabela `usuarios` no SQLite):**
   Criar a tabela `usuarios` com os campos `id`, `username`, `password_hash`, `nome`, `perfil_id` (vinculado aos perfis do sistema).
   
2. **Nova tabela `perfis` no SQLite:**
   Para podermos criar e associar perfis de forma dinâmica e consistente no backend e frontend, moveremos a persistência dos perfis para o banco SQLite.

3. **Backend (FastAPI):**
   - Rota `POST /api/perfis`: Valida permissão do criador (ADMIN ou GESTÃO LEC) e insere perfil no SQLite.
   - Rota `GET /api/perfis`: Retorna todos os perfis cadastrados.
   - Rota `POST /api/usuarios`: Valida permissão de hierarquia do criador e insere o usuário com senha criptografada.
   - Rota `GET /api/usuarios`: Retorna lista de usuários cadastrados (para visualização no painel).

4. **Frontend (Vue 3):**
   - Ajustar o formulário "Criar Novo Perfil" em `Perfis.vue`: desabilitar/ocultar seleção de cores e tipo (sempre Especialidade e cor verde) e ocultar o painel caso o perfil ativo seja Especialidade.
   - Adicionar o formulário "Criar Novo Usuário" em `Perfis.vue` (ou componente filho), adaptando dinamicamente os perfis disponíveis no dropdown de acordo com a hierarquia do usuário logado.

## Risks / Trade-offs

- **[Risco]** Senhas salvas em texto limpo → **Mitigação**: Armazenar no banco utilizando algoritmo de hash seguro (ex: bcrypt ou passlib).
