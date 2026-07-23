## 1. Script de Importação

- [x] 1.1 Criar script em Python `scratch/import_planilhas_plastica.py` para ler `data/Fila sistema Sede Plástica.xlsx` e `data/Procedimentos Plástica.xlsx`.
- [x] 1.2 Mapear e cruzar os campos `id_procedimento`, `prontuario`, `medico_responsavel`, `swalis`, `sin_judicializado` e `dth_indicacao`.
- [x] 1.3 Inserir o perfil `PLASTICA` na tabela `perfis` se não existir.
- [x] 1.4 Inserir pacientes e solicitações aprovadas no banco SQLite (`data/app.db`).

## 2. Validação

- [x] 2.1 Executar a migração dos dados e verificar os contadores no banco.
- [x] 2.2 Validar a exibição no frontend (menus Pacientes, Sistema LEC e Histórico).

