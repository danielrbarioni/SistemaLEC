# Design

## Context

No componente `frontend/src/views/Pacientes.vue`, os dados dos pacientes são agregados em `todosPacientesMap` combinando a base inicial de pacientes com o histórico de solicitações aprovadas da LEC.
A renderização e filtragem ocorrem na computed `pacientesProcessados`.
Atualmente, existem quatro checkboxes de filtros divididos em duas colunas:
1. Procedimentos:
   - `filtroApenasUmProcedimento`: Pacientes com exatamente 1 procedimento cadastrado.
   - `filtroApenasMultiplos`: Pacientes com mais de 1 procedimento cadastrado.
2. Especialidades:
   - `filtroApenasUmaEspecialidade`: Pacientes com exatamente 1 especialidade vinculada.
   - `filtroApenasMultiplasEspecialidades`: Pacientes com mais de 1 especialidade vinculada.

O usuário solicitou adicionar uma terceira opção na coluna de procedimentos:
- **"Exibir apenas pacientes com procedimento duplicado"** (paciente que tem o mesmo procedimento cadastrado mais de uma vez).

## Goals / Non-Goals

**Goals:**
- Adicionar o estado reativo `filtroApenasProcedimentoDuplicado` (boolean, padrão `false`).
- Inserir o novo checkbox na interface na coluna de procedimentos, mantendo o layout harmônico e estilizado.
- Garantir a alternância exclusiva entre as três opções de procedimentos (ao marcar uma, desmarcar as outras duas).
- Implementar algoritmo de detecção de duplicidade comparando os procedimentos do paciente após normalização pelo helper `procedimentoHelper`.
- Filtrar `pacientesProcessados` quando o filtro estiver ativo.

**Non-Goals:**
- Não alterar a tabela de especialidades ou os filtros de especialidade.
- Não alterar regras de negócio de inclusão/edição/exclusão de solicitações no backend.
- Não mesclar ou excluir automaticamente procedimentos duplicados (este filtro tem caráter de auditoria/consulta).

## Decisions

### 1. Critério de detecção de procedimento duplicado
- **Decisão**: Utilizar `extrairNomeBaseProcedimento(formatarNomeProcedimento(p.procedimento || ''))` para padronizar o nome do procedimento antes de comparar duplicidades.
- **Justificativa**: Garante que procedimentos com pequenas variações de notação (com ou sem ID sufixado, e.g. "HERNIORRAFIA (ID 123)" vs "HERNIORRAFIA") sejam reconhecidos como o mesmo procedimento.
- **Alternativa descartada**: Comparação de string exata `===`, que falharia caso um registro tivesse sufixo `(ID 999)` e outro não.

### 2. Exclusividade mútua entre filtros de procedimento
- **Decisão**: Usar watchers do Vue 3 para resetar os outros dois filtros quando qualquer um dos três for ativado:
  - Se `filtroApenasProcedimentoDuplicado` se tornar `true`, define `filtroApenasUmProcedimento = false` e `filtroApenasMultiplos = false`.
  - Se `filtroApenasUmProcedimento` se tornar `true`, define `filtroApenasProcedimentoDuplicado = false`.
  - Se `filtroApenasMultiplos` se tornar `true`, define `filtroApenasProcedimentoDuplicado = false`.
- **Justificativa**: Mantém consistência com o comportamento existente entre `filtroApenasUmProcedimento` e `filtroApenasMultiplos`, evitando estados conflitantes de seleção.

### 3. Escopo da detecção de duplicidade
- **Decisão**: A detecção avalia se o paciente possui o mesmo procedimento cadastrado mais de uma vez no histórico de procedimentos (`pac.procedimentos`). Se o usuário também estiver com filtro de especialidade ativo, o paciente precisa ter procedimentos na especialidade ativa e possuir o procedimento duplicado.
- **Justificativa**: Segue o padrão de `totalProcedimentosGerais` e `totalEspecialidadesGerais`.

## Risks / Trade-offs

- **[Performance com listas grandes]** → A checagem de duplicidade percorre a lista de procedimentos de cada paciente usando `Map` de contagem O(N), onde N é o número de procedimentos por paciente (tipicamente de 1 a 10). O impacto é imperceptível (microsegundos).
- **[Procedimentos nulos ou vazios]** → Registros com string de procedimento vazia ou não informada serão desconsiderados na checagem de duplicidade para evitar falsos positivos de pacientes com múltiplos registros em branco.
