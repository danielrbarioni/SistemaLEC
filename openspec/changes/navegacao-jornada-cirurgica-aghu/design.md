# Design

## Context

Veja `proposal.md` para a motivação e o escopo funcional. A arquitetura do módulo **Navegação** parte de três premissas fundamentais validadas com o usuário e no catálogo do banco PostgreSQL do AGHU (`dbaghu`):
1. **Independência total do Sistema LEC e da tabela local `Pacientes`**: A Navegação é construída exclusivamente sobre os eventos de consultas e exames do paciente (`pac_codigo` / `prontuario`) no AGHU.
2. **Integração estritamente unidirecional (Somente Leitura no AGHU)**: Nenhuma escrita é realizada no banco PostgreSQL do AGHU; configurações do circuito cirúrgico e futuras ações locais de navegação (filtros, reclassificações, alertas internos) são persistidas exclusivamente no SQLite local (`app.db`) do Comunicação Cirúrgica.
3. **Mapeamento real das tabelas e status no AGHU (`dbaghu`)**:
   - **Grades / Siglas de Consultas (`agh.agh_especialidades` + `agh.aac_grade_agendamen_consultas`)**:
     - **EPO (Enfermagem Pré-Operatória)**:
       - `EPO` (`seq=1668`): `ENFERMAGEM - PRÉ OPERATÓRIO`
       - `EPG` (`seq=2744`): `ENFERMAGEM PRE-OPERATORIO GINECOLOGIA`
       - `POO` (`seq=2746`): `ENFERMAGEM PRE-OPERATORIO OTORRINO`
       - `OEP` (`seq=2742`): `ENFERMAGEM PRE-OPERATORIO PLASTICA`
       - `POT` (`seq=2309`): `TELEENFERMAGEM PRE-OPERATORIO`
       - `POF` (`seq=2790`): `ENFERMAGEM PRE-OPERATORIO OFTALMOLOGIA`
     - **Consultas Pré-Operatórias (solicitadas pela EPO)**:
       - `RIS` (`seq=1550`): `CARDIO - RISCO CIRURGICO`
       - `PPC` (`seq=2042`): `PNEUMOLOGIA - PARECER`
       - `RCI` (`seq=2514`): `CARDIO - RISCO CIRURGICO INFANTIL`
       - `OHR` (`seq=2830`): `OCI AVALIACAO DE RISCO CIRURGICO`
       - `PPO` (`seq=2696`): `PNEUMOPEDIATRIA - PRE-OPERATORIO`
     - **APA (Avaliação Pré-Anestésica)**:
       - `ANE` (`seq=1534`): `ANESTESIOLOGIA`
       - `TAN` (`seq=2328`): `ANESTESIOLOGIA - TELEMEDICINA`
   - **Status de Consultas no AGHU (`agh.aac_consultas.ret_seq` → `agh.aac_retornos`)**:
     Para consultas marcadas a pacientes (`ind_sit_consulta = 'M'` e `pac_codigo IS NOT NULL`), existem 7 retornos no AGHU, mapeados para os 4 status de negócio da Navegação:
     - **`Agendado`**: `ret_seq = 9` (`PACIENTE AGENDADO`) e `ret_seq = 20` (`AGUARDANDO ATENDIMENTO`)
     - **`Realizado`**: `ret_seq = 10` (`PACIENTE ATENDIDO`) e `ret_seq = 60` (`EM ATENDIMENTO` — quando a consulta foi aberta/atendida pelo profissional)
     - **`Falta do paciente`**: `ret_seq = 40` (`PACIENTE FALTOU`) e `ret_seq = 50` (`PACIENTE DESISTIU CONS`)
     - **`Falta do profissional`**: `ret_seq = 30` (`PROFISSIONAL FALTOU`)
   - **Exames e Status de Exames no AGHU (`agh.ael_exames` + `agh.ael_solicitacao_exames` + `agh.ael_item_solicitacao_exames` + `agh.ael_sit_item_solicitacoes`)**:
     - Os status de itens de exame em `agh.ael_sit_item_solicitacoes` são: `LI` (`LIBERADO`), `EO` (`EXECUTADO`), `EX` (`EXECUTANDO`), `AE` (`AREA EXECUTORA`), `RE` (`RECEBIDO`), `CO` (`COLETADO`), `CS` (`COLETADO PELO SOLICITANTE`), `EC` (`EM COLETA`), `AG` (`AGENDADO`), `AC` (`A COLETAR`), `AX` (`A EXECUTAR`), `PE` (`PENDENTE`), `CA` (`CANCELADO`).
     - Os 8 grupos de exames elencados e validados pela Gestão LEC na Tabela 2.2 organizam o catálogo monitorado em `agh.ael_exames` (configuráveis pela Gestão LEC), enquanto na linha de cada paciente na Tabela 2.2 são exibidos **cards individuais apenas para os exames efetivamente solicitados** para aquele paciente (mostrando o registro mais recente de cada `Prontuário + Sigla do Exame` com seu nome/sigla, status e data):
       1. **Laboratório** (`LAB`): Hemograma (`H`), Coagulograma/TP/TTPA, Glicemia, Ureia, Creatinina, etc.
       2. **Raio X** (`RAIO_X`): `RXPAP` (`RX TÓRAX PA+PERFIL`), `RXCVB`, `RXTX1`, `RXTX4`, `RXTX5`, `RXTX7`, `RXTX9`, `DL`.
       3. **Espirometria** (`ESPIROMETRIA`): `ESP` (`ESPIROMETRIA SEM PROVA FARMACODINÂMICA`), `ESPB` (`ESPIROMETRIA COM PROVA FARMACODINÂMICA`), `ESPP` (`ESPIROMETRIA PEDIÁTRICA`), `ERGOE`.
       4. **Ecocardiograma Transtorácico** (`ECOCARDIOGRAMA`): `ETT` (`ECOCARDIOGRAMA TRANSTORÁCICO`), `ECO` (`ECOCARDIOGRAMA`), `ECOPE` (`ECOCARDIOGRAMA PEDIATRICO`), `ECOBO`, `ETE`.
       5. **Cintilografia Miocárdica** (`CINTILOGRAFIA`): `CMDIP` (`CINTILOGRAFIA DO MIOCARDIO COM DIPIRIDAMOL`), `CMREP` (`CINTILOGRAFIA DO MIOCARDIO EM REPOUSO`), `CMTLR`, `CMPIR`.
       6. **Ressonância Magnética** (`RESSONANCIA`): todas as 205 siglas ativas de ressonância magnética (`UPPER(descricao) LIKE '%RESSON%' OR UPPER(descricao_usual) LIKE '%RESSON%'`).
       7. **Holter 24h** (`HOLTER`): `HOLT` (`HOLTER` / `HOLTER 24 HORAS`).
       8. **Teste de Esteira** (`TESTE_ESTEIRA`): `ERGO` (`ERGOMETRIA` / `TESTE ERGOMETRICO`), `ERGOE` (`ERGOESPIROMETRIA`).

