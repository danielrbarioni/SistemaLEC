# Design

## Context

Veja `proposal.md` para a motivação e os dados levantados no AGHU e na VM de produção.
O sistema já possui em `src/helpers/database_migration_helper.py` a rotina `migrate_cirurgia_geral_to_geral(conn)` executada na inicialização (`src/main.py`), que unifica `CIRURGIA GERAL` dentro de `GERAL` de forma idempotente e segura.

## Goals / Non-Goals

**Goals:**
- Estender a unificação para incluir `APARELHO DIGESTIVO` (`APARELHO_DIGESTIVO`, `CIRURGIA DO APARELHO DIGESTIVO`) e `PROCTOLOGIA` dentro de `GERAL` em todas as tabelas do SQLite (`perfis`, `usuarios`, `pacientes`, `solicitacoes`, `categorizacoes_profissionais`, `solicitacoes_criacao_usuario`).
- Remover `'APARELHO DIGESTIVO'` e `'PROCTOLOGIA'` de `ESPECIALIDADE_AGHU_MAP`, preservando `'GERAL': [33]`.
- Atualizar `normalize_specialty_name` (backend) e `normalizeEsp` (frontend) para normalizar `Aparelho Digestivo` e `Proctologia` em `GERAL`.

**Non-Goals:**
- Alterar qualquer dado no banco PostgreSQL do AGHU.
- Adicionar os códigos `727` ou `1450` ao mapeamento de `GERAL` no AGHU (`GERAL` permanece estritamente com `[33]`).

## Decisions

### 1. Extensão da Migração Transacional em `src/helpers/database_migration_helper.py`
- **Decisão**: Expandir `migrate_cirurgia_geral_to_geral(conn)` para abranger a lista de especialidades legadas `('CIRURGIA_GERAL', 'CIRURGIA GERAL', 'APARELHO_DIGESTIVO', 'APARELHO DIGESTIVO', 'CIRURGIA DO APARELHO DIGESTIVO', 'PROCTOLOGIA')`:
  1. Garantir que o perfil `GERAL` exista.
  2. Para cada usuário vinculado a qualquer uma dessas especialidades legadas: se já possuir registro em `GERAL`, remover o vínculo redundante (preservando função/nome se necessário); caso contrário, atualizar para `GERAL`.
  3. Excluir da tabela `perfis` os perfis correspondentes a essas especialidades legadas.
  4. Atualizar `especialidade = 'GERAL'` em `pacientes`, `solicitacoes` e `solicitacoes_criacao_usuario`, além de normalizar `perfil_executor` nas solicitações.
  5. Mesclar `categorias_json` na tabela `categorizacoes_profissionais` para médicos que tinham categorização nessas especialidades e em `GERAL`, sem perda nem duplicação.
- **Racional**: Executa dentro da transação `app.state.app_db.engine.begin()` no startup do serviço e é 100% idempotente. No deploy para a VM (`scripts/deploy_to_vm.py`), um backup completo do `app.db` (`app_backup_<timestamp>.db.bak`) é criado antes do restart do serviço.

## Risks / Trade-offs

- **[Risk]** Usuário com sessão aberta no navegador cujo `localStorage` ainda tenha `APARELHO DIGESTIVO` ou `PROCTOLOGIA` selecionado como perfil ativo. → **Mitigation**: Ao atualizar `normalizeEsp` em `DefaultLayout.vue` e nas views para converter `APARELHO DIGESTIVO` e `PROCTOLOGIA` em `GERAL` (e quando `fetchPerfis()` carregar a lista sem esses perfis), o frontend automaticamente seleciona/opera como `GERAL`.

