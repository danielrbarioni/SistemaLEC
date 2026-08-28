## Why

Na aba de Inclusão (`INSERIR`), os dados do paciente são buscados no AGHU. Caso um número de prontuário não seja localizado na base do AGHU (ex: prontuários recém-criados, contingências ou pacientes sem sincronização no momento), o usuário ainda deve ter a opção de prosseguir com a solicitação de inclusão, mediante confirmação explícita.

Essa alteração implementa um fluxo de confirmação amigável e seguro, que pergunta ao usuário se ele deseja tentar outro número ou prosseguir mesmo sem localização no AGHU, atribuindo ao nome do paciente a descrição padronizada `'Prontuário <x> não identificado no AGHU'`.

## What Changes

- **Diálogo de Confirmação na Busca (Aba Inclusão)**: Ao buscar um prontuário na aba `INSERIR` e não localizá-lo no AGHU (404), exibir o modal de confirmação:
  - *Mensagem*: `"Número de prontuário não identificado no AGHU. Deseja continuar com a solicitação de inclusão desse prontuário mesmo assim?"`
  - *Opção 1 ("Inserir novo prontuário")*: Limpa o campo do prontuário e o formulário, permitindo que o usuário digite um novo número.
  - *Opção 2 ("Continuar")*: Mantém o prontuário, preenche o nome do paciente automaticamente como `'Prontuário <x> não identificado no AGHU'` e habilita a continuação da solicitação.
- **Backend**: Ajustar a validação em `solicitacao_controller.py` para aceitar solicitações de inclusão com a identificação padronizada `'Prontuário <x> não identificado no AGHU'` quando o prontuário não for encontrado no AGHU.
- **Escopo Exclusivo para Inclusão**: As abas de Edição, Standby e Exclusão continuam buscando exclusivamente pacientes cadastrados no banco do Sistema LEC.
- **Preservação do Banco da VM**: Nenhuma alteração estrutural no banco de dados.

## Capabilities

### New Capabilities
- `confirmacao-inclusao-prontuario-nao-localizado-aghu`: Confirmação com o usuário para prosseguir ou reiniciar ao buscar prontuário não localizado no AGHU na aba de Inclusão.

## Impact

- **Backend**: `src/controllers/solicitacao_controller.py`, `src/routers/solicitacao.py`.
- **Frontend**: `frontend/src/views/InteracoesLec.vue`.
