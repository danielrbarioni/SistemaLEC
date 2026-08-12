## Context

A importação de planilhas Excel de pacientes é um fluxo crítico executado por perfis da Gestão LEC. Durante a utilização, surgiram erros de usabilidade (drag-and-drop instável devido ao borbulhamento de eventos DOM no Vue 3) e erros de infraestrutura HTTP (HTTP 405 Method Not Allowed ao enviar requisições multipart POST para a API).

## Goals / Non-Goals

**Goals:**
- Garantir comportamento de drag-and-drop suave e robusto no modal `ImportarPlanilhaPacientesModal.vue`.
- Tratar requisições HTTP `POST` no FastAPI tanto para `/api/pacientes/importar-excel` quanto para `/api/pacientes/importar-excel/`.
- Configurar suporte a CORS (`CORSMiddleware`) no FastAPI para tratar requisições preflight `OPTIONS`.
- Tratar erros de interpretação de arquivos Excel com `openpyxl` e mensagens amigáveis em HTTP 400.

**Non-Goals:**
- Alterações na estrutura das colunas esperadas da planilha Excel (A até L).
- Modificação das regras de negócio do processamento da fila de pacientes.

## Decisions

1. **Utilizar `dragCounter` e `pointer-events-none` no componente de upload Vue 3**:
   - *Decisão*: Manter um contador de `dragenter` e `dragleave` no estado do componente Vue 3 e desativar interações de ponteiro nos nós filhos internos do label.
   - *Razão*: Evita que o evento de saída de elementos filhos zere o estado `isDragging`, garantindo estabilidade no efeito de drag-and-drop.

2. **Registro duplo de rotas no FastAPI e CORS Middleware**:
   - *Decisão*: Mapear `@router.post("/importar-excel")` e `@router.post("/importar-excel/")` simultaneamente e incluir `CORSMiddleware`.
   - *Razão*: Previne respostas HTTP 307/308 que alguns clientes ou servidores proxy convertem para `GET`, ocasionando HTTP 405 Method Not Allowed.

3. **Fallback seguro de leitura Excel com `openpyxl`**:
   - *Decisão*: Tentar leitura padrão com `pandas.read_excel` e em caso de exceção tentar fallback com `engine='openpyxl'`.
   - *Razão*: Garante suporte amplo a planilhas criadas em versões diferentes do Microsoft Excel ou LibreOffice sem quebrar o servidor com exceções não capturadas.

## Risks / Trade-offs

- **[Risk] Redirecionamento por Nginx/Proxy** → *Mitigation*: O mapeamento duplo de rotas e CORS resolve o comportamento independentemente de o proxy adicionar ou remover barras no final das URLs.
