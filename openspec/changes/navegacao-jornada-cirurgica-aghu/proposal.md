# Proposal

## Why

O menu **Navegação** (`NavegacaoLec.vue`) precisa evoluir de um protótipo estático para um painel funcional de acompanhamento da **Jornada Cirúrgica do Paciente no HC-UFPE**, alimentado diretamente (e exclusivamente em modo leitura) pelo banco de dados do **AGHU (`dbaghu`)**, sem depender da tabela local `Pacientes` nem do Sistema LEC. Isso permitirá acompanhar os estágios reais do paciente no circuito pré-operatório (Consultas de Enfermagem EPO, Exames e Consultas Pré-Operatórias, e Avaliação Pré-Anestésica APA), localizar em qual(is) estágio(s) um prontuário específico se encontra, e permitir que a Gestão LEC visualize e edite dinamicamente quais grades de consultas e exames compõem o circuito cirúrgico.

## What Changes

- **1. Visibilidade Restrita ao Perfil ADMIN**:
  - Manter o menu **Navegação** visível exclusivamente para o perfil `ADMIN`, removendo o modal bloqueante *"Funcionalidade em desenvolvimento"* para permitir o uso completo pelo `ADMIN`.
- **2. Cinco Painéis/Tabelas da Jornada Cirúrgica (Alimentados Diretamente pelo AGHU)**:
  - **Tabela 1 — Pacientes com consulta de enfermagem (EPO) agendada**:
    - Filtro automático: consulta mais recente por `(Prontuário + Grade EPO)` nas grades EPO configuradas (padrão inicial: `EPO`, `EPG`, `POO`, `OEP`, `POT`, `POF`), com status `Agendado` (`ret_seq = 9 - PACIENTE AGENDADO` ou `20 - AGUARDANDO ATENDIMENTO`).
    - Ordenação: da data de consulta EPO mais antiga para a mais recente.
  - **Tabela 2.1 — Pacientes com consulta de enfermagem (EPO) faltosa**:
    - Filtro automático: consulta mais recente por `(Prontuário + Grade EPO)` nas grades EPO configuradas, com status de falta (`ret_seq = 40 - PACIENTE FALTOU`, `30 - PROFISSIONAL FALTOU` ou `50 - PACIENTE DESISTIU CONS`).
    - Ordenação: da data de consulta EPO mais antiga para a mais recente.
  - **Tabela 2.2 — Pacientes com consulta de enfermagem (EPO) realizada + Circuito Pré-Operatório (Exames e Consultas Pré-Op)**:
    - Filtro automático: consulta mais recente por `(Prontuário + Grade EPO)` nas grades EPO configuradas, com status `Realizado` (`ret_seq = 10 - PACIENTE ATENDIDO` ou `60 - EM ATENDIMENTO`).
    - Colunas dinâmicas dos **Grupos de Exames Pré-Operatórios** configurados (padrão inicial: *Laboratório*, *Raio X*, *Espirometria*, *Ecocardiograma Transtorácico*, *Cintilografia Miocárdica*, *Ressonância Magnética*), exibindo para cada grupo a **Data** e o **Status** do exame mais recente `(Prontuário + Grupo de Exame)`.
    - Colunas dinâmicas das **Grades de Consultas Pré-Operatórias** solicitadas pela EPO configuradas (padrão inicial: `RIS` — Cardio Risco Cirúrgico e `PPC` — Pneumologia Parecer), exibindo para cada grade a **Data** e o **Status** da consulta mais recente `(Prontuário + Grade Pré-Op)`.
    - Ordenação: da data de consulta EPO mais antiga para a mais recente.
  - **Tabela 3.1 — Pacientes com avaliação pré-anestésica (APA) não realizada**:
    - Filtro automático: consulta mais recente por `(Prontuário + Grade APA)` nas grades de APA configuradas (padrão inicial: `ANE`), com status `Agendado`, `Falta do paciente` ou `Falta do profissional` (e filtro modificável para escolher entre esses status).
    - Ordenação: da data de APA mais antiga para a mais recente.
  - **Tabela 3.2 — Pacientes com avaliação pré-anestésica (APA) realizada**:
    - Filtro automático: consulta mais recente por `(Prontuário + Grade APA)` nas grades de APA configuradas (`ANE`), com status `Realizado` (`ret_seq = 10 - PACIENTE ATENDIDO`).
    - Ordenação: da data de APA **mais recente para a mais antiga**.
- **3. Busca Global por Prontuário / Paciente na Jornada Cirúrgica**:
  - Campo de busca global no topo da Navegação que localiza um paciente pelo prontuário (ou nome) e destaca em **qual(is) das 5 tabelas/estágios** ele se encontra simultaneamente (exibindo um resumo imediato de todas as suas passagens nas Tabelas 1, 2.1, 2.2, 3.1 e 3.2).
- **4. Gestão Dinâmica de Grades de Consultas e Exames do Circuito Cirúrgico (com Busca no AGHU)**:
  - Painel/Modal de configuração (acessível a `ADMIN` e `GESTAO_LEC`) que permite visualizar, adicionar, editar e ativar/desativar:
    - As siglas/grades de consulta de **Enfermagem Pré-Operatória (EPO)**;
    - As siglas/grades de **Consultas Pré-Operatórias** (ex.: `RIS`, `PPC`);
    - As siglas/grades de **Avaliação Pré-Anestésica (APA)** (ex.: `ANE`, `TAN`);
    - Os **Grupos de Exames Pré-Operatórios** e as siglas de exames do AGHU (`agh.ael_exames`) associadas a cada grupo, com pesquisa ao vivo no catálogo do AGHU.

## Capabilities

### New Capabilities
- `navegacao-jornada-cirurgica-aghu`: Painéis da jornada cirúrgica alimentados diretamente pelo AGHU (Tabelas 1, 2.1, 2.2, 3.1 e 3.2), busca global de estágio por prontuário e gerenciamento dinâmico de grades de consultas e grupos de exames pré-operatórios com busca no AGHU.

### Modified Capabilities

## Impact

- **Backend**:
  - Novo modelo e tabela SQLite local `navegacao_config` (ou tabelas de configuração de grades e grupos de exames da navegação) inicializados com os valores padrão da Gestão LEC (`EPO, EPG, POO, OEP, POT, POF`, `RIS, PPC`, `ANE` e os 6 grupos de exames pré-operatórios).
  - Novo roteador `src/routers/navegacao.py` (`/api/navegacao/paineis`, `/api/navegacao/config`, `/api/navegacao/aghu/grades`, `/api/navegacao/aghu/exames`) com consultas otimizadas e cache com TTL sobre `agh.aac_consultas`, `agh.aac_grade_agendamen_consultas`, `agh.agh_especialidades`, `agh.aac_retornos`, `agh.ael_solicitacao_exames`, `agh.ael_item_solicitacao_exames` e `agh.ael_exames`.
- **Frontend**:
  - `frontend/src/views/NavegacaoLec.vue`: implementação das 5 tabelas/estágios com seus filtros automáticos e modificáveis, busca global de paciente por prontuário mostrando todos os estágios em que ele consta, e modal de configuração de grades e exames com busca ao vivo no AGHU.
