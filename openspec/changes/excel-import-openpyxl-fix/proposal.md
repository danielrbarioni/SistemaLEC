## Why

Ao tentar importar planilhas de pacientes (.xlsx) no menu **Pacientes**, o backend retornou a seguinte mensagem de erro de exceção para os usuários:
> *"Não foi possível interpretar o arquivo Excel enviado. Certifique-se de que é uma planilha Excel (.xlsx ou .xls) válida. (Erro: Missing optional dependency 'openpyxl'. Use pip or conda to install openpyxl.)"*

A falha ocorre porque a biblioteca `pandas` depende do pacote `openpyxl` para efetuar a leitura de arquivos Excel modernos no formato `.xlsx` (e `xlrd` para `.xls` legados). Como o `openpyxl` não constava explicitamente no arquivo [`requirements.txt`](file:///c:/Users/daniel.barioni/.gemini/antigravity-ide/scratch/Antigravity%20IDE/Sistema%20LEC/requirements.txt), o ambiente de execução não dispunha do módulo necessário para ler as planilhas das especialidades.

## What Changes

1. **Inclusão de Dependências de Planilhas:**
   - Adicionar `openpyxl` e `xlrd` explicitamente em [`requirements.txt`](file:///c:/Users/daniel.barioni/.gemini/antigravity-ide/scratch/Antigravity%20IDE/Sistema%20LEC/requirements.txt) para garantir que qualquer instalação do backend (local ou na VM de produção) possua os motores de leitura de arquivos `.xlsx` e `.xls`.
   - Instalar `openpyxl` e `xlrd` no ambiente virtual (`.venv`).

2. **Resiliência e Tratamento no Helper de Importação:**
   - Atualizar [`src/helpers/excel_import_helper.py`](file:///c:/Users/daniel.barioni/.gemini/antigravity-ide/scratch/Antigravity%20IDE/Sistema%20LEC/src/helpers/excel_import_helper.py) para utilizar detecção e tentativa automática com `engine='openpyxl'` e fallback para `engine='xlrd'`.
   - Garantir mensagens de erro claras e amigáveis caso ocorram problemas de formato na planilha enviada pelo usuário.

3. **Validação e Testes com Planilhas Reais:**
   - Executar testes automatizados de importação com as planilhas existentes em `data/` (ex: `data/Fila sistema Sede Plástica.xlsx`), validando a integridade dos dados, criação/atualização de pacientes e vinculação às especialidades.

## Capabilities

### New Capabilities
- Capacidade de carregar, interpretar e processar planilhas Excel `.xlsx` e `.xls` sem falhas de dependência ausente.

### Modified Capabilities
- `excel_import_helper.py`: leitura de streams de bytes de arquivos Excel suportando múltiplos motores (`openpyxl` e `xlrd`) com tratamento de exceções robusto.

## Impact

- **Ambiente de Produção (VM) e Local:** A importação de planilhas de pacientes por especialidade funcionará de forma imediata e transparente.
- **Integridade dos Dados:** Preservação integral da lógica de não-duplicação de pacientes e registros cirúrgicos já cadastrados.
