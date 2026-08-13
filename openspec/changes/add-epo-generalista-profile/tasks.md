# Tasks: Adicionar Perfil EPO GENERALISTA

- [x] **1. Cadastro do Perfil Padrão e Ordenação no Backend** <!-- id: 0 -->
  - [x] Adicionar o perfil `EPO GENERALISTA` (`EPO_GENERALISTA`) na criação inicial/seed de perfis em `src/models/profile.py` e `src/routers/perfil.py` <!-- id: 1 -->
  - [x] Ajustar a ordem de perfis padrão e suporte no backend <!-- id: 2 -->

- [x] **2. Integração e Estilização no Frontend** <!-- id: 3 -->
  - [x] Cadastrar o perfil `EPO GENERALISTA` em `frontend/src/stores/perfis.ts` com a cor da badge em Laranja (`bg-orange-100 text-orange-800 border-orange-200`) <!-- id: 4 -->
  - [x] Ajustar a ordenação no menu Perfis (`Perfis.vue`): ADMIN → GESTÃO LEC → **EPO GENERALISTA** → ESPECIALIDADES → NENHUM <!-- id: 5 -->

- [x] **3. Permissões de Enfermeiro e Tratamento de Filtro Global** <!-- id: 6 -->
  - [x] Atualizar a verificação `isEnfermeiro` em `InteracoesLec.vue` para incluir o perfil `EPO GENERALISTA` <!-- id: 7 -->
  - [x] Garantir em `Pacientes.vue`, `NavegacaoLec.vue` e `InteracoesLec.vue` que usuários `EPO GENERALISTA` naveguem sem filtro de especialidade automático preso <!-- id: 8 -->

- [x] **4. Build e Deploy na VM** <!-- id: 9 -->
  - [x] Compilar o frontend (`npm run build`) e validar os tipos TypeScript <!-- id: 10 -->
  - [x] Fazer o deploy para a VM via `deploy_app.py` preservando o banco de dados <!-- id: 11 -->
