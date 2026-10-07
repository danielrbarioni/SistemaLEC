# Design

## Context
Ver `proposal.md` para motivação. O sistema gerencia pacientes cirúrgicos no frontend (`Pacientes.vue`), onde já carrega em memória tanto a lista de pacientes quanto o catálogo de solicitações (`/api/solicitacoes`). Cada solicitação já possui metadados ricos (`tipo`, `evento_tipo`, `status`, `detalhes`, `usuario`, `perfil_executor`, `data_criacao`, `procedimento_anterior`).

## Goals / Non-Goals

**Goals:**
- Prover visualização cronológica (linha do tempo) de todos os eventos relevantes associados a cada procedimento no modal de detalhes do paciente em `Pacientes.vue`.
- Exibir com clareza as datas, o autor (perfil e usuário), o tipo de ação e a justificativa/detalhes informados em cada etapa (inclusão na fila, edições, entrada e saída de standby, respostas de aprovação/rejeição).
- Assegurar rastreabilidade retrospectiva para procedimentos importados via planilha Excel e novos procedimentos adicionados ou alterados no futuro.

**Non-Goals:**
- Não alterar o schema de banco de dados (zero migrações de DB, zero tabelas adicionais).
- Não alterar as regras de negócio de submissão de solicitações ou validações no backend.
- Não alterar a tabela principal do menu Pacientes (a alteração fica concentrada nos cards de procedimentos do modal de detalhes).

## Decisions

### Decisão 1: Agregação da Linha do Tempo diretamente no Frontend
- **Abordagem**: Em `todosPacientesMap` (em `Pacientes.vue`), para cada procedimento associado a um paciente, compilar uma coleção ordenada cronologicamente de itens de timeline (`timeline: TimelineItem[]`).
- **Alternativa descartada**: Criar um novo endpoint REST `/api/pacientes/:codigo/procedimentos/:proc/historico`.
- **Justificativa**: O frontend já consome `/api/solicitacoes` e `/api/pacientes` em lote. Reutilizar esses dados evita overhead de rede, elimina requisições N+1 e garante resposta imediata ao abrir o modal de qualquer paciente.

### Decisão 2: Mapeamento de Eventos e Rastreamento de Renomeações
- Cada evento do paciente é associado ao procedimento correto considerando a especialidade e o nome do procedimento (incluindo o vínculo histórico via `procedimento_anterior`).
- **Eventos contemplados**:
  1. **Inclusão**: Origem planilha Excel ou solicitação de inclusão aprovada/executada. Apresenta data de indicação/inclusão e justificativa/dados da fila.
  2. **Edição**: Solicitações de alteração e alterações executadas, com resumo de campos modificados e justificativa textual.
  3. **Standby e Cancelar Standby**: Registro da data, quantidade de dias de standby e motivo/justificativa clínica.
  4. **Respostas e Decisões**: Aprovação, rejeição ou cancelamento da Gestão LEC com a justificativa de deferimento/indeferimento.
  5. **Cadastro Inicial Legado**: Para pacientes que não possuem solicitações na tabela SQLite mas existem na base original, gerar evento inicial sintetizado com a data de inserção registrada.

### Decisão 3: Componente Visual da Linha do Tempo
- Estilo moderno com linha vertical conectando marcadores circulares coloridos (verde para inclusão/aprovação, roxo para standby, azul para edição, vermelho para rejeição/cancelamento, cinza para importação legada).
- Cada card exibe a data formatada (`DD/MM/AAAA HH:mm`), título da ação, responsável (usuário/perfil) e um balão destacado contendo a justificativa.
- Controle de colapso/expansão caso o usuário prefira uma visualização mais resumida.

## Risks / Trade-offs

- **[Risco: Procedimentos renomeados perderem eventos anteriores]** → **Mitigação**: O algoritmo de vinculação verifica tanto `s.procedimento` quanto `s.procedimento_anterior` ao correlacionar solicitações com o procedimento atual.
- **[Risco: Volume de eventos poluir visualmente o modal]** → **Mitigação**: O bloco de linha do tempo terá visual compacto e elegante dentro do card de cada procedimento, com scroll suave ou expansão toggle quando houver múltiplos eventos.
