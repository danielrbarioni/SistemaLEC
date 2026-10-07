# Design

## Context

No frontend, a listagem de procedimentos cirúrgicos é utilizada em dois locais principais:
1. `frontend/src/views/InteracoesLec.vue`: Formulário de criação e edição de solicitações (inserção, edição, standby, exclusão).
2. `frontend/src/views/Pacientes.vue`: Filtro de consulta de pacientes cadastrados no sistema.

Anteriormente, ambos os componentes mesclavam os procedimentos retornados do AGHU com o histórico local de solicitações e pacientes (`extraProcs`). Isso permitia que procedimentos sem ID ou textos livres de importações anteriores (como "CERVICAL" em Geral ou "PROCEDIMENTO 706") fossem selecionados para novas solicitações.

## Goals / Non-Goals

**Goals:**
- Restringir o dropdown de procedimentos em `InteracoesLec.vue` exclusivamente aos procedimentos oficiais ativos do AGHU (`listFromAghu`), garantindo que todas as opções contenham o formato `(ID XXX)`.
- Se o usuário estiver editando uma solicitação cujo procedimento original seja legado (não presente no AGHU), incluir condicionalmente esse procedimento atual na lista para não deixar o campo em branco ou corromper a visualização.
- Preservar no menu Pacientes (`Pacientes.vue`) a listagem completa (`listFromAghu + extraProcs`) para que filtros continuem localizando pacientes cadastrados no passado com nomes legados.
- Preservar sem nenhuma modificação todos os registros no banco de dados SQLite.

**Non-Goals:**
- Não renomear nem migrar procedimentos já gravados no banco de dados.
- Não alterar as tabelas ou queries de banco no backend.

## Decisions

### 1. Separação de propósitos entre Interações (criação/edição) e Pacientes (auditoria/filtro)
- **Decisão**: Em `InteracoesLec.vue`, a computed `procedimentosDaEspecialidade` passará a retornar apenas `listFromAghu` (mais o procedimento corrente caso seja edição de um registro existente). Em `Pacientes.vue`, a computed `procedimentosOpcoes` continuará incluindo `extraProcs`.
- **Justificativa**: Respeita os dois requisitos de negócio solicitados: impede cadastros novos com nomes indevidos e permite encontrar pacientes antigos pelos seus nomes cadastrados.

### 2. Tratamento de edição de registros legados
- **Decisão**: Se `form.procedimento` possuir um valor que não consta em `listFromAghu` (ex: um paciente antigo cadastrado como `HERNIOPLASTIA INGUINAL / CRURAL (UNILATERAL)` sem ID), o valor é adicionado ao topo da lista de opções durante a edição.
- **Justificativa**: Evita que o `<select>` do Vue fique vazio ou desmarque o procedimento existente ao abrir a edição.

## Risks / Trade-offs

- **[Indisponibilidade temporária de rede com AGHU]** → O helper `especialidadeAghuMap` já possui cache em memória de procedimentos por especialidade durante a sessão e tratamento de erro gracioso.
