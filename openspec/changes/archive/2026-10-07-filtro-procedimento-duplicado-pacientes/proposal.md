# Proposal

## Why

Na gestão de pacientes do Sistema LEC (menu Pacientes), os gestores e equipes médicas precisam identificar rapidamente inconsistências de cadastro, como pacientes que possuem o mesmo procedimento cirúrgico cadastrado mais de uma vez (procedimentos duplicados). Atualmente, existem filtros para pacientes com apenas 1 procedimento ou mais de 1 procedimento, mas não há como isolar diretamente aqueles que possuem procedimentos repetidos/duplicados.

Esta funcionalidade permite auditar a fila cirúrgica, evitar duplicidades de agendamento e manter os dados dos pacientes íntegros.

## What Changes

- Adição de um novo checkbox de filtro na seção de filtros de procedimentos do menu Pacientes: **"Exibir apenas pacientes com procedimento duplicado"**.
- Implementação de exclusividade mútua entre os filtros de procedimento da coluna (selecionar "apenas 1 procedimento", "mais de 1 procedimento" ou "procedimento duplicado" desmarca automaticamente os demais).
- Identificação de duplicidade de procedimentos por paciente considerando a normalização e padronização do nome do procedimento (comparando nomes base ou padronizados para detectar ocorrências repetidas do mesmo procedimento para um mesmo paciente).
- Exibição na listagem de pacientes apenas daqueles que possuem procedimentos duplicados quando o filtro estiver ativo.

## Capabilities

### New Capabilities
- `pacientes-filtros`: Regras e comportamentos de filtragem na visualização de pacientes do Sistema LEC, incluindo filtros por quantidade de procedimentos, especialidades e detecção de procedimentos duplicados.

### Modified Capabilities
<!-- Nenhuma capability existente tem requisitos alterados -->

## Impact

- **Frontend**: Componente `frontend/src/views/Pacientes.vue` (novo estado reativo de filtro, watcher para exclusividade de seleção e lógica de detecção de duplicidades na computação de `pacientesProcessados`).
- **Helpers**: Utilização dos utilitários existentes em `frontend/src/utils/procedimentoHelper.ts` (`formatarNomeProcedimento`, `extrairNomeBaseProcedimento`) para verificação padronizada de procedimentos iguais.
- **Backend / APIs**: Nenhuma alteração de API ou banco de dados necessária (a filtragem é processada no frontend sobre o conjunto de pacientes e solicitações carregadas).