## Goals / Non-Goals

**Goals:**
- Implementar consultas SQL no PostgreSQL do AGHU altamente performáticas usando `DISTINCT ON` para obter apenas o registro mais recente por `(Prontuário + Grade)` ou `(Prontuário + Grupo de Exame)`.
- Disponibilizar as 5 tabelas da jornada cirúrgica (`1`, `2.1`, `2.2`, `3.1`, `3.2`) com seus filtros automáticos, filtros modificáveis e ordenações exatas.
- Disponibilizar busca global por prontuário/nome que mostra em qual(is) das 5 tabelas o paciente aparece.
- Disponibilizar interface para visualizar, pesquisar no AGHU e editar as grades de consultas e os exames de cada grupo pré-operatório, persistindo a configuração no SQLite local.

**Non-Goals:**
- Não realizar nenhuma operação de escrita no banco do AGHU.
- Não implementar nesta etapa as ações operacionais secundárias entre áreas (como disparo de alertas/mensagens), deixando a arquitetura preparada para recebê-las na próxima evolução.

## Decisions

### 1. Estratégia de Busca Performática no AGHU (`DISTINCT ON` + Recorte Temporal + Cache TTL)
- **Decisão**:
  - **Ancoragem por Siglas de Grades + Janela Temporal Configurável (padrão: últimos 12 meses + agendamentos futuros)**:
    - Em uma única query PostgreSQL com `DISTINCT ON (c.pac_codigo, e.sigla)` ordenada por `c.pac_codigo, e.sigla, c.dt_consulta DESC`, buscamos a consulta mais recente de cada `(Paciente, Sigla da Grade)` para todas as siglas configuradas em `EPO` (`EPO, EPG, POO, OEP, POT, POF`) e `APA` (`ANE, TAN`).
    - Essa query executa em menos de **150 ms** no PostgreSQL do AGHU porque filtra diretamente por `g.esp_seq` das siglas monitoradas e `c.ind_sit_consulta = 'M'`.
  - **Enriquecimento seletivo da Tabela 2.2 (apenas para os `pac_codigo` com EPO Realizada)**:
    - Para o subconjunto de `pac_codigo` que se encontram na **Tabela 2.2** (EPO Realizada):
      1. Buscamos com `DISTINCT ON (c.pac_codigo, e.sigla)` a consulta mais recente nas grades pré-operatórias configuradas (`RIS, PPC, RCI, OHR, PPO`).
      2. Buscamos nos pedidos de exame (`agh.ael_solicitacao_exames soe JOIN agh.agh_atendimentos atd ON soe.atd_seq = atd.seq JOIN agh.ael_item_solicitacao_exames ise ON ise.soe_seq = soe.seq`) filtrando `WHERE atd.pac_codigo = ANY(:pac_codigos_epo_realizada) AND ise.ufe_ema_exa_sigla = ANY(:siglas_exames_monitorados) AND ise.sit_codigo <> 'CA'`, usando `DISTINCT ON (atd.pac_codigo, ise.ufe_ema_exa_sigla)` para retornar o item mais recente de cada exame individual solicitado para o paciente, que será exibido como um **card** na linha do paciente na Tabela 2.2.
  - **Cache em memória no Backend com TTL (60s) + Botão "Atualizar do AGHU"**:
    - O resultado consolidado das 5 tabelas fica em cache em memória por 60 segundos (e é invalidado imediatamente quando a configuração de grades/exames é alterada ou quando o usuário clica em *"Atualizar dados do AGHU"*). Assim, a navegação entre as 5 abas/tabelas, a aplicação de filtros modificáveis e a busca global por prontuário ocorrem instantaneamente no frontend.

