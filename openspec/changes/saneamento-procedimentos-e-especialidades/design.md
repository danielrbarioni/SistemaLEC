## Context
Durante a auditoria dos dados importados das listas antigas do AGHU para o Comunicação Cirúrgica:
1. Na **Ginecologia Geral (`GINECOLOGIA GERAL`)**, 242 pacientes foram importados com procedimentos `PROCEDIMENTO 706` a `PROCEDIMENTO 983` (onde o número correspondia ao índice da linha da planilha de importação, e não ao código AGHU `pci_seq`). Cruzando com a base do Sistema LEC e o catálogo oficial de procedimentos cirúrgicos do AGHU (`v_fat_associacao_procedimentos` / `mbc_procedimento_cirurgicos`), **239 pacientes** tiveram seu procedimento e `pci_seq` exatos identificados, restando apenas **3 prontuários** que já haviam saído da planilha da LEC de 05/11 (`15915684` com `PROCEDIMENTO 757`, `14602452` com `PROCEDIMENTO 788`, e `21572425` com `PROCEDIMENTO 903`).
2. Na **Dermatologia (`DERMATOLOGIA`)**, 33 pacientes ativos (e registros excluídos/órfãos na mesma faixa) ficaram com `PROCEDIMENTO 966`, cujo código `966` no AGHU e no Sistema LEC corresponde a `BIOPSIA DE PELE E PARTES MOLES (ID 966)`.
3. Na **Geral (`GERAL`)**, 1 paciente ativo (Prontuário `11118031` — `SERGIO DE ALBUQUERQUE ANGELOS`) ficou com `PROCEDIMENTO 326`, cujo código `326` no AGHU e no Sistema LEC corresponde a `FISTULECTOMIA  FISTULOTOMIA ANAL (ID 326)`.
4. Na **Geral (`GERAL`)**, existem **21 pacientes ativos** com o procedimento `CIRURGIA BARIATRICA POR VIDEOLAPAROSCOPIA (ID 26)` que devem ser movidos para a especialidade `BARIÁTRICA`.
5. Quando a especialidade `ONCO - MASTO` foi editada para `ONCO-MASTO` no menu `Usuários`, o endpoint `PUT /api/perfis/{perfil_id}` (`src/routers/perfil.py`) atualizou apenas a tabela `perfis`, deixando `ONCO - MASTO` na tabela `usuarios` e nas linhas de log administrativo da tabela `solicitacoes` (`CRIAR_PERFIL` e `CRIAR_USUARIO` com `codigo_paciente = 0` e `origem_menu = 'Usuários'`). Como `Pacientes.vue` coletava todas as especialidades presentes em `solicitacoes.value` sem ignorar registros administrativos de `Usuários`, ambas as opções (`ONCO - MASTO` e `ONCO-MASTO`) passaram a aparecer no filtro de Especialidades do menu `Pacientes`.

## Goals / Non-Goals

**Goals:**
- Atualizar com precisão cirúrgica os 239 pacientes da Ginecologia Geral, 33 pacientes da Dermatologia e 1 paciente da Geral para seus procedimentos corretos (`<NOME DO PROCEDIMENTO AGHU> (ID <pci_seq>)`) nas tabelas `solicitacoes` e `pacientes`.
- Garantir que os nomes genéricos (`PROCEDIMENTO 706`..`PROCEDIMENTO 983`, `PROCEDIMENTO 966`, `PROCEDIMENTO 326`) desapareçam do filtro de procedimentos do menu `Pacientes`.
- Transferir os 21 pacientes de `CIRURGIA BARIATRICA POR VIDEOLAPAROSCOPIA (ID 26)` da especialidade `GERAL` para `BARIÁTRICA`.
- Unificar `ONCO - MASTO` para `ONCO-MASTO` em todas as tabelas do banco e atualizar `PUT /api/perfis/{perfil_id}` + `Pacientes.vue` para que qualquer renomeação futura de especialidade atualize automaticamente usuários, solicitações, pacientes e categorizações, sem deixar o nome antigo nos filtros.

**Non-Goals:**
- Excluir ou alterar o procedimento dos 3 pacientes da Ginecologia Geral que não constavam mais na planilha do Sistema LEC de 05/11 sem instrução explícita sobre o procedimento deles (mas ocultar os rótulos genéricos `PROCEDIMENTO NNN` do dropdown de filtro de procedimentos em `Pacientes.vue`).

## Decisions

