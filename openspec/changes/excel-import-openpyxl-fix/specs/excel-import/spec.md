## ADDED Requirements

### Requirement: Suporte Nativo a Planilhas Excel (.xlsx e .xls)
O sistema SHALL suportar a importação de planilhas nos formatos `.xlsx` e `.xls` através da presença mandatória dos pacotes `openpyxl` e `xlrd` no ambiente de execução Python.

#### Scenario: Importação com Sucesso de Planilha XLSX
- **GIVEN** que o usuário envia um arquivo de planilha no formato `.xlsx` com a fila de pacientes de uma especialidade
- **WHEN** o endpoint `POST /api/pacientes/importar-excel` processa o arquivo
- **THEN** o sistema SHALL ler as linhas e colunas utilizando o motor `openpyxl` sem erros de dependência ausente
- **AND** SHALL retornar o resumo de pacientes criados/atualizados com código HTTP 200.

#### Scenario: Tratamento de Arquivo Não Reconhecido
- **GIVEN** que o usuário envia um arquivo corrompido ou de formato binário não suportado
- **WHEN** os motores de leitura do Excel falharem
- **THEN** o sistema SHALL retornar HTTP 400 com mensagem amigável indicando a necessidade de uma planilha Excel válida.
