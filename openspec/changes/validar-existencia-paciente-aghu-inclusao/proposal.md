## Why

Atualmente, na aba "Solicitar Inclusão" do módulo de Solicitações LEC, é possível enviar solicitações de inclusão de procedimento cirúrgico para prontuários inexistentes no AGHU. Isso ocorre porque o provedor SQLite retornava um objeto mock com nome fictício (`Paciente #<codigo>`) quando o paciente não era encontrado, os erros 404 do AGHU eram mascarados pelo fallback, o frontend permitia submissão sem validação prévia e o backend não bloqueava a criação de solicitações para prontuários não cadastrados no AGHU.

Esta mudança é necessária para garantir a integridade dos dados clínicos e impedir que solicitações inválidas entrem no fluxo de regulação cirúrgica da LEC.

## What Changes

- **Correção no Provedor SQLite**: Remover a geração de pacientes fictícios (`Paciente #<codigo>`) em `PacienteSqliteProvider.obter_paciente_por_codigo`, retornando erro HTTP 404 quando o paciente não existir.
- **Tratamento de 404 no Provedor Híbrido**: Em `HybridPacienteProvider.obter_paciente_por_codigo`, diferenciar erro de conexão (fallback para SQLite) de paciente não encontrado (HTTP 404), não retornando dados fictícios.
- **Validação de Inclusão no Backend**: No `solicitacao_controller.criar_solicitacao` para o tipo `INSERIR`, verificar a existência real do paciente no AGHU/base de pacientes e validar que o `nome_paciente` não está vazio nem é um placeholder fictício, rejeitando prontuários inexistentes com HTTP 400/404.
- **Validação de Prontuário no Frontend**: Na aba "Solicitar Inclusão" de `InteracoesLec.vue`, garantir que a busca no AGHU tenha sido realizada com sucesso antes de permitir o envio, limpar os dados do paciente caso o usuário altere o número do prontuário, e bloquear o botão de envio se o paciente não foi localizado no AGHU.
- **Garantia de Não Alteração no Banco da VM**: Todas as mudanças são implementadas exclusivamente na camada de aplicação (código Python/FastAPI e Vue 3), sem modificações estruturais ou escrita indevida no banco de dados da VM.

## Capabilities

### New Capabilities
- `validacao-inclusao-aghu`: Validação obrigatória da existência prévia do paciente no AGHU (Cadastro de Pacientes) antes de permitir a criação de solicitações de inclusão de procedimento, tanto no frontend quanto no backend.

### Modified Capabilities
- `patient-autofetch`: Alteração no comportamento de busca para nunca retornar registros fictícios quando o prontuário não for encontrado em nenhum repositório cadastral, retornando 404 e limpando o formulário.

## Impact

- **Backend**: `src/controllers/solicitacao_controller.py`, `src/routers/solicitacao.py`, `src/providers/implementations/paciente_sqlite_provider.py`, `src/providers/implementations/paciente_hybrid_provider.py`.
- **Frontend**: `frontend/src/views/InteracoesLec.vue`.
- **APIs**: `/api/pacientes/{codigo}` e `POST /api/solicitacoes`.
- **Banco de Dados**: Nenhum esquema, migration ou dado no banco da VM é alterado.
