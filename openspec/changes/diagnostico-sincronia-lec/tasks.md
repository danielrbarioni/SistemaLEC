# Tasks

## 1. Banco de Dados e Backend — Histórico de Diagnósticos, Motor de Comparação e Sincronização

- [x] 1.1 Criar o modelo `src/models/diagnostico_lec.py` (`DiagnosticoLec`) e adicionar a criação automática da tabela `diagnosticos_lec` em `src/helpers/database_migration_helper.py` e `src/main.py`, verificando que a tabela é criada na inicialização do backend.
- [x] 1.2 Atualizar `src/helpers/lec_diagnostico_helper.py` para ler `Lateralidade`, `SWALIS`, `Médico responsável` e `Judicializado` das planilhas do Sistema LEC, mantendo `EM_OUTRA_ESPECIALIDADE_NO_CC` separado e adicionando a categoria `DIVERGENCIA_DADOS_CADASTRAIS` com o detalhamento lado a lado (`valor_cc` vs `valor_lec`) para pacientes presentes em ambos os sistemas.
- [x] 1.3 Atualizar em `src/helpers/lec_diagnostico_helper.py` e `src/routers/paciente.py` o executor de ações (`INCLUIR_NO_CC`, `EXCLUIR_DO_CC`, `TRANSFERIR_ESPECIALIDADE_NO_CC` e `EDITAR_INFORMACOES_NO_CC` individual) para gravar todas as ações na tabela `solicitacoes` com `origem_menu = "Pacientes"`, `evento_tipo = "EXECUCAO"`, o usuário executor e detalhes estruturados (`Campo: valor_antigo -> valor_novo | Justificativa: ...`), registrando mudanças de especialidade e de informações como `tipo = "EDITAR"` do tipo `"EXECUCAO"`.

## 2. Frontend — Aba de Divergência de Informações, Correção Manual Individual e Ação Excluir do CC

- [x] 2.1 Atualizar `frontend/src/services/pacienteService.ts` com a categoria `DIVERGENCIA_DADOS_CADASTRAIS`, a interface `CampoDivergenteLec`, a ação `EXCLUIR_DO_CC` e o payload de edição manual individual `dados_edicao`.
- [x] 2.2 Atualizar `frontend/src/components/DiagnosticoSincroniaLecModal.vue` para: (a) renomear *"Dar Baixa no CC"* para **`"Excluir do CC"`** / **`"Excluir do Comunicação Cirúrgica"`**; (b) adicionar a aba **🟡 Divergência de Informações (Swalis, Médico, Lateralidade, Judicialização)** mostrando o que consta em cada sistema; (c) incluir o modal/painel de **Avaliação Individual e Correção Manual no CC** para que o usuário Gestão LEC edite manualmente as informações divergentes de cada paciente; e validar o build (`npm run build`).
