## Context

Na aba de Solicitação de Inclusão (`INSERIR`), o sistema realiza a busca do prontuário no AGHU. Quando o prontuário não é localizado no AGHU, a regra anterior bloqueava terminantemente a criação da solicitação.

O usuário solicitou que seja permitido prosseguir com a solicitação mesmo para prontuários não identificados no AGHU, contanto que:
1. O usuário receba uma pergunta de confirmação clara:
   `"Número de prontuário não identificado no AGHU. Deseja continuar com a solicitação de inclusão desse prontuário mesmo assim?"`
2. Tenha duas opções:
   - **"Inserir novo prontuário"**: apaga o número digitado e reinicia o processo.
   - **"Continuar"**: prossegue com o prontuário, atribuindo ao nome do paciente `'Prontuário <x> não identificado no AGHU'`.
3. Essa lógica é restrita à aba de Inclusão (as abas de Edição, Standby e Exclusão operam sobre pacientes já cadastrados no próprio banco do sistema).

## Goals / Non-Goals

**Goals:**
- Criar diálogo de confirmação interativo no frontend (`InteracoesLec.vue`) ao não encontrar o prontuário no AGHU na aba `INSERIR`.
- Ao escolher "Inserir novo prontuário", limpar o campo e o formulário.
- Ao escolher "Continuar", atribuir o nome `'Prontuário <x> não identificado no AGHU'`, liberar o formulário e habilitar o botão de envio.
- Ajustar o backend em `solicitacao_controller.py` para aceitar a criação da solicitação quando o nome seguir o padrão de prontuário não identificado no AGHU.
- Manter o comportamento das demais abas intacto.
- Nenhuma alteração estrutural no banco de dados.

**Non-Goals:**
- Não aplicar a confirmação nas abas de Edição, Standby e Exclusão (que dependem de pacientes já existentes no Sistema LEC).

## Decisions

1. **Estado do Modal no Frontend (`InteracoesLec.vue`)**:
   - `modalConfirmacaoProntuarioNaoLocalizado = ref({ aberto: false, prontuario: '' })`.
   - Ao capturar o erro 404 na busca do AGHU da aba `INSERIR`:
     - Abrir o modal com o número do prontuário digitado.
2. **Ações do Modal**:
   - `confirmarInserirNovoProntuario()`: fecha o modal, limpa `form.codigo_paciente` e executa `limparFormulario()`.
   - `confirmarContinuarSemAghu()`: fecha o modal, define `form.nome_paciente = \`Prontuário \${form.codigo_paciente} não identificado no AGHU\`` e marca `pacienteValidadoNoAghu = true`.
3. **Backend (`solicitacao_controller.py`)**:
   - No método `criar_solicitacao` e `editar_solicitacao`, caso `tipo == "INSERIR"` e o AGHU retorne 404:
     - Se `nome_paciente` estiver preenchido (ex: `Prontuário ... não identificado no AGHU` ou similar), permitir a solicitação.
     - Bloquear apenas se o nome for vazio.
