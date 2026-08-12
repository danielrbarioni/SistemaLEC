## ADDED Requirements

### Requirement: Captura e Upload Estável de Planilha Excel via Interface
O sistema DEVE permitir a seleção e o arraste de planilhas Excel (.xlsx ou .xls) na interface web sem oscilações de drag-and-drop e sem redirecionamentos incorretos de método HTTP.

#### Scenario: Arraste de arquivo para a zona de soltura
- **WHEN** o usuário arrasta um arquivo Excel sobre a área de soltura do modal de importação
- **THEN** a interface DEVE manter o destaque visual da zona de soltura de forma estável até o soltar do arquivo, capturando o arquivo selecionado sem abrir o documento na página.

#### Scenario: Envio e upload de arquivo Excel via formulário POST
- **WHEN** o usuário confirma a importação enviando o arquivo para o endpoint `/api/pacientes/importar-excel` ou `/api/pacientes/importar-excel/`
- **THEN** o backend DEVE processar a requisição `POST` diretamente sem redirecionamento 307/308 nem erro 405 Method Not Allowed, retornando o resumo do processamento.
