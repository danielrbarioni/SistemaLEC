## 1. Dependency Updates

- [x] 1.1 Add `openpyxl>=3.1.2` and `xlrd>=2.0.1` to `requirements.txt`
- [x] 1.2 Install `openpyxl` and `xlrd` in the active virtual environment (`.venv`)

## 2. Parser Resilience in excel_import_helper.py

- [x] 2.1 Update `src/helpers/excel_import_helper.py` to use a multi-engine fallback strategy (`openpyxl` -> `xlrd` -> default)
- [x] 2.2 Improve exception handling and feedback messages for invalid or corrupted spreadsheet files

## 3. Testing and Verification

- [x] 3.1 Run an automated test script with real `.xlsx` files (`data/Fila sistema Sede Plástica.xlsx`) to verify parsing and row extraction
- [x] 3.2 Verify that the `POST /api/pacientes/importar-excel` endpoint successfully processes Excel imports without missing dependency errors
