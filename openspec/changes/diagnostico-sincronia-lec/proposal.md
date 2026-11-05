# Proposal

## Why

As especialidades cirúrgicas registram solicitações de inclusão, exclusão, edição e standby no **Comunicação Cirúrgica**, que após aprovação pela Gestão LEC devem se refletir no **Sistema LEC**. Como os dois sistemas não possuem integração direta via banco de dados, divergências operacionais e cadastrais acumulam-se ao longo do tempo (ex.: exclusões aprovadas no Comunicação Cirúrgica ainda não baixadas no Sistema LEC, pacientes que saíram do Sistema LEC e permanecem ativos no Comunicação Cirúrgica, inclusões feitas diretamente no Sistema LEC, pacientes em especialidades distintas entre os dois sistemas ou divergências em Swalis, médico responsável, lateralidade e judicialização). É necessária uma ferramenta integrada na tela de **Pacientes**, exclusiva para os perfis **Administrador** e **Gestão LEC**, que mantenha o histórico de diagnósticos realizados, compare as planilhas exportadas do Sistema LEC com a base ativa do Comunicação Cirúrgica, permita visualizar e filtrar todas as pendências diretamente na tela e ofereça ações auditáveis de sincronização e correção manual no banco do Comunicação Cirúrgica, registrando todas as mudanças no menu **Histórico** com origem `Pacientes`.

## What Changes

