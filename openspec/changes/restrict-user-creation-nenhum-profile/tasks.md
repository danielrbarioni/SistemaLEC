# Tasks: Restringir Criação de Usuários para o Perfil NENHUM

- [x] **1. Impedir Perfil NENHUM de Criar / Solicitar Usuários** <!-- id: 0 -->
  - [x] Ocultar o formulário de criação/solicitação de usuário em `Perfis.vue` para usuários com perfil `NENHUM` <!-- id: 1 -->
  - [x] Validar no backend (`src/routers/usuario.py`) para bloquear requisições de criação de usuário/solicitação enviadas por usuários com perfil `NENHUM` <!-- id: 2 -->

- [x] **2. Proibir Seleção e Atribuição do Perfil NENHUM para Novos Usuários** <!-- id: 3 -->
  - [x] Filtrar os selects de perfil em `Perfis.vue` para remover a opção `NENHUM` na criação de usuários <!-- id: 4 -->
  - [x] Validar no backend (`src/routers/usuario.py`) para rejeitar criação/solicitação de usuário com perfil_id `NENHUM` <!-- id: 5 -->

- [x] **3. Deploy na VM e Validação** <!-- id: 6 -->
  - [x] Fazer build do frontend e deploy para a VM preservando os dados da VM <!-- id: 7 -->
  - [x] Validar restrições no ambiente da VM <!-- id: 8 -->
