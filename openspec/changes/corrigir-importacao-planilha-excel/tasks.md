## 1. Frontend Drag & Drop Fixes

- [x] 1.1 Atualizar `ImportarPlanilhaPacientesModal.vue` com `dragCounter` para estabilizar o estado `isDragging`.
- [x] 1.2 Aplicar `pointer-events-none` nos nós visuais filhos da área de soltura de arquivo.
- [x] 1.3 Adicionar manipuladores preventivos de eventos drag & drop para evitar navegação no browser.

## 2. Backend Routing & Middleware Fixes

- [x] 2.1 Mapear rotas duplas `@router.post("/importar-excel")` e `@router.post("/importar-excel/")` em `src/routers/paciente.py`.
- [x] 2.2 Adicionar `CORSMiddleware` ao servidor FastAPI em `src/main.py`.
- [x] 2.3 Adicionar tratamento de exceção com `openpyxl` em `src/helpers/excel_import_helper.py`.

## 3. Build & Deployment

- [x] 3.1 Recompilar o bundle do Vue 3 (`npm run build`).
- [x] 3.2 Publicar o código e reiniciar o serviço na VM de produção (`10.34.0.202`).
