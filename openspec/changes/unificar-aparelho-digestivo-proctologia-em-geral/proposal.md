# Proposal

## Why

As especialidades `Aparelho Digestivo` e `Proctologia` devem ser unificadas dentro da especialidade `Geral`, deixando de existir como perfis/especialidades separadas no sistema. A análise prévia no banco de produção da VM e no AGHU comprovou que 100% dos usuários de `Aparelho Digestivo` (27/27) e de `Proctologia` (16/16) já estão cadastrados em `Geral` com a mesma função, tornando a unificação totalmente segura e eliminando fragmentação de filas e perfis.

## What Changes

- **Migração Transacional e Idempotente no Banco de Dados (`app.db`)**:
  - Converter todos os registros de `APARELHO DIGESTIVO` (`APARELHO_DIGESTIVO`, `CIRURGIA DO APARELHO DIGESTIVO`) e `PROCTOLOGIA` para `GERAL` nas tabelas `pacientes`, `solicitacoes`, `categorizacoes_profissionais` e `solicitacoes_criacao_usuario`.
  - Migrar/desduplicar os vínculos na tabela `usuarios` (mantendo o vínculo único com `GERAL`) e remover os perfis `APARELHO_DIGESTIVO` / `APARELHO DIGESTIVO` e `PROCTOLOGIA` da tabela `perfis`.
- **Normalização de Especialidade no Backend e Frontend**:
  - Atualizar `normalize_specialty_name` em `src/helpers/string_helper.py` e `normalizeEsp` nas views/layouts do frontend (`DefaultLayout.vue`, `InteracoesLec.vue`, `Pacientes.vue`, `Historico.vue`, `Perfis.vue`) para mapear `APARELHO DIGESTIVO` e `PROCTOLOGIA` para `GERAL`.
- **Mapeamento de Procedimentos do AGHU (`ESPECIALIDADE_AGHU_MAP`)**:
  - Remover `APARELHO DIGESTIVO` e `PROCTOLOGIA` de `ESPECIALIDADE_AGHU_MAP` em `frontend/src/utils/especialidadeAghuMap.ts`, mantendo `GERAL` vinculado exclusivamente ao código `33` (`CIRURGIA GERAL`) do AGHU.

## Capabilities

### New Capabilities
- `unificacao-especialidades-geral`: Unificação completa e idempotente das especialidades `Aparelho Digestivo` e `Proctologia` dentro de `Geral` em perfis, usuários, solicitações, pacientes, categorizações e mapeamento do AGHU.

### Modified Capabilities
<!-- Nenhuma capability existente possui requisitos conflitantes. -->

## Impact

- **Backend**:
  - `src/helpers/string_helper.py`: `normalize_specialty_name` passa a converter variações de `Aparelho Digestivo` e `Proctologia` para `GERAL`.
  - `src/helpers/database_migration_helper.py`: `migrate_cirurgia_geral_to_geral(conn)` expandida para unificar também `Aparelho Digestivo` e `Proctologia` dentro de `GERAL` de forma transacional na inicialização da aplicação.
- **Frontend**:
  - `frontend/src/utils/especialidadeAghuMap.ts`: Remoção das chaves `'APARELHO DIGESTIVO'` e `'PROCTOLOGIA'`, mantendo `'GERAL': [33]`.
  - `frontend/src/layouts/DefaultLayout.vue`, `frontend/src/views/InteracoesLec.vue`, `frontend/src/views/Pacientes.vue`, `frontend/src/views/Historico.vue`, `frontend/src/views/Perfis.vue`: Normalização de `Aparelho Digestivo` e `Proctologia` para `GERAL`.