### 1. Script Idempotente de Saneamento (`scripts/saneamento_procedimentos_especialidades.py`)
- **Decisão**: Criar um script Python dedicado e transacional (`scripts/saneamento_procedimentos_especialidades.py`) contendo o mapeamento determinístico (gerado a partir da auditoria `CC x Sistema LEC x AGHU`) para executar no banco SQLite (`app.db`) tanto localmente quanto na VM de produção (`10.34.0.202`) sem perda de dados:
  1. **Ginecologia Geral (239 pacientes)**: Atualiza `solicitacoes.procedimento` (por `id` da solicitação e também para eventuais linhas históricas do mesmo `(codigo_paciente, procedimento_generico)`) e `pacientes.procedimento` para o formato `<DESCRICAO_AGHU> (ID <PCI_SEQ>)`.
  2. **Dermatologia (33 pacientes + históricos)**: Atualiza todas as ocorrências de `PROCEDIMENTO 966` em `solicitacoes.procedimento`, `solicitacoes.procedimento_anterior` e `pacientes.procedimento` (na especialidade `DERMATOLOGIA`) para `BIOPSIA DE PELE E PARTES MOLES (ID 966)`.
  3. **Geral (1 paciente + históricos)**: Atualiza todas as ocorrências de `PROCEDIMENTO 326` em `solicitacoes.procedimento`, `solicitacoes.procedimento_anterior` e `pacientes.procedimento` (na especialidade `GERAL`) para `FISTULECTOMIA  FISTULOTOMIA ANAL (ID 326)`.
  4. **Bariátrica (21 pacientes)**: Atualiza `solicitacoes.especialidade = 'BARIÁTRICA'` e `pacientes.especialidade = 'BARIÁTRICA'` onde `especialidade = 'GERAL'` e `procedimento LIKE 'CIRURGIA BARIATRICA POR VIDEOLAPAROSCOPIA%'`.
  5. **Unificação `ONCO - MASTO` -> `ONCO-MASTO`**: Atualiza `usuarios.especialidade`, `solicitacoes.especialidade`, `pacientes.especialidade` e `categorizacoes_profissionais.especialidade` onde o valor for `'ONCO - MASTO'` (ou com espaços extras ao redor do hífen) para `'ONCO-MASTO'`, além de ajustar o texto de `detalhes` do registro `CRIAR_PERFIL` se necessário.

### 2. Atualização em Cascata ao Renomear Especialidade (`src/routers/perfil.py`)
- **Decisão**: No endpoint `PUT /api/perfis/{perfil_id}` (`update_perfil`), capturar `old_esp = (db_perfil.especialidade or db_perfil.nome or "").strip()` antes da alteração. Quando `db_perfil.tipo == "ESPECIALIDADE"` e o novo nome (`new_esp`) for diferente de `old_esp`:
  - Atualizar `User.especialidade` (`usuarios`) onde `especialidade == old_esp` ou `perfil == db_perfil.id`.
  - Atualizar `Solicitacao.especialidade` (`solicitacoes`) onde `especialidade == old_esp`.
  - Atualizar `Patient.especialidade` (`pacientes`) onde `especialidade == old_esp`.
  - Atualizar `CategorizacaoProfissional.especialidade` (`categorizacoes_profissionais`) onde `especialidade == old_esp`.
  - Dessa forma, se qualquer especialidade (com ou sem procedimentos/pacientes) for renomeada no menu `Usuários`, todos os pacientes, solicitações, médicos e categorizações migram atomicamente para o novo nome.

### 3. Higienização dos Filtros de Especialidade e Procedimento (`frontend/src/views/Pacientes.vue`)
- **Decisão**:
  1. Em `solicitacoes` computed (`Pacientes.vue`, linha ~942), filtrar também registros administrativos oriundos do menu `Usuários` (`origStr === 'usuários' || origStr === 'usuarios'`) ou com `codigo_paciente === 0` / tipos `CRIAR_PERFIL`, `EDITAR_PERFIL`, `EXCLUIR_PERFIL`, `CRIAR_USUARIO`, `EDITAR_USUARIO`, `EXCLUIR_USUARIO`, garantindo que logs de gerenciamento de contas/perfis jamais entrem na lista de solicitações de pacientes nem criem especialidades fantasmas.
  2. Em `procedimentosOpcoes` computed (`Pacientes.vue`, linha ~905):
     - Coletar procedimentos extras apenas dos pacientes **ativos** (`todosPacientesMap.value.values()`) em vez de varrer solicitações já excluídas (`EXCLUIDO`/`REALIZADO`) ou órfãs em `basePacientes`.
     - Filtrar rótulos genéricos legados que casem com `/^PROCEDIMENTO\s+\d+(\s*\(ID\s*\d+\))?$/i`, garantindo que nenhum `PROCEDIMENTO NNN` apareça no dropdown de filtro de procedimentos do menu `Pacientes`.

