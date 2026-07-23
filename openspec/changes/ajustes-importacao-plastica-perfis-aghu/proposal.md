## Why

Após a importação inicial das planilhas da especialidade de Cirurgia Plástica, foram identificados 3 ajustes necessários no sistema:
1. Duplicidade no cadastro de perfis para a especialidade Plástica.
2. Divergência na contagem do total de procedimentos na tela de Pacientes.
3. Ausência das informações cadastrais reais dos pacientes (nome, data de nascimento, nome da mãe), que devem ser buscadas no banco PostgreSQL do AGHU através do prontuário.

## What Changes

- **Limpeza de Perfis:** Remover a duplicidade de perfis da especialidade Plástica na tabela `perfis` do SQLite, mantendo um único registro padronizado.
- **Correção da Contagem de Procedimentos:** Ajustar a lógica/consulta de contagem no backend/frontend da tela de Pacientes para refletir com precisão a quantidade total de procedimentos e solicitações importadas.
- **Enriquecimento Cadastral via AGHU:** Atualizar a integração com o AGHU (PostgreSQL) para consultar os dados do paciente pelo número do prontuário (`codigo`) e popular/exibir o nome completo, data de nascimento, nome da mãe, CPF e sexo na listagem de Pacientes.

## Capabilities

### New Capabilities
- `ajustes-importacao-plastica-perfis-aghu`: Correção de duplicidade de perfis, ajuste nos contadores da tela de Pacientes e integração com AGHU para dados cadastrais dos pacientes.

### Modified Capabilities
- Nenhuma alteração em especificações existentes.

## Impact

- **Banco SQLite local (`data/app.db`):** Tabela `perfis`, `pacientes` e `solicitacoes`.
- **Backend FastAPI (`src/routers/paciente.py`, `src/providers/`):** Consulta ao PostgreSQL do AGHU para resgate dos dados do paciente pelo prontuário.
- **Frontend Vue (`frontend/src/views/Pacientes.vue`, `Perfis.vue`):** Exibição correta dos nomes reais dos pacientes, dados pessoais e contadores de solicitações.
