# Proposal

## Why

Atualmente, as 6 tabelas da **Navegação da Jornada Cirúrgica** exibem a posição bruta do paciente segundo os eventos do AGHU, sem permitir que a operação classifique casos já analisados (como pacientes sem seguimento cirúrgico ou consultas realizadas cujo profissional não deu baixa no AGHU) nem dispare solicitações de ação para avanço de estágio (como reagendar EPO/APA, agendar APA ou sinalizar paciente pronto no Sistema LEC). Introduzir classificações vinculadas ao evento específico do AGHU — que segregam o paciente em subtabelas ("substatus") ou o promovem para a tabela de consulta realizada, geram alertas numéricos em vermelho até que a ação seja "ticada", permitem desfazer a classificação a qualquer momento e retornam automaticamente o paciente à Lista Principal caso surja um novo evento posterior no AGHU — transforma a Navegação em uma ferramenta ativa de gestão de fluxo cirúrgico. Além disso, a `Tabela 4 (APA realizada)` precisa monitorar eventuais **Consultas solicitadas pela APA** de forma análoga às consultas pré-operatórias da `Tabela 2`.

## What Changes

- **Sistema de Classificações, Subtabelas ("Substatus") e Alertas de Ação nas Tabelas `1.2`, `2`, `3.2` e `4`**:
  - Cada uma dessas tabelas passa a contar com uma **"Lista Principal"** (pacientes aguardando análise/classificação no evento atual) e **"Subtabelas"** internas para os pacientes segregados por classificação:
    1. **`Tabela 1.2 - Consulta EPO não realizada`**:
       - `Reagendar consulta EPO`: segrega para subtabela da `1.2`, gera **alerta numérico em vermelho** (para o perfil responsável) até ser **"ticado"** como realizado na subtabela, permanecendo na subtabela até ocorrer novo evento no AGHU.
       - `Sem seguimento cirúrgico`: segrega para subtabela da `1.2`.
       - `Realizada (sem registro no AGHU)`: **envia o paciente para a Lista Principal da `Tabela 2`**, com status equivalente ao de realizada (`Realizado (Sem registro no AGHU)`), enriquecendo-o normalmente com os cards de exames e consultas pré-op e permitindo desfazer a classificação diretamente na `Tabela 2` (retornando-o à Lista Principal da `1.2`).
    2. **`Tabela 2 - Consulta EPO realizada`**:
       - `Agendar consulta APA`: segrega para subtabela da `2`, gera **alerta numérico em vermelho** até ser **"ticado"** como realizado na subtabela, permanecendo na subtabela até ocorrer novo evento no AGHU (ex.: marcação da APA, que o moverá para a `3.1`).
       - `Sem seguimento cirúrgico`: segrega para subtabela da `2`.
    3. **`Tabela 3.2 - APA não realizada`**:
       - `Reagendar consulta APA`: segrega para subtabela da `3.2`, gera **alerta numérico em vermelho** até ser **"ticado"** como realizado na subtabela, permanecendo na subtabela até ocorrer novo evento no AGHU.
       - `Sem seguimento cirúrgico`: segrega para subtabela da `3.2`.
       - `Realizada (sem registro no AGHU)`: **envia o paciente para a Lista Principal da `Tabela 4`**, com status equivalente ao de realizada (`Realizado (Sem registro no AGHU)`), permitindo desfazer a classificação diretamente na `Tabela 4` (retornando-o à Lista Principal da `3.2`).
    4. **`Tabela 4 - APA realizada`**:
       - `Paciente pronto no Sistema LEC`: segrega para subtabela da `4`, gera **alerta numérico em vermelho** até ser **"ticado"** como realizado na subtabela, permanecendo na subtabela até sair da janela temporal analisada ou até ocorrer novo evento no AGHU.
       - `Sem seguimento cirúrgico`: segrega para subtabela da `4`.
