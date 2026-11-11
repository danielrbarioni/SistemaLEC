# Proposal: Saneamento de Procedimentos Genéricos e Especialidades (`saneamento-procedimentos-e-especialidades`)

## Why
Na migração inicial das "listas antigas do AGHU" para o Comunicação Cirúrgica via importação de planilhas, diversos registros receberam nomes de procedimentos genéricos (`PROCEDIMENTO <ID>`) em vez da nomenclatura oficial do AGHU:
- **Ginecologia Geral (`GINECOLOGIA GERAL`)**: 242 pacientes ficaram com `PROCEDIMENTO 706` a `PROCEDIMENTO 983` (onde o número era o número sequencial de linha da planilha de importação, e não o `pci_seq` do AGHU). Destes 242 pacientes, **239** possuem seu procedimento real identificado na base do Sistema LEC (com o respectivo `pci_seq` do AGHU), enquanto **3** não constavam mais na planilha da LEC de 05/11.
- **Dermatologia (`DERMATOLOGIA`)**: 33 pacientes ficaram com `PROCEDIMENTO 966` (código AGHU `966`), cujo nome oficial no AGHU e no Sistema LEC é `BIOPSIA DE PELE E PARTES MOLES (ID 966)`.
- **Geral (`GERAL`)**: 1 paciente (Prontuário `11118031` — `SERGIO DE ALBUQUERQUE ANGELOS`) ficou com `PROCEDIMENTO 326` (código AGHU `326`), cujo nome oficial no AGHU e no Sistema LEC é `FISTULECTOMIA  FISTULOTOMIA ANAL (ID 326)`.

Além disso, existem duas inconsistências de especialidades que precisam ser corrigidas:
1. **Pacientes de Cirurgia Bariátrica na especialidade `GERAL`**: Existem **21 pacientes ativos** na especialidade `GERAL` com o procedimento `CIRURGIA BARIATRICA POR VIDEOLAPAROSCOPIA (ID 26)` que devem pertencer à especialidade `BARIÁTRICA`.
2. **Duplicidade de especialidade no filtro do menu Pacientes após renomeação (`ONCO - MASTO` e `ONCO-MASTO`)**: Um usuário Gestão LEC criou a especialidade `ONCO - MASTO`, posteriormente editada para `ONCO-MASTO` no menu Usuários. No entanto, a edição do perfil atualizou apenas a tabela `perfis`, mantendo `ONCO - MASTO` na tabela `usuarios` e nos registros de auditoria da tabela `solicitacoes` (`CRIAR_PERFIL` / `CRIAR_USUARIO` com `origem_menu = 'Usuários'`), fazendo com que ambos (`ONCO - MASTO` e `ONCO-MASTO`) aparecessem no filtro de Especialidades do menu `Pacientes`.

## What Changes
1. **Saneamento dos 239 pacientes da Ginecologia Geral**:
   - Atualizar o campo `procedimento` (e `procedimento_anterior` quando aplicável) nas tabelas `solicitacoes` e `pacientes` para os 239 pacientes identificados na Ginecologia Geral, substituindo `PROCEDIMENTO 706..983` pelo formato padrão `<NOME DO PROCEDIMENTO AGHU> (ID <pci_seq>)`.
   - Remover os nomes genéricos (`PROCEDIMENTO 706`..`PROCEDIMENTO 983`) do filtro de procedimentos do menu `Pacientes`.
2. **Saneamento dos 33 pacientes da Dermatologia**:
   - Atualizar os 33 pacientes da `DERMATOLOGIA` (e registros órfãos/históricos com `PROCEDIMENTO 966`) para `BIOPSIA DE PELE E PARTES MOLES (ID 966)` nas tabelas `solicitacoes` e `pacientes`.
   - Remover `PROCEDIMENTO 966` do filtro de procedimentos do menu `Pacientes`.
3. **Saneamento do paciente da Geral**:
   - Atualizar o paciente da `GERAL` (Prontuário `11118031` — `SERGIO DE ALBUQUERQUE ANGELOS`) de `PROCEDIMENTO 326` para `FISTULECTOMIA  FISTULOTOMIA ANAL (ID 326)` nas tabelas `solicitacoes` e `pacientes`.
   - Remover `PROCEDIMENTO 326` do filtro de procedimentos do menu `Pacientes`.
4. **Reclassificação dos 21 pacientes de Cirurgia Bariátrica**:
   - Alterar a `especialidade` dos 21 pacientes da `GERAL` com procedimento `CIRURGIA BARIATRICA POR VIDEOLAPAROSCOPIA (ID 26)` (nas tabelas `solicitacoes` e `pacientes`) de `GERAL` para `BARIÁTRICA`.
5. **Unificação de `ONCO - MASTO` para `ONCO-MASTO` e Prevenção em Renomeações Futuras**:
   - Atualizar todos os registros existentes (`usuarios`, `solicitacoes`, `pacientes`, `categorizacoes_profissionais`) que possuam `especialidade = 'ONCO - MASTO'` para `'ONCO-MASTO'`.
   - Em `PUT /api/perfis/{perfil_id}` (`src/routers/perfil.py`), ao renomear a especialidade de um perfil (`Profile.especialidade`), propagar automaticamente a alteração em cascata para `usuarios.especialidade`, `solicitacoes.especialidade`, `pacientes.especialidade` e `categorizacoes_profissionais.especialidade`.
   - Em `frontend/src/views/Pacientes.vue`:
     - Excluir eventos administrativos de `Usuários`/`Perfis` (`origem_menu === 'Usuários'` / `CRIAR_PERFIL` / `CRIAR_USUARIO` / `codigo_paciente === 0`) da lista de solicitações de pacientes e da construção dos filtros de especialidade e procedimento.
     - Construir `procedimentosOpcoes` considerando apenas procedimentos ativos (e o catálogo oficial do AGHU da especialidade), filtrando nomes genéricos residuais (`/^PROCEDIMENTO\s+\d+$/i`).

## Capabilities

### New Capabilities
- `saneamento-procedimentos-e-especialidades`: Rotina de saneamento de dados de procedimentos genéricos (`GINECOLOGIA GERAL`, `DERMATOLOGIA`, `GERAL`), transferência dos 21 pacientes de `CIRURGIA BARIATRICA POR VIDEOLAPAROSCOPIA (ID 26)` para `BARIÁTRICA`, unificação de `ONCO - MASTO` para `ONCO-MASTO`, atualização em cascata ao renomear especialidades e blindagem dos filtros do menu `Pacientes`.

### Modified Capabilities
- Nenhuma capability existente teve requisitos conflitantes; trata-se de saneamento de dados e correção comportamental na edição de perfis/filtros de `Pacientes`.

## Impact
- **Backend (`src/routers/perfil.py`)**: `update_perfil` passa a propagar mudanças de nome de especialidade para `User`, `Solicitacao`, `Patient` e `CategorizacaoProfissional`.
- **Script/Migração de Saneamento (`scripts/saneamento_procedimentos_especialidades.py`)**: Atualiza de forma idempotente e transacional os registros do banco SQLite (`app.db`) para os 5 itens solicitados.
- **Frontend (`frontend/src/views/Pacientes.vue`)**: Higieniza `solicitacoes`, `especialidades` e `procedimentosOpcoes` para evitar poluição por logs administrativos ou procedimentos genéricos inativos/substituídos.

