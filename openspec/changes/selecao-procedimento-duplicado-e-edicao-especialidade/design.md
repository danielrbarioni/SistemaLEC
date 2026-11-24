# Design

## Context

Veja `proposal.md` para a motivação completa. Em resumo:
1. Em `frontend/src/views/InteracoesLec.vue` (`buscarDados()`), a reconstrução dos procedimentos ativos de um paciente utiliza um `Map` indexado por `${s.especialidade}||${s.procedimento}`. Quando um paciente possui dois procedimentos idênticos na mesma especialidade (ex.: duas inclusões aprovadas de `PLASTICA MAMARIA FEMININA NAO ESTETICA (ID 588)` em `PLASTICA`), a segunda sobrescreve a primeira no `Map`, resultando em apenas 1 item em `procedimentosPaciente` e ocultando o seletor `Qual procedimento deseja editar / excluir / colocar em standby?`. Além disso, em `Pacientes.vue` (`todosPacientesMap`), ao processar uma solicitação aprovada de `EXCLUIR`, o filtro `pac.procedimentos.filter(...)` removia todas as instâncias que coincidissem em `especialidade + procedimento` em vez de remover apenas a instância alvo.
2. Na aba `EDITAR` de `InteracoesLec.vue`, a propriedade computada `isEspecialidadeDisabled` retorna `true` sempre que `abaAtiva.value === 'EDITAR'` ou `perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE'`, impedindo a alteração da especialidade do procedimento.

## Goals / Non-Goals

**Goals:**
- Preservar cada instância ativa de procedimento na busca das abas `EDITAR`, `STANDBY` e `EXCLUIR`, exibindo o seletor com **Swalis**, **Médico Responsável** e **Data/Hora de Inserção** sempre que `procedimentosPaciente.length > 1`.
- Rastrear a instância alvo de uma solicitação de `EDITAR`, `STANDBY`, `CANCELAR_STANDBY` ou `EXCLUIR` por meio do identificador `procedimento_alvo_id` (ID da solicitação `INSERIR` de origem daquela instância), garantindo que edições, standbys e exclusões afetem exclusivamente a instância selecionada.
- Permitir a alteração da especialidade na aba `EDITAR` para `ADMIN` e `GESTAO_LEC` (qualquer especialidade) e para usuários de `ESPECIALIDADE` que possuam perfil cadastrado tanto na especialidade atual do procedimento (`especialidade_anterior`) quanto na especialidade de destino (`especialidade`).
- Persistir `especialidade_anterior` e `procedimento_alvo_id` na tabela `solicitacoes` com migração automática segura no startup (`ALTER TABLE`).

**Non-Goals:**
- Não alterar o funcionamento da aba `INSERIR`, que continua bloqueando novas inclusões duplicadas para o mesmo `paciente + procedimento`.

## Decisions

### 1. Identificação de instância por `procedimento_alvo_id` e reconstrução em lista
- **Decisão**:
  - Adicionar a coluna opcional `procedimento_alvo_id TEXT` ao modelo `Solicitacao` (`src/models/solicitacao.py`) e na migração de inicialização em `src/main.py`.
  - Em `InteracoesLec.vue` (`buscarDados`), substituir `procMap` por uma lista de instâncias `procsList` (alinhada com `todosPacientesMap` de `Pacientes.vue`), onde cada `INSERIR` aprovado adiciona um item com `id: s.id` e `data_insercao: s.data_criacao || '—'`.
  - Ao reprocessar `EDITAR`, `STANDBY`, `CANCELAR_STANDBY` e `EXCLUIR` (tanto em `InteracoesLec.vue` quanto em `Pacientes.vue` e `_obter_procedimentos_ativos_normalizados` em `solicitacao_controller.py`), localizar o item primeiro por `p.id === s.procedimento_alvo_id` e, como fallback para solicitações legadas sem `procedimento_alvo_id`, usar `findIndex` pela combinação `(especialidade_anterior || especialidade) + (procedimento_anterior || procedimento)`, removendo no `EXCLUIR` apenas 1 ocorrência (`splice(idx, 1)`).
  - Na validação de duplicidade (`_validar_duplicidade_paciente_procedimento` e `enviarSolicitacao`), ao verificar se já existe `EDITAR`, `STANDBY` ou `EXCLUIR` pendente para o procedimento, comparar `procedimento_alvo_id` quando presente, permitindo que duas instâncias distintas do mesmo procedimento duplicado possam receber solicitações independentes (ex.: excluir uma das cópias duplicadas) e bloqueando duas solicitações pendentes para a mesma instância.

