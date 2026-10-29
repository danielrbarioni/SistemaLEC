# Tasks

## 1. Normalização e Validação de Duplicidade no Backend

- [x] 1.1 Adicionar a função `normalizar_nome_base_procedimento(proc: str | None) -> str` em `src/helpers/string_helper.py` para extrair o nome base canônico do procedimento (sem prefixos/sufixos de ID, acentos ou diferenças de caixa) e verificar com asserções em Python.
- [x] 1.2 Atualizar `src/controllers/solicitacao_controller.py` criando a rotina de verificação de procedimentos ativos do paciente (cruzando `solics_paciente` aprovadas e `paciente_provider.listar_pacientes()`) e de solicitações pendentes reais (`evento_tipo` de solicitação principal), bloqueando com HTTP 400 e mensagem clara em `criar_solicitacao` e `editar_solicitacao` para os 4 casos (`INSERIR`, `EDITAR`, `STANDBY`/`CANCELAR_STANDBY` e `EXCLUIR`), verificando com testes automatizados em Python.

## 2. Validação Preventiva e Mensagens de Erro no Frontend (`Solicitações LEC`)

- [x] 2.1 Atualizar `frontend/src/views/InteracoesLec.vue` para importar `extrairNomeBaseProcedimento` e carregar a base de pacientes (`pacientesBase`) a fim de validar a dupla `paciente + procedimento` no envio (`enviarSolicitacao`) para `INSERIR` (contra `Pacientes` e solicitações `INSERIR` pendentes), `EDITAR` (contra solicitações `EDITAR` pendentes e conflito de novo procedimento), `STANDBY` (contra solicitações `STANDBY` pendentes) e `EXCLUIR` (contra solicitações `EXCLUIR` pendentes), exibindo mensagem de erro clara via `toast.error`.
- [x] 2.2 Compilar o frontend (`npm run build` em `frontend/`) garantindo ausência de erros de compilação TypeScript/Vue e atualização do bundle em `src/static/dist`.
