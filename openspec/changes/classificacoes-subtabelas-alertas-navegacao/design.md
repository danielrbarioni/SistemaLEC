# Design

## Context

Veja `proposal.md` para a motivação e o escopo funcional. O módulo **Navegação da Jornada Cirúrgica** (`src/routers/navegacao.py` e `frontend/src/views/NavegacaoLec.vue`) já organiza os pacientes do AGHU em 6 tabelas (`1.1`, `1.2`, `2`, `3.1`, `3.2` e `4`) aplicando a regra de evento mais recente por paciente e progressão temporal entre EPO e APA (`dt_apa.date() >= dt_epo.date()`).

Como a integração com o banco PostgreSQL do AGHU (`dbaghu`) é estritamente de leitura (`SELECT`), todas as classificações operacionais, segregações em subtabelas e marcações ("ticar") de ações realizadas são persistidas no banco SQLite local (`app.db`) e reconciliadas em tempo real com os eventos mais recentes vindos do AGHU.

## Goals / Non-Goals

**Goals:**
- Persistir classificações operacionais por paciente vinculadas ao evento específico do AGHU (`numero_consulta` + `data_consulta`), garantindo que qualquer novo evento posterior invalide automaticamente a classificação antiga e devolva o paciente à **Lista Principal** da tabela correspondente.
- Implementar as classificações e subtabelas de:
  - **`Tabela 1.2`**: `Reagendar consulta EPO` (subtabela + alerta vermelho a ser ticado), `Sem seguimento cirúrgico` (subtabela) e `Realizada (sem registro no AGHU)` (promove para a Lista Principal da `Tabela 2`).
  - **`Tabela 2`**: `Agendar consulta APA` (subtabela + alerta vermelho a ser ticado) e `Sem seguimento cirúrgico` (subtabela).
  - **`Tabela 3.2`**: `Reagendar consulta APA` (subtabela + alerta vermelho a ser ticado), `Sem seguimento cirúrgico` (subtabela) e `Realizada (sem registro no AGHU)` (promove para a Lista Principal da `Tabela 4`).
  - **`Tabela 4`**: `Paciente pronto no Sistema LEC` (subtabela + alerta vermelho a ser ticado) e `Sem seguimento cirúrgico` (subtabela).
- Permitir desfazer qualquer classificação diretamente no card da classificação, retornando o paciente ao status e lista original.
- Adicionar na `Tabela 4` a coluna **`Consultas solicitadas pela APA`**, seus filtros (`Situação` e `Grades`) e a aba de configuração no modal **`⚙️ Consultas e Exames monitorados`**.

**Non-Goals:**
- Não alterar dados no banco PostgreSQL do AGHU (`dbaghu`).

## Decisions

### 1. Modelo de Persistência e Encadeamento Temporal (`navegacao_classificacoes`)
- **Decisão**:
  - Criar a tabela `navegacao_classificacoes` no SQLite (`app.db`) com os campos:
    - `id` (`VARCHAR` PK — UUID ou chave composta)
    - `pac_codigo` (`INTEGER`, indexado)
    - `prontuario` (`VARCHAR`, indexado)
    - `contexto_evento` (`VARCHAR`: `'EPO'` para classificações sobre o evento EPO nas Tabelas `1.2` e `2`; `'APA'` para classificações sobre o evento APA nas Tabelas `3.2` e `4`)
    - `tabela_origem` (`VARCHAR`: `'T1_2'`, `'T2'`, `'T3_2'`, `'T4'`)
    - `numero_consulta_ref` (`INTEGER`: `c.numero` da consulta EPO ou APA no AGHU no momento da classificação)
    - `data_consulta_ref` (`VARCHAR`: `YYYY-MM-DD HH:MM` da consulta EPO ou APA no momento da classificação)
    - `status_consulta_ref` (`VARCHAR`: status mapeado no momento da classificação)
    - `classificacao` (`VARCHAR`: `'REAGENDAR_EPO'`, `'SEM_SEGUIMENTO'`, `'REALIZADA_SEM_REGISTRO_AGHU'`, `'AGENDAR_APA'`, `'REAGENDAR_APA'`, `'PACIENTE_PRONTO_LEC'`)
    - `requer_acao` (`INTEGER`: `1` para `REAGENDAR_EPO`, `AGENDAR_APA`, `REAGENDAR_APA`, `PACIENTE_PRONTO_LEC`; `0` para os demais)
    - `acao_realizada` (`INTEGER`: `0` = pendente / gera alerta vermelho; `1` = já "ticado" como realizado na subtabela)
    - `usuario_classificacao`, `data_classificacao`, `usuario_acao`, `data_acao`
  - **Regra de Encadeamento Temporal e Promoção em Duas Etapas (`1.2 -> 2` e `3.2 -> 4`)**:
    1. Ao avaliar o evento atual do paciente vindo do AGHU (seja `epo_atual` ou `apa_atual`):
       - Uma classificação registrada no banco só é válida para o evento atual se **`numero_consulta_ref == evento_atual["numero_consulta"]` e `data_consulta_ref == evento_atual["data_consulta"]`**.
       - Se o paciente teve uma **nova consulta** no AGHU (ex.: tinha consulta EPO em `01/03/2026` classificada como `Sem seguimento cirúrgico` ou `Reagendar consulta EPO`, e depois surgiu nova consulta EPO em `01/08/2026`), o `numero_consulta` e a `data_consulta` do evento mais recente mudam. Com isso, a classificação antiga de `01/03/2026` não casa com o novo evento de `01/08/2026` e o paciente **entra automaticamente na Lista Principal** da tabela correspondente ao novo evento!
       - Além disso, se uma consulta que estava `Agendado (Data Passada)` ou `Falta` na `Tabela 1.2` / `3.2` tiver seu retorno alterado oficialmente no AGHU para `Realizado` (`ret_seq = 10` ou `60`), o paciente avança normalmente pelo status oficial do AGHU para a `Tabela 2` / `Tabela 4`.
    2. **Caso especial — `Realizada (sem registro no AGHU)` (`1.2 -> 2` e `3.2 -> 4`)**:
       - Quando um paciente na `Tabela 1.2` recebe a classificação `REALIZADA_SEM_REGISTRO_AGHU` para sua consulta `epo_atual`:
         - Ele é promovido da `Tabela 1.2` para a **`Tabela 2 (Consulta EPO realizada)`**, recebendo `status = "Realizado"`, `status_detalhe = "Realizado (Sem registro no AGHU)"`, `promovido_sem_registro = True`, e é enriquecido normalmente com os cards de **Exames Pré-Operatórios** e **Consultas Pré-Operatórias**.
         - Uma vez na `Tabela 2`, ele aparece na **Lista Principal da Tabela 2** (com botão de *"Desfazer classificação 'Realizada sem registro'"* no card de status, que o devolve à Lista Principal da `Tabela 1.2`).
         - Estando na Lista Principal da `Tabela 2`, ele também pode receber uma classificação própria da `Tabela 2` (`Agendar consulta APA` ou `Sem seguimento cirúrgico`). Para permitir que um paciente promovido de `1.2 -> 2` (ou `3.2 -> 4`) também seja classificado em `T2` (ou `T4`) sem perder o vínculo de promoção, armazenamos uma linha por `(pac_codigo, tabela_origem)`:
           - A classificação em `tabela_origem = 'T1_2'` (`REALIZADA_SEM_REGISTRO_AGHU`) promove o paciente para `T2`.
           - Se na `T2` ele receber `AGENDAR_APA` (`tabela_origem = 'T2'`), ele passa para a subtabela `Agendar consulta APA` da `T2`. Se o usuário desfizer `AGENDAR_APA`, ele volta para a Lista Principal da `T2`; se desfizer `REALIZADA_SEM_REGISTRO_AGHU`, ele volta para a Lista Principal da `T1_2`!

