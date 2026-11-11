## 1. Script de Saneamento de Dados (`scripts/saneamento_procedimentos_especialidades.py`)

- [x] 1.1 Criar o script `scripts/saneamento_procedimentos_especialidades.py` com o mapeamento dos 239 pacientes da `GINECOLOGIA GERAL` (`PROCEDIMENTO 706`..`PROCEDIMENTO 983` -> `<NOME AGHU> (ID <pci_seq>)`), atualizando `solicitacoes` e `pacientes`.
- [x] 1.2 Incluir no script a atualização dos 33 pacientes da `DERMATOLOGIA` (e registros correlatos) de `PROCEDIMENTO 966` para `BIOPSIA DE PELE E PARTES MOLES (ID 966)`.
- [x] 1.3 Incluir no script a atualização do paciente da `GERAL` (Prontuário `11118031` — `SERGIO DE ALBUQUERQUE ANGELOS`) de `PROCEDIMENTO 326` para `FISTULECTOMIA  FISTULOTOMIA ANAL (ID 326)`.
- [x] 1.4 Incluir no script a transferência de especialidade (`GERAL` -> `BARIÁTRICA`) dos 21 pacientes com procedimento `CIRURGIA BARIATRICA POR VIDEOLAPAROSCOPIA (ID 26)` nas tabelas `solicitacoes` e `pacientes`.
- [x] 1.5 Incluir no script a unificação de `ONCO - MASTO` para `ONCO-MASTO` em `usuarios`, `solicitacoes`, `pacientes` e `categorizacoes_profissionais`.

## 2. Backend: Propagação em Cascata ao Renomear Especialidade

- [x] 2.1 Atualizar `PUT /api/perfis/{perfil_id}` em `src/routers/perfil.py` (`update_perfil`) para propagar automaticamente a mudança de nome de especialidade (`old_esp` -> `new_esp`) nas tabelas `usuarios`, `solicitacoes`, `pacientes` e `categorizacoes_profissionais`.

## 3. Frontend: Blindagem dos Filtros no Menu Pacientes (`frontend/src/views/Pacientes.vue`)

- [x] 3.1 Atualizar o computed `solicitacoes` em `frontend/src/views/Pacientes.vue` para ignorar registros administrativos do menu `Usuários` (`origem_menu === 'Usuários'` / `codigo_paciente === 0` / tipos `CRIAR_PERFIL`, `CRIAR_USUARIO`, etc.), evitando que logs de criação/edição de perfis poluam o filtro de Especialidade.
- [x] 3.2 Atualizar o computed `procedimentosOpcoes` em `frontend/src/views/Pacientes.vue` para considerar procedimentos ativos (`todosPacientesMap`) além do catálogo AGHU da especialidade e filtrar nomes genéricos residuais (`/^PROCEDIMENTO\s+\d+/i`), removendo `PROCEDIMENTO 706`..`983`, `PROCEDIMENTO 966` e `PROCEDIMENTO 326` do filtro de procedimentos.

## 4. Validação e Testes

- [x] 4.1 Testar a execução do script de saneamento sobre a cópia do banco da VM e validar contagens (239 Ginecologia, 33 Dermatologia, 1 Geral, 21 Bariátrica, 0 ocorrências de `ONCO - MASTO`).
- [x] 4.2 Validar o build do frontend (`npm run build`) e o teste de renomeação de especialidade no backend.

