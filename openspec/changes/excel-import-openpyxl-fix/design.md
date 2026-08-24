## Context

O Sistema LEC possui um módulo de importação em lote de filas cirúrgicas a partir de planilhas Excel disponibilizadas pelas especialidades médicas (ex: Plástica, Ortopedia, Cirurgia Geral). A importação é realizada via upload de arquivo no frontend ([`ImportarPlanilhaPacientesModal.vue`](file:///c:/Users/daniel.barioni/.gemini/antigravity-ide/scratch/Antigravity%20IDE/Sistema%20LEC/frontend/src/components/ImportarPlanilhaPacientesModal.vue)), que envia um `multipart/form-data` para o endpoint `POST /api/pacientes/importar-excel`.

No backend, o método `process_excel_pacientes_import` em [`src/helpers/excel_import_helper.py`](file:///c:/Users/daniel.barioni/.gemini/antigravity-ide/scratch/Antigravity%20IDE/Sistema%20LEC/src/helpers/excel_import_helper.py) recebe os bytes do arquivo e utiliza a biblioteca `pandas` (`pd.read_excel`) para extrair os dados em formato tabular.

A biblioteca `pandas` em versões modernas (2.x+) não embute nativamente parsers de formatos binários/compactados como `.xlsx` e `.xls`, necessitando explicitamente dos pacotes `openpyxl` (para arquivos padrão XML/OpenXML `.xlsx`) e `xlrd` (para arquivos legados `.xls`).

## Goals / Non-Goals

### Goals
- Adicionar `openpyxl` e `xlrd` no arquivo de manifesto de dependências `requirements.txt`.
- Instalar as dependências no ambiente virtual (`.venv`).
- Reforçar o parser em `excel_import_helper.py` para tentar ordenadamente `openpyxl` e `xlrd`.
- Testar a importação de planilhas `.xlsx` reais garantindo funcionamento fim a fim.

### Non-Goals
- Não alterar as regras de negócio de reconciliação de pacientes (prontuário, nome, CRM médico, data de inclusão e status).

## Technical Details

### 1. Atualização do `requirements.txt`
```text
openpyxl>=3.1.2
xlrd>=2.0.1
```

### 2. Reforço no `src/helpers/excel_import_helper.py`
O stream de bytes será aberto tentando os seguintes engines em cascata:
1. `openpyxl` (padrão para `.xlsx` e `.xlsm`)
2. `xlrd` (padrão para `.xls` legado)
3. Tratamento de exceções específico com mensagens claras sobre colunas obrigatórias ou integridade de arquivo.

```python
excel_stream = io.BytesIO(file_bytes)
df = None
last_err = None

for engine in ["openpyxl", "xlrd", None]:
    try:
        excel_stream.seek(0)
        if engine:
            df = pd.read_excel(excel_stream, header=0, engine=engine)
        else:
            df = pd.read_excel(excel_stream, header=0)
        break
    except Exception as e:
        last_err = e

if df is None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Não foi possível interpretar o arquivo Excel enviado. Certifique-se de que é uma planilha Excel (.xlsx ou .xls) válida. (Erro: {last_err})"
    )
```

## Migration and Deployment Plan

1. Executar `pip install openpyxl xlrd` no ambiente local.
2. Na implantação na VM de produção, o script de atualização executará `pip install -r requirements.txt`, garantindo que o `openpyxl` seja instalado e o serviço Uvicorn reiniciado sem indisponibilidade.
