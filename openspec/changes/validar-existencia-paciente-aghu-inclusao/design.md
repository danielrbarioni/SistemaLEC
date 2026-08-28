## Context

No Sistema LEC, a aba **Solicitar Inclusão** (`INSERIR`) é responsável por registrar solicitações de inclusão cirúrgica de pacientes que obrigatoriamente existem no cadastro do AGHU. As outras abas (**Edição**, **Standby**, **Exclusão**) operam sobre pacientes e procedimentos já previamente incluídos no Sistema LEC.

Identificou-se que solicitações de inclusão foram permitidas para prontuários inexistentes devido a:
1. `PacienteSqliteProvider` gerando um registro mock (`Paciente #<codigo>`) em vez de lançar erro 404 quando o prontuário não existia.
2. `HybridPacienteProvider` tratando 404 como falha de conexão e caindo no provedor SQLite que entregava o registro mock.
3. Ausência de validação no controller de solicitações (`solicitacao_controller.py`) sobre a existência real do prontuário no AGHU e integridade do nome do paciente.
4. Ausência de bloqueio no frontend (`InteracoesLec.vue`) caso o usuário não tenha realizado a busca com sucesso ou alterado o prontuário após a busca.

## Goals / Non-Goals

**Goals:**
- Garantir que o endpoint `GET /api/pacientes/{codigo}` retorne estritamente erro `404 Not Found` quando um paciente não existir no AGHU ou na base local.
- Impedir que provedores de dados gerem registros ou nomes fictícios de pacientes.
- Adicionar validação no backend (`solicitacao_controller.criar_solicitacao`) para rejeitar solicitações de `INSERIR` caso o paciente não exista ou o nome seja inválido/fictício.
- Adicionar controle de estado e validação no frontend (`InteracoesLec.vue`) para que a solicitação de inclusão só possa ser enviada se o prontuário tiver sido buscado e validado no AGHU com sucesso.
- Garantir que qualquer alteração no campo de prontuário invalide imediatamente a busca anterior e limpe os campos dependentes (nome, data de nascimento, mãe).
- Respeitar a restrição de não alterar a estrutura ou dados do banco de dados na VM.

**Non-Goals:**
- Não alterar as regras das abas de Edição, Standby e Exclusão que já consultam a base de procedimentos do Sistema LEC.
- Não modificar o esquema ou tabelas do banco de dados na VM.

## Decisions

1. **Eliminação de Mock Data nos Provedores**:
   - `PacienteSqliteProvider.obter_paciente_por_codigo`: Lançar `HTTPException(status_code=404, detail="Paciente não encontrado")` quando `p` for `None`.
   - `HybridPacienteProvider.obter_paciente_por_codigo`: Propagar o 404 quando o paciente não existir no AGHU nem no SQLite local.

2. **Validação no Backend (`solicitacao_controller.py`)**:
   - No método `criar_solicitacao`, quando `tipo == "INSERIR"`, verificar se o prontuário é válido e obter a confirmação do paciente através do provedor de pacientes.
   - Validar que o `nome_paciente` recebido não está em branco e não possui o formato fictício `Paciente #`.
   - Se o paciente não for encontrado, retornar `HTTPException(status_code=400, detail="Paciente com prontuário ... não encontrado no AGHU (Cadastro de Pacientes). Não é possível solicitar inclusão para prontuário inexistente.")`.

3. **Validação e UX no Frontend (`InteracoesLec.vue`)**:
   - Criar uma variável reativa `pacienteValidadoNoAghu` (ou `prontuarioBuscadoComSucesso`).
   - Adicionar `watch` em `form.codigo_paciente` para que, ao digitar qualquer novo caractere, `pacienteValidadoNoAghu` seja definido como `false` e `form.nome_paciente`, `form.dt_nascimento`, `form.nome_mae` sejam resetados.
   - Em `enviarSolicitacao`: Se `abaAtiva === 'INSERIR'`, verificar se `pacienteValidadoNoAghu` é verdadeiro e se `form.nome_paciente` está preenchido. Caso contrário, exibir alerta toast e bloquear o envio.

## Risks / Trade-offs

- **[Risk]** Testes locais com provedor SQLite sem seed de pacientes podem falhar se tentarem prontuários aleatórios.
  → **Mitigation**: Os testes e ambiente de desenvolvimento já possuem pacientes no banco SQLite / seed para testes locais e mock de requisições.
- **[Risk]** Usuário tentar enviar formulário pressionando Enter no campo de prontuário sem clicar em "Buscar".
  → **Mitigation**: O frontend valida se a busca foi completada com sucesso antes de submeter e pode disparar a busca ou exibir a mensagem clara de orientação.
