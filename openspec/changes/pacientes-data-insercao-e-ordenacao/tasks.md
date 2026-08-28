# Tasks: Exibição da Data/Hora de Inserção e Reordenação Multi-Critério no Menu Pacientes

- [x] **1. Mapeamento e Exibição da Data/Hora de Inserção em Pacientes.vue** <!-- id: 0 -->
  - [x] Atualizar `todosPacientesMap` em `frontend/src/views/Pacientes.vue` para extrair e preservar `data_insercao` das solicitações de inclusão e base de pacientes <!-- id: 1 -->
  - [x] Implementar a função utilitária `formatarDataHora` em `Pacientes.vue` para formatação legível `DD/MM/AAAA HH:mm` <!-- id: 2 -->
  - [x] Adicionar a coluna **"Data de Inserção"** no cabeçalho e no corpo da tabela principal (`procedimentosFlat`) <!-- id: 3 -->
  - [x] Adicionar o campo **"Data de Inserção"** nos quadros de procedimentos do Modal de Detalhes do Paciente <!-- id: 4 -->

- [x] **2. Implementar Algoritmo de Reordenação Multi-Critério** <!-- id: 5 -->
  - [x] Implementar função de ranking numérico para Swalis (`A1` > `A2` > `B` > `C` > `D` > Sem Swalis) <!-- id: 6 -->
  - [x] Implementar ordenação cronológica ascendente pela data/hora de inserção (mais antigo primeiro) <!-- id: 7 -->
  - [x] Aplicar ordenação alfabética com `localeCompare('pt-BR')` como terceiro critério de desempate <!-- id: 8 -->

- [x] **3. Validação e Testes** <!-- id: 9 -->
  - [x] Validar a correta renderização das datas de inserção para procedimentos importados e solicitados <!-- id: 10 -->
  - [x] Validar a hierarquia de ordenação na tabela e garantir consistência com os filtros de busca <!-- id: 11 -->
