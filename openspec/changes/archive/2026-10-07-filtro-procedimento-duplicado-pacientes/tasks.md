# Tasks

## 1. Interface e Estado Reativo

- [x] 1.1 Adicionar estado reativo `filtroApenasProcedimentoDuplicado` em `Pacientes.vue` e verificar que inicia como falso
- [x] 1.2 Inserir checkbox "Exibir apenas pacientes com procedimento duplicado" na coluna de procedimentos do template de `Pacientes.vue` e verificar renderização consistente com os outros filtros
- [x] 1.3 Implementar watchers para garantir exclusividade mútua entre os 3 filtros de procedimento (`filtroApenasUmProcedimento`, `filtroApenasMultiplos`, `filtroApenasProcedimentoDuplicado`) e verificar desmarcação automática

## 2. Lógica de Filtragem e Verificação

- [x] 2.1 Implementar lógica de detecção de duplicidade de procedimentos por paciente utilizando normalização com `extrairNomeBaseProcedimento` e `formatarNomeProcedimento`
- [x] 2.2 Integrar a condição de procedimento duplicado no filtro da computed `pacientesProcessados` em `Pacientes.vue` e verificar que apenas pacientes elegíveis são exibidos
- [x] 2.3 Executar verificação de tipo / build do frontend com `npm run build` ou checagem de integridade para garantir ausência de regressões
