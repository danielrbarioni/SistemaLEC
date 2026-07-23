## Why

O hospital precisa importar os dados legados de pacientes e procedimentos da especialidade de Cirurgia Plástica que já foram cadastrados no sistema da Sede. Isso permitirá que a equipe de Gestão LEC e os médicos de Plástica tenham acesso aos registros consolidados no sistema local.

## What Changes

- Criar um script de migração em Python (`scratch/import_planilhas_plastica.py`) para ler e cruzar as duas planilhas Excel disponibilizadas na pasta `data/`:
  - `Fila sistema Sede Plástica.xlsx` (Contém prontuário, ID do procedimento, médico responsável, swalis, se é judicializado, data de indicação).
  - `Procedimentos Plástica.xlsx` (Mapeia `id_procedimento` para a descrição textual do procedimento).
- Garantir a presença do perfil `PLÁSTICA` na tabela `perfis`.
- Popular as tabelas `pacientes` e `solicitacoes` do banco SQLite local (`data/app.db`) com os registros vinculados à especialidade Plástica.

## Capabilities

### New Capabilities
- `importacao-planilhas-plastica`: Importação e vinculação dos dados legados da especialidade Plástica (Sede) para o banco de dados do Sistema LEC.

### Modified Capabilities
- Nenhuma alteração em especificações existentes.

## Impact

- Banco de dados SQLite local (`data/app.db`): Popular tabelas `perfis`, `pacientes` e `solicitacoes`.
- Frontend: Exibição imediata dos pacientes e procedimentos importados nas telas de **Pacientes**, **Sistema LEC** e **Histórico**.
