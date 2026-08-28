## 1. Backend: Ajuste na Validação de Inclusão

- [x] 1.1 Em `src/controllers/solicitacao_controller.py`, permitir solicitação do tipo `INSERIR` para prontuários não localizados no AGHU quando o `nome_paciente` estiver preenchido com a identificação informada (`Prontuário <x> não identificado no AGHU`).

## 2. Frontend: Diálogo de Confirmação e Fluxo na Aba de Inclusão

- [x] 2.1 Criar modal de confirmação no template de `InteracoesLec.vue` com a pergunta `"Número de prontuário não identificado no AGHU. Deseja continuar com a solicitação de inclusão desse prontuário mesmo assim?"` e os botões `"Inserir novo prontuário"` e `"Continuar"`.
- [x] 2.2 Ao não localizar o paciente no AGHU durante a busca na aba `INSERIR`, abrir o diálogo de confirmação em vez de bloquear o fluxo.
- [x] 2.3 Implementar a ação `"Inserir novo prontuário"`: fechar o modal, apagar o campo de prontuário e reiniciar o formulário.
- [x] 2.4 Implementar a ação `"Continuar"`: fechar o modal, definir o nome como `Prontuário <x> não identificado no AGHU` e habilitar o formulário para submissão.

## 3. Testes e Verificação

- [x] 3.1 Testar busca de prontuário inexistente no AGHU na aba `INSERIR` com a escolha de "Inserir novo prontuário" (verificar limpeza).
- [x] 3.2 Testar busca de prontuário inexistente no AGHU na aba `INSERIR` com a escolha de "Continuar" e envio bem-sucedido da solicitação.
- [x] 3.3 Validar que as demais abas (`EDITAR`, `STANDBY`, `EXCLUIR`) continuam operando exclusivamente sobre pacientes da base local.
