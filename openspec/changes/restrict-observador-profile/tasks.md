# Tasks: Restringir Perfil 'OBSERVADOR' (Renomeado para 'NENHUM') e Registrar Solicitações no Histórico

- [x] **1. Alterar Perfil OBSERVADOR para NENHUM** <!-- id: 0 -->
  - [x] Renomear o perfil 'OBSERVADOR' para 'NENHUM' no banco de dados / seeds / enums sem afetar dados de pacientes <!-- id: 1 -->
  - [x] Atualizar referências no backend e no frontend onde 'OBSERVADOR' era utilizado <!-- id: 2 -->

- [x] **2. Restringir Acesso e Menus para Perfil NENHUM** <!-- id: 3 -->
  - [x] Ocultar e desabilitar os menus Comunicação LEC, Navegação, Pacientes e Histórico para usuários com perfil 'NENHUM' <!-- id: 4 -->
  - [x] Implementar guarda de rota/bloqueio para que tentativas de navegação a esses menus exibam a mensagem: `'Solicite criação de usuário e associação a um perfil, no menu Perfis'` <!-- id: 5 -->

- [x] **3. Registrar Solicitações no Histórico** <!-- id: 6 -->
  - [x] Adicionar registro de histórico para criação de solicitações de usuário <!-- id: 7 -->
  - [x] Adicionar registro de histórico para aprovação de solicitações de usuário <!-- id: 8 -->
  - [x] Adicionar registro de histórico para criação de solicitações de perfil <!-- id: 9 -->
  - [x] Adicionar registro de histórico para aprovação de solicitações de perfil <!-- id: 10 -->

- [x] **4. Reiniciar Serviços Localhost e VM e Validar** <!-- id: 11 -->
  - [x] Reiniciar serviços locais e na VM mantendo o banco de dados preservado <!-- id: 12 -->
  - [x] Testar acesso com o perfil NENHUM e verificar gravação de histórico de solicitações <!-- id: 13 -->
