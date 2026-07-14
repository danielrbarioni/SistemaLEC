## Why

Para melhor identificação e segurança do paciente na tela do Sistema LEC, ao buscar um prontuário, o sistema deve exibir também a Data de Nascimento e o Nome da Mãe do paciente cadastrado no AGHU. Esses campos devem aparecer logo abaixo do número do prontuário e do nome.

## What Changes

- **Frontend**:
  - Adicionar os campos "Data de Nascimento" e "Nome da Mãe" (somente leitura) no formulário do Sistema LEC, logo abaixo do Prontuário/Nome.
  - Atualizar o método de busca de dados do paciente para popular esses novos campos a partir da API.
  - Limpar esses campos ao limpar o formulário.

## Capabilities

### New Capabilities
- Nenhuma

### Modified Capabilities
- `interacoes-lec`: Exibição de dados demográficos adicionais (Data de Nascimento e Nome da Mãe).

## Impact

- **Frontend**: `InteracoesLec.vue` layout e comportamento.