### 2. Rastreamento de `especialidade_anterior` e controle de permissão por perfil
- **Decisão**:
  - Adicionar a coluna opcional `especialidade_anterior TEXT` ao modelo `Solicitacao` (`src/models/solicitacao.py`), schemas `SolicitacaoCreate`/`SolicitacaoUpdate` (`src/routers/solicitacao.py`) e migração automática em `src/main.py`.
  - No frontend (`InteracoesLec.vue`):
    - Calcular `especialidadesDoUsuarioLogado`:
      - Se `perfisStore.perfilAtivo.tipo` for `ADMIN` ou `GESTAO_LEC` (ou `authStore.isAdmin`), todas as especialidades de `especialidades.value` são permitidas.
      - Caso contrário, coletar todas as especialidades vinculadas ao usuário logado em `perfisStore.perfisDoUsuario` e `usuariosLocais.value` (filtrando por `u.username.toLowerCase() === authStore.user.username.toLowerCase()`).
    - Na aba `EDITAR`, quando `formCarregadoDaSede.value === true`, habilitar o `<select id="especialidade">` se o usuário for `ADMIN`/`GESTAO_LEC` ou se possuir perfil na especialidade atual (`form.especialidade_anterior`) e tiver mais de 1 especialidade permitida em `especialidadesDoUsuarioLogado`. As opções exibidas no dropdown na aba `EDITAR` serão filtradas por `especialidadesDisponiveisParaEdicao`.
    - Quando o usuário trocar a especialidade na aba `EDITAR`:
      - Manter `form.procedimento = form.procedimento_anterior` caso `desejaAlterarProcedimento === 'Não'` (ou permitir escolher um novo procedimento da nova especialidade caso marque `Sim`).
      - Limpar `form.medico_responsavel` e `form.categorizacao` caso o médico atual não pertença à nova especialidade selecionada, exigindo a seleção de um profissional cadastrado na nova especialidade.
      - Considerar a mudança de especialidade (`!isSameSpecialty(orig.especialidade, form.value.especialidade)`) como alteração válida no formulário de edição.
  - No backend (`src/controllers/solicitacao_controller.py` e `src/routers/solicitacao.py`):
    - Em `criar_solicitacao` e `editar_solicitacao`, quando `tipo == 'EDITAR'` e `especialidade_anterior` diferir de `especialidade`, validar que o usuário executor possui perfil `ADMIN`, `GESTAO_LEC`, ou registros em `usuarios` cobrindo tanto `especialidade_anterior` quanto `especialidade`.
    - Em `SolicitacaoSqliteProvider.atualizar_status_solicitacao`, quando uma solicitação `EDITAR` é aprovada, localizar o registro na tabela `pacientes` usando `solic.especialidade_anterior or solic.especialidade` e atualizar `pac_obj.especialidade = solic.especialidade` além de `pac_obj.procedimento = solic.procedimento`.

## Risks / Trade-offs

- **[Risk] Solicitações legadas sem `procedimento_alvo_id` ou `especialidade_anterior`** → **Mitigação**: Todas as buscas e reconstruções mantêm fallback compatível com registros antigos (`s.especialidade_anterior || s.especialidade` e busca por `findIndex` que afeta apenas uma instância por evento de exclusão/edição).
- **[Risk] Médico responsável inválido após troca de especialidade** → **Mitigação**: Ao alterar a especialidade na aba `EDITAR`, a lista `medicosDaEspecialidade` passa a refletir a nova especialidade e a submissão valida que o médico selecionado pertence à especialidade de destino.
