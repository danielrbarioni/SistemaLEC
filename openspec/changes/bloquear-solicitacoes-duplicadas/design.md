# Design

## Context

Veja `proposal.md` para a motivação e `specs/solicitacao-duplicidade-validacao/spec.md` para os requisitos de negócio.
Atualmente:
- Em `src/controllers/solicitacao_controller.py`:
  - A validação de `INSERIR` compara `s.get("especialidade") == especialidade and s.get("procedimento") == procedimento` de forma literal (sensível a variações de formatação de ID como `966 - NOME` vs `NOME (ID 966)` e sensível à especialidade), não verifica registros vindos diretamente de `paciente_provider.listar_pacientes()`, e não ignora eventos de auditoria (`evento_tipo not in ("", None, "SOLICITACAO")`) ao checar solicitações pendentes.
  - As validações de `EDITAR`, `STANDBY` e `EXCLUIR` comparam strings apenas com `.lower()` sem extrair o nome base do procedimento e sem filtrar `evento_tipo`, além de não serem reaplicadas em `editar_solicitacao` (`PUT /api/solicitacoes/{id}`).
- Em `frontend/src/views/InteracoesLec.vue`:
  - `enviarSolicitacao` só valida duplicidade preventiva no frontend para a aba `EXCLUIR`, deixando `INSERIR`, `EDITAR` e `STANDBY` sem validação local antes da chamada de rede e sem carregar/cruzar a lista completa de procedimentos ativos do paciente na aba `INSERIR`.

## Goals / Non-Goals

**Goals:**
- Garantir comparação canônica da dupla `paciente + procedimento` (pelo prontuário `codigo_paciente` e pelo nome base normalizado do procedimento cirúrgico, independentemente de prefixo/sufixo de ID ou acentuação).
- Validar e bloquear no frontend (`InteracoesLec.vue`) e no backend (`solicitacao_controller.py`) todas as 4 regras:
  1. `INSERIR`: bloquear quando `paciente + procedimento` já existir ativamente em `Pacientes` (seja via solicitações aprovadas reconstruídas ou cadastro base em `pacientes`) **ou** quando já houver solicitação `INSERIR` com status `PENDENTE` para o mesmo `paciente + procedimento`.
  2. `EDITAR`: bloquear quando `paciente + procedimento` (considerando tanto o procedimento original quanto o novo procedimento, caso alterado) já tiver solicitação `EDITAR` com status `PENDENTE` (e também bloquear caso o novo procedimento escolhido na edição já pertença ativamente ao paciente ou tenha inclusão pendente).
  3. `STANDBY` (`STANDBY` / `CANCELAR_STANDBY`): bloquear quando `paciente + procedimento` já tiver solicitação de standby com status `PENDENTE`.
  4. `EXCLUIR`: bloquear quando `paciente + procedimento` já tiver solicitação `EXCLUIR` com status `PENDENTE`.

**Non-Goals:**
- Alterar o esquema de tabelas do banco de dados SQLite ou PostgreSQL (AGHU).
- Impedir que um mesmo paciente tenha múltiplos procedimentos **diferentes** na fila ou solicitações para procedimentos distintos.

## Decisions

### 1. Normalização Canônica do Nome do Procedimento (`normalizar_nome_base_procedimento`)
- **Decisão**: Criar em `src/helpers/string_helper.py` a função `normalizar_nome_base_procedimento(proc: str | None) -> str` equivalente a `extrairNomeBaseProcedimento` do frontend (`frontend/src/utils/procedimentoHelper.ts`), removendo prefixos numéricos (`^\d+\s*[-–—]\s*`), sufixos de ID (`\s*\(\s*(?:ID\s*)?\d+\s*\)$` e `\s*[-–—]\s*(?:ID\s*)?\d+$`), acentos e espaços extras em caixa alta. No frontend (`InteracoesLec.vue`), importar e usar `extrairNomeBaseProcedimento` de `../utils/procedimentoHelper`.
- **Racional**: Na base `Pacientes` e nas solicitações, um mesmo procedimento pode estar gravado como `"COLECISTECTOMIA VIDEOLAPAROSCOPICA (ID 123)"`, `"123 - COLECISTECTOMIA VIDEOLAPAROSCOPICA"` ou `"COLECISTECTOMIA VIDEOLAPAROSCOPICA"`. Comparar pelo nome base normalizado garante que a dupla `paciente + procedimento` seja reconhecida com 100% de precisão.

### 2. Verificação Completa da Dupla `paciente + procedimento` na Base `Pacientes` e Solicitações
- **Decisão**:
  - Criar em `src/controllers/solicitacao_controller.py` uma função auxiliar `_obter_procedimentos_ativos_paciente(codigo: str, solics_paciente: list, paciente_provider)` que reconstrói os procedimentos ativos do paciente exatamente como a tela `Pacientes`:
    1. Reproduz o histórico de solicitações `APROVADO` (`evento_tipo not in ("RESPOSTA", "ALTERACAO", "EDICAO", "CANCELAMENTO")`) aplicando `INSERIR`, `EDITAR` e `EXCLUIR`.
    2. Se o paciente não tiver solicitações aprovadas mas possuir procedimento cadastrado diretamente no `paciente_provider` (`listar_pacientes`), considera também esse procedimento ativo.
  - Filtrar solicitações pendentes reais (`s.get("status") == "PENDENTE"` e `s.get("evento_tipo") not in ("RESPOSTA", "ALTERACAO", "EDICAO", "CANCELAMENTO")`) para verificar conflitos por tipo (`INSERIR`, `EDITAR`, `STANDBY`/`CANCELAR_STANDBY`, `EXCLUIR`), permitindo excluir um `ignore_solic_id` quando chamado a partir de `editar_solicitacao`.
- **Racional**: Centraliza a regra no backend para proteger tanto `POST /api/solicitacoes` quanto `PUT /api/solicitacoes/{id}`, e espelha a mesma verificação em `enviarSolicitacao` no `InteracoesLec.vue` para feedback instantâneo via `toast.error`.

## Risks / Trade-offs

- **[Risk]** Eventos de log no histórico (`evento_tipo == 'ALTERACAO'` ou `'EDICAO'`) herdam `status = 'PENDENTE'` enquanto a solicitação principal está pendente e poderiam gerar falsos positivos se a solicitação principal fosse editada. → **Mitigation**: Ignorar registros cujo `evento_tipo` seja `'RESPOSTA'`, `'ALTERACAO'`, `'EDICAO'` ou `'CANCELAMENTO'` ao checar solicitações pendentes, avaliando apenas a solicitação principal (`evento_tipo in (None, '', 'SOLICITACAO')`).

