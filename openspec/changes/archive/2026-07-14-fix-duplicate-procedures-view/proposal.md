## Why

Ao listar os pacientes na tela de Pacientes, o sistema exibe incorretamente um procedimento em branco ("Procedimento não informado") além do procedimento real do paciente. Isso ocorre porque o mapeamento inicial da lista de pacientes a partir da base (AGHU) não possui informações de procedimentos e injeta um procedimento nulo por padrão, que depois é complementado pelas solicitações aprovadas sem remover o nulo.

## What Changes

- **Frontend**:
  - Em `Pacientes.vue`, inicializar a lista de procedimentos de cada paciente como um array vazio (`[]`) ao ler os dados básicos do paciente, deixando que as solicitações aprovadas adicionem os procedimentos reais.

## Capabilities

### New Capabilities
- Nenhuma

### Modified Capabilities
- `pacientes-view`: Exibição limpa de procedimentos dos pacientes.

## Impact

- **Frontend**: `Pacientes.vue`
