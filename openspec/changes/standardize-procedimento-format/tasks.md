# Tasks: Padronizar Formato e Eliminar Duplicidades de Procedimentos

- [x] **1. Criar Função de Normalização de Procedimentos** <!-- id: 0 -->
  - [x] Implementar helper de formatação unificada no padrão `NOME DO PROCEDIMENTO (ID XXX)` tanto no frontend quanto no backend <!-- id: 1 -->

- [x] **2. Atualizar Filtros e Exibições no Frontend** <!-- id: 2 -->
  - [x] Atualizar `Pacientes.vue` para normalizar e desduplicar a lista do filtro de procedimentos e as informações dos cards/tabela <!-- id: 3 -->
  - [x] Atualizar `InteracoesLec.vue` para normalizar e desduplicar os procedimentos nos formulários e históricos <!-- id: 4 -->
  - [x] Atualizar `NavegacaoLec.vue` para normalizar e desduplicar procedimentos nas abas e listas <!-- id: 5 -->

- [x] **3. Deploy na VM e Validação** <!-- id: 6 -->
  - [x] Gerar build do frontend e realizar deploy dos arquivos atualizados para a VM sem alterar o banco de dados da VM <!-- id: 7 -->
  - [x] Validar a ausência de duplicidades e formatação `NOME DO PROCEDIMENTO (ID XXX)` em todos os menus <!-- id: 8 -->