- **Encadeamento Temporal Automático entre Eventos do AGHU e Classificações**:
  - Toda classificação fica vinculada ao evento específico do paciente no AGHU (`numero_consulta` + `data_consulta` + `status` no AGHU).
  - Se o paciente tiver uma **nova consulta posterior** no AGHU (ou se a consulta anterior sofrer alteração de desfecho no AGHU), a classificação vinculada ao evento antigo deixa de valer para o novo evento e o paciente **retorna automaticamente para a "Lista Principal"** da tabela correspondente ao novo evento.
- **Desfazimento de Classificação**:
  - No próprio card da classificação (tanto nas subtabelas quanto nos pacientes promovidos para a `Tabela 2` ou `Tabela 4` via `Realizada (sem registro no AGHU)`), há a opção **"Desfazer classificação"**, que remove a classificação atual e devolve o paciente imediatamente ao status e tabela/lista principal em que estava antes.
- **Nova Coluna e Configuração `Consultas solicitadas pela APA` na `Tabela 4`**:
  - Inclusão da coluna **`Consultas solicitadas pela APA`** na `Tabela 4 - APA realizada` (exibindo cards com sigla, nome completo da grade, status e data, além dos filtros de situação e grade na `Tabela 4`, espelhando o funcionamento das consultas pré-operatórias da `Tabela 2`).
  - Inclusão da aba **`Grades de Consultas Solicitadas pela APA`** no modal **`⚙️ Consultas e Exames monitorados`** para que as grades possam ser pesquisadas no AGHU e adicionadas dinamicamente assim que informadas pela equipe.

## Capabilities

### New Capabilities
- `navegacao-jornada-cirurgica-aghu`: Classificações operacionais por estágio, segregação em subtabelas com alertas vermelhos e marcação ("ticar") de ações realizadas, promoção manual de consultas realizadas sem baixa no AGHU (`1.2 -> 2` e `3.2 -> 4`), encadeamento temporal por evento, desfazimento de classificações e monitoramento de consultas solicitadas pela APA na Tabela 4.

### Modified Capabilities
<!-- Nenhuma spec arquivada em openspec/specs/ é alterada diretamente -->

## Impact

- **Banco de Dados Local (`app.db`)**:
  - Nova tabela `navegacao_classificacoes` para persistir as classificações vinculadas ao evento (`pac_codigo`, `prontuario`, `estagio_origem`, `numero_consulta_ref`, `data_consulta_ref`, `grade_sigla_ref`, `classificacao`, `acao_realizada`, metadados de auditoria).
  - Extensão do JSON em `navegacao_config` com a chave `grades_pos_apa` (lista de grades de consultas solicitadas pela APA).
- **Backend (`src/routers/navegacao.py`, `src/models/navegacao_config.py`, `src/helpers/database_migration_helper.py`)**:
  - Endpoints para aplicar classificação, "ticar"/desmarcar ação realizada e desfazer classificação.
  - Lógica de cruzamento entre os eventos mais recentes do AGHU e as classificações ativas respeitando o encadeamento temporal e a promoção `1.2 -> 2` e `3.2 -> 4`.
  - Consulta no AGHU das grades configuradas em `grades_pos_apa` para enriquecer os pacientes da `Tabela 4`.
- **Frontend (`frontend/src/views/NavegacaoLec.vue`)**:
  - Seletor de **Lista Principal vs. Subtabelas** dentro das Tabelas `1.2`, `2`, `3.2` e `4`, com badges vermelhos de alerta para ações pendentes não "ticadas" (também refletidos nos cartões superiores das tabelas).
  - Controles de classificação na Lista Principal, checkbox/botão de "Ticar ação realizada" nas subtabelas com alerta, e botão "Desfazer" no card da classificação.
  - Nova coluna e filtros de `Consultas solicitadas pela APA` na `Tabela 4` e nova aba no modal `⚙️ Consultas e Exames monitorados`.
