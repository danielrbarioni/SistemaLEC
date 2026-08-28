## 1. Backend: Correção nos Provedores de Pacientes

- [x] 1.1 Remover fallback para paciente fictício em `PacienteSqliteProvider.obter_paciente_por_codigo`, retornando HTTP 404 quando o paciente não existir.
- [x] 1.2 Ajustar `HybridPacienteProvider.obter_paciente_por_codigo` para não mascarar 404 do AGHU e garantir que pacientes inexistentes retornem 404.

## 2. Backend: Validação de Existência na Criação de Solicitações

- [x] 2.1 Injetar o provedor de pacientes em `src/routers/solicitacao.py` e repassar para `solicitacao_controller.criar_solicitacao`.
- [x] 2.2 Implementar validação obrigatória de existência do prontuário no AGHU/base de pacientes quando `tipo == "INSERIR"`.
- [x] 2.3 Bloquear no backend `nome_paciente` vazio ou com formato fictício (`Paciente #`), retornando HTTP 400 Bad Request.

## 3. Frontend: Validação Reativa e UX no Formulário de Inclusão

- [x] 3.1 Adicionar controle de estado de validação (`pacienteValidadoNoAghu`) em `InteracoesLec.vue`.
- [x] 3.2 Limpar dados cadastrais (nome, nascimento, mãe) e invalidar a busca anterior ao modificar o campo de prontuário.
- [x] 3.3 Bloquear o envio da solicitação na aba `INSERIR` caso o prontuário não tenha sido previamente localizado no AGHU, exibindo toast de orientação.

## 4. Testes e Verificação

- [x] 4.1 Validar que a API `/api/pacientes/{codigo}` retorna 404 para prontuários inexistentes sem dados fictícios.
- [x] 4.2 Validar que a API `POST /api/solicitacoes` rejeita prontuários inexistentes no tipo `INSERIR`.
- [x] 4.3 Validar que o frontend orienta o usuário e impede submissão sem busca prévia válida.
