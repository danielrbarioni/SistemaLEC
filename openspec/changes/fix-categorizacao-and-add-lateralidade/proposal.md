## Why

Durante a utilização prática da funcionalidade de categorização profissional e edição de procedimentos, foram identificados dois problemas críticos:
1. Em pacientes com múltiplos procedimentos na mesma especialidade (com cirurgiões diferentes), a solicitação de edição de um procedimento específico estava comparando os dados com o procedimento errado do paciente, gerando diffs incorretos (ex.: acusando falsa alteração de cirurgião).
2. Ao solicitar e aprovar a categorização de um procedimento, a nova edição do mesmo procedimento não carregava a categoria aprovada no formulário de edição, retornando indevidamente para "Sem categorização".

Adicionalmente, o sistema necessita de um novo campo obrigatório para procedimentos cirúrgicos: **Lateralidade** (`lado esquerdo`, `lado direito`, `bilateral`, `não se aplica`), garantindo rastreabilidade cirúrgica sem quebrar a base legada (que deve receber o valor `"Indefinida"`).

## What Changes

- **Correção da Seleção e Baseline de Procedimento em Edição**: O fluxo de edição no formulário e no diff de aprovação agora correlaciona o procedimento específico exato por chave composta/identificador único (procedimento + médico responsável + lateralidade/especialidade), eliminando comparações cruzadas indevidas em pacientes com mais de um procedimento.
- **Carregamento Consistente de Categorização na Edição**: Ao abrir a modal/formulário de edição de um procedimento que já possui categorização aprovada, o formulário inicializa e seleciona a categoria ativa do procedimento em vez de "sem categorização".
- **Novo Campo Obrigatório "Lateralidade"**:
  - Adicionado no banco de dados (`pacientes` e `solicitacoes`), providers e modelos.
  - Procedimentos legados existentes recebem o valor padrão `"Indefinida"`.
  - Formulários de **Inclusão** (`INSERIR`) e **Edição** (`EDITAR`) exigem a seleção de uma das 4 opções: `lado esquerdo`, `lado direito`, `bilateral` ou `não se aplica`.
  - Em edições, a lateralidade atual do procedimento é carregada automaticamente no campo do formulário.
  - A lateralidade é exibida no card de procedimento (telas de Pacientes, Solicitações LEC e Histórico).

## Capabilities

### New Capabilities
- `lateralidade-procedimento`: Gerenciamento e obrigatoriedade do campo Lateralidade Cirúrgica em solicitações de inclusão e edição de procedimentos, com opções padronizadas e valor `"Indefinida"` para registros legados.
- `correcao-edicao-categorizacao-e-procedimento`: Identificação precisa do procedimento em edição para múltiplos procedimentos do mesmo paciente e carregamento fiel da categorização aprovada na reedição.

### Modified Capabilities
<!-- Nenhuma especificação de alto nível existente teve requisitos alterados -->

## Impact

- **Modelos e Banco de Dados**: Adição da coluna `lateralidade` nas tabelas `pacientes` e `solicitacoes` do SQLite com default `"Indefinida"`.
- **Backend**: Atualização dos schemas Pydantic, rotas de solicitação, aprovação e helpers de diff para incluir `lateralidade`.
- **Frontend**: Atualização de `InteracoesLec.vue`, `Pacientes.vue`, `Historico.vue` e stores para validação obrigatória, carregamento de estado no formulário de edição e exibição visual do badge/informação de lateralidade nos cards e tabelas.