### 2. Estrutura de Configuração Persistida em SQLite (`navegacao_config`)
- **Decisão**:
  - Criar a tabela `navegacao_config` no SQLite local (`app.db`) contendo um documento JSON estruturado (inicializado automaticamente com o seed da Gestão LEC caso ainda não exista):
    - `janela_meses`: `12` (recorte temporal padrão em meses para trás, além de todas as datas futuras agendadas)
    - `grades_epo`: lista de objetos `{ sigla, nome_especialidade, grd_seqs?, ativo }` (seed: `EPO, EPG, POO, OEP, POT, POF`)
    - `grades_preop`: lista de objetos `{ sigla, nome_especialidade, grd_seqs?, ativo }` (seed: `RIS, PPC, RCI, OHR, PPO`)
    - `grades_apa`: lista de objetos `{ sigla, nome_especialidade, grd_seqs?, ativo }` (seed: `ANE, TAN`)
    - `grupos_exames`: lista de objetos `{ id, nome, siglas_exames: [{ sigla, descricao }], ativo }` (seed: os 8 grupos elencados e validados pela Gestão LEC com suas respectivas siglas reais do `agh.ael_exames`).

## Risks / Trade-offs

- **[Risk] Consultas no AGHU com status `60 - EM ATENDIMENTO` que não foram finalizadas pelo profissional** → **Mitigação**: Exibir o rótulo claro `Realizado (Em Atendimento)` ou `Realizado` na Tabela 2.2/3.2 (e `Agendado (Aguardando Atendimento)` para `ret_seq = 20` na Tabela 1/3.1), garantindo que nenhum paciente atendido desapareça das tabelas por falta de clique em "Finalizar" no AGHU.
- **[Risk] Grande quantidade de siglas de Ressonância Magnética ou Laboratório no AGHU** → **Mitigação**: O agrupamento por `grupos_exames` permite associar múltiplas siglas de `agh.ael_exames` a uma única coluna da Tabela 2.2 (ex.: coluna *Ressonância Magnética* ou *Laboratório*) e pesquisar/editar essas siglas a qualquer momento pela interface da Gestão LEC.