### 2. Visualização de Lista Principal, Subtabelas e Alertas em Vermelho
- **Decisão**:
  - Em cada tabela que possui classificações (`Tabela 1.2`, `Tabela 2`, `Tabela 3.2` e `Tabela 4`), será exibida uma barra de **Subtabelas (Substatus)** logo acima dos filtros da tabela:
    - **Aba `Lista Principal`**: exibe apenas os pacientes daquela tabela que **não** estão segregados em nenhuma subtabela daquela etapa.
    - **Abas das Subtabelas** (ex. na `1.2`: `Reagendar consulta EPO` e `Sem seguimento cirúrgico`; na `2`: `Agendar consulta APA` e `Sem seguimento cirúrgico`; na `3.2`: `Reagendar consulta APA` e `Sem seguimento cirúrgico`; na `4`: `Paciente pronto no Sistema LEC` e `Sem seguimento cirúrgico`).
  - **Contador de Alerta em Vermelho**:
    - Para as subtabelas que geram solicitação de ação (`Reagendar consulta EPO`, `Agendar consulta APA`, `Reagendar consulta APA`, `Paciente pronto no Sistema LEC`), a quantidade de pacientes com **`acao_realizada == False`** (ação pendente ainda não "ticada") é exibida em um **badge vermelho de alerta** (`bg-red-600 text-white animate-pulse/shadow`) tanto na aba da subtabela quanto no cartão superior de seleção da tabela (`Tabela 1.2`, `Tabela 2`, `Tabela 3.2`, `Tabela 4`).
    - Quando o usuário entra na subtabela e **"tica" (marca como realizada)** a ação naquele paciente:
      - O contador vermelho de alertas pendentes diminui imediatamente;
      - O paciente **permanece naquela subtabela** (com badge verde `"✓ Ação realizada"` + data/usuário e possibilidade de desmarcar o check ou desfazer a classificação) até que ocorra um novo evento no AGHU (ou saia da janela temporal).

### 3. Coluna `Consultas solicitadas pela APA` na `Tabela 4`
- **Decisão**:
  - Adicionar `grades_pos_apa: List[Dict[str, Any]] = []` em `DEFAULT_NAVEGACAO_CONFIG` (`src/routers/navegacao.py`).
  - No modal **`⚙️ Consultas e Exames monitorados`**, adicionar a aba **`Grades de Consultas Solicitadas pela APA`** (com a mesma busca ao vivo no catálogo de especialidades/grades do AGHU).
  - Para os pacientes da `Tabela 4`, caso existam grades ativas em `grades_pos_apa`, buscar no AGHU com `DISTINCT ON (c.pac_codigo, e.sigla)` a consulta mais recente do paciente naquelas grades e retornar em `item["consultas_pos_apa"]`, exibindo os cards na nova coluna **`Consultas solicitadas pela APA`** da `Tabela 4` e disponibilizando na `Tabela 4` os filtros **`Situação das Consultas Solicitadas pela APA`** e **`Grades Solicitadas pela APA`**.

## Risks / Trade-offs

- **[Risk] Invalidação de cache ao classificar, ticar ação ou desfazer classificação** → **Mitigação**: As operações de classificação/check/desfazimento atualizam apenas o SQLite (`app.db`); podemos separar o cache da query bruta do AGHU (`_NAVEGACAO_AGHU_RAW_CACHE`) da camada que aplica as classificações do SQLite, de forma que classificar, ticar ou desfazer responda em **menos de 20 ms** sem precisar reconsultar o PostgreSQL do AGHU a cada clique!