- **Novo botão `"Diagnóstico Comunicação Cirúrgica x Sistema LEC"`** no cabeçalho da tela de **Pacientes** ([`Pacientes.vue`](file:///c:/Users/daniel.barioni/Comunicação%20Cirúrgica/frontend/src/views/Pacientes.vue)), posicionado ao lado do botão `"Importar Planilha"` e restrito exclusivamente aos perfis **Administrador** (`ADMIN`) e **Gestão LEC** (`GESTAO_LEC`).
- **Histórico de Diagnósticos Realizados e Opção `"Novo Diagnóstico"`**:
  - Ao clicar no botão `"Diagnóstico Comunicação Cirúrgica x Sistema LEC"`, o modal exibe a **lista de diagnósticos já realizados**, ordenada da **data/hora mais recente para a mais antiga**, além do botão **`"Novo Diagnóstico"`**.
  - Diferentes usuários (`ADMIN` / `GESTAO_LEC`) podem abrir qualquer diagnóstico já armazenado para consultar informações ou executar ações sobre os itens pendentes, ficando cada ação registrada com o usuário específico que a executou.
- **Upload Flexível com Desduplicação e Verificação Preliminar de Cobertura de Especialidades**:
  - Suporta o envio de **1 planilha** (`.xlsx`/`.xls`), **múltiplas planilhas** simultâneas ou **1 arquivo `.zip`**.
  - Identificação automática da especialidade, **desduplicação automática** de arquivos repetidos e **Painel Preliminar de Cobertura de Especialidades** (informando quais especialidades tiveram planilha importada, quais não tiveram e quais não possuem fila ativa no CC).
- **Motor de Diagnóstico Automático e Visualização Completa na Tela do Comunicação Cirúrgica**:
  - Mantém o caso de **Especialidade diferente (`EM_OUTRA_ESPECIALIDADE_NO_CC`)** em aba própria separada (com ação de mudança de especialidade) e adiciona uma categoria dedicada para **Divergência de Informações (`DIVERGENCIA_DADOS_CADASTRAIS`)** nos pacientes presentes em ambos os sistemas, comparando **Swalis**, **Médico Responsável**, **Lateralidade** e **Judicialização** e indicando claramente o valor que está no **Comunicação Cirúrgica** e o valor que está no **Sistema LEC**:
    1. **Exclusão aprovada no CC pendente no LEC** (`EXCLUSAO_APROVADA_CC_PENDENTE_LEC`)
    2. **Inclusão aprovada no CC pendente no LEC** (`INCLUSAO_APROVADA_CC_PENDENTE_LEC`)
    3. **Em outra especialidade no CC** (`EM_OUTRA_ESPECIALIDADE_NO_CC`)
    4. **Divergência de informações (Swalis, Médico, Lateralidade, Judicialização)** (`DIVERGENCIA_DADOS_CADASTRAIS`) — avaliadas individualmente e corrigidas manualmente pelo usuário Gestão LEC.
    5. **Inserido direto no LEC (sem passagem pelo CC)** (`INSERIDO_DIRETO_NO_LEC`)
    6. **Saiu do LEC sem exclusão no CC** (`SAIU_DO_LEC_SEM_BAIXA_NO_CC`)
- **Ações de Sincronização e Correção Manual (Executadas Exclusivamente no CC e Registradas no Menu `Histórico`)**:
  - **Ação 1 — Incluir no Comunicação Cirúrgica (`INCLUIR_NO_CC`)**: cria a solicitação `INSERIR` aprovada (`origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"`, com o usuário que executou e explicação detalhada da origem no Diagnóstico LEC).
  - **Ação 2 — Excluir do Comunicação Cirúrgica (`EXCLUIR_DO_CC`)**: registra uma solicitação `EXCLUIR` aprovada (`origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"`) com o usuário que executou e justificativa detalhada no Histórico, removendo o procedimento ativo da lista de `Pacientes`.
  - **Ação 3 — Mudar Especialidade no Comunicação Cirúrgica (`TRANSFERIR_ESPECIALIDADE_NO_CC`)**: atualiza a especialidade ativa no CC e registra uma entrada no menu **Histórico** como **`tipo = "EDITAR"`**, **`evento_tipo = "EXECUCAO"`**, **`origem_menu = "Pacientes"`**, com o usuário executor e detalhes no padrão `Especialidade: <antiga> -> <nova> | Justificativa: ...`.
  - **Ação 4 — Avaliar e Corrigir Manualmente Informações Divergentes no CC (`EDITAR_INFORMACOES_NO_CC`)**: para a aba de divergências de Swalis, Médico Responsável, Lateralidade e Judicialização, o usuário avalia **individualmente** cada paciente, edita manualmente os campos que deseja atualizar no CC (vendo lado a lado o valor atual no CC e o valor no Sistema LEC) e confirma; a alteração atualiza o procedimento ativo no CC e gera um registro no menu **Histórico** como **`tipo = "EDITAR"`**, **`evento_tipo = "EXECUCAO"`**, **`origem_menu = "Pacientes"`**, com o usuário que executou e o detalhamento exato dos campos alterados (`Campo: valor_antigo -> valor_novo`).

## Capabilities

### New Capabilities
- `diagnostico-sincronia-lec`: Histórico persistido de diagnósticos realizados, upload múltiplo/ZIP com verificação preliminar de cobertura de especialidades, classificação automática de divergências de presença, de especialidade e de dados clínicos/cadastrais (Swalis, médico responsável, lateralidade e judicialização), correção manual individual de dados divergentes e ações de sincronização no Comunicação Cirúrgica com registro completo no menu Histórico (`origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"`).

### Modified Capabilities
<!-- Nenhuma capability existente teve seus requisitos alterados. -->

## Impact

- **Backend (`src/helpers/lec_diagnostico_helper.py`, `src/routers/paciente.py`)**:
  - Leitura das colunas `SWALIS`, `Médico responsável`, `Lateralidade` e `Judicializado` das planilhas do Sistema LEC e comparação com os dados ativos do paciente no CC para gerar os itens `DIVERGENCIA_DADOS_CADASTRAIS` com a lista estruturada de campos divergentes (`campo`, `valor_cc`, `valor_lec`).
  - Ação `EXCLUIR_DO_CC` (substituindo o rótulo "Dar Baixa no CC") e ação individual `EDITAR_INFORMACOES_NO_CC` (recebendo os valores escolhidos manualmente pelo gestor para `swalis`, `medico_responsavel`, `lateralidade` e `judicializado`).
  - Todos os registros gerados pelas ações do diagnóstico gravam `origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"`, `usuario = usuario_executor` e `detalhes` explicativos, sendo que mudanças de especialidade ou de informações entram como `tipo = "EDITAR"` e `evento_tipo = "EXECUCAO"`.
- **Frontend (`frontend/src/components/DiagnosticoSincroniaLecModal.vue`, `frontend/src/services/pacienteService.ts`)**:
  - Nova aba **🟡 Divergência de Informações (Swalis, Médico, Lateralidade, Judicialização)** exibindo lado a lado o que está no CC e o que está no Sistema LEC, sem ação em lote, e com modal/painel de avaliação e correção manual individual.
  - Botões renomeados para **`"Excluir do CC"`** / **`"Excluir do Comunicação Cirúrgica"`**.
