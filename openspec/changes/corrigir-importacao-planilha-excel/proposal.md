## Why

Ao tentar importar planilhas Excel na tela de Pacientes do Sistema LEC, os usuários enfrentam dois problemas críticos de usabilidade e comunicação com a API:
1. O arrastar e soltar (drag & drop) não captura o arquivo adequadamente devido ao borbulhamento de eventos em nós filhos do HTML.
2. A seleção de arquivo retorna o erro "Method Not Allowed" (HTTP 405) devido a inconsistências de roteamento, ausência de suporte a barra final (`/`) na rota do FastAPI e falta de pré-configuração do middleware CORS.

## What Changes

- **Frontend (`ImportarPlanilhaPacientesModal.vue`)**:
  - Implementação de controle de contador de entrada (`dragCounter`) para impedir oscilações do estado de arrasto (`isDragging`).
  - Adição de `pointer-events-none` nos elementos visuais internos do componente de dropzone.
  - Tratamento preventivo nos eventos `@dragenter`, `@dragover`, `@dragleave` e `@drop` para evitar abertura indesejada de arquivos no navegador.
  - Exibição tratada para mensagens de erro HTTP 405.
- **Backend (`src/routers/paciente.py` & `src/main.py`)**:
  - Mapeamento duplo das rotas `@router.post("/importar-excel")` e `@router.post("/importar-excel/")` para garantir tratamento correto sem redirecionamento 307/308.
  - Adição do `CORSMiddleware` na aplicação FastAPI para responder adequadamente às requisições preflight `OPTIONS`.
  - Tratamento resiliente na leitura do Excel em `src/helpers/excel_import_helper.py` com fallback de engine `openpyxl` e retorno amigável de HTTP 400 em falhas de parsing.

## Capabilities

### New Capabilities
- `importacao-planilha-excel`: Garantia de suporte robusto a drag-and-drop e upload via formulário HTTP POST para planilhas Excel de pacientes sem erros HTTP 405 ou interrupções na interface.

### Modified Capabilities
*(nenhuma capacidade existente teve seus requisitos de negócio alterados)*

## Impact

- **Frontend**: Componente `ImportarPlanilhaPacientesModal.vue` e serviço `pacienteService.ts`.
- **Backend**: Roteador `src/routers/paciente.py`, aplicação principal `src/main.py` e helper `src/helpers/excel_import_helper.py`.
