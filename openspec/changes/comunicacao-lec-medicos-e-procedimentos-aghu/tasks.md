## 1. Mapeamento de Especialidades e Procedimentos AGHU

- [x] 1.1 Criar `frontend/src/utils/especialidadeAghuMap.ts` contendo os códigos AGHU (`seq`) de todas as 23 especialidades cirúrgicas.
- [x] 1.2 Implementar função helper para buscar procedimentos do AGHU agregando múltiplos códigos por especialidade e gerenciando cache em memória.

## 2. Ajustes na Interface de Comunicação LEC (`InteracoesLec.vue`)

- [x] 2.1 Corrigir o `<datalist id="medicos-lista">` para usar `<option :value="med" />` sem duplicação de rótulo visual.
- [x] 2.2 Integrar o carregamento de procedimentos do AGHU para a especialidade ativa/selecionada via `especialidadeAghuMap`.
- [x] 2.3 Atualizar a busca de procedimentos para exibir os procedimentos do AGHU com fallback para procedimentos já cadastrados na base local.

## 3. Ajustes na Interface de Pacientes (`Pacientes.vue`)

- [x] 3.1 Integrar `especialidadeAghuMap` no filtro de procedimentos de `Pacientes.vue` para suportar todas as especialidades do AGHU.

## 4. Build, Deploy e Verificação

- [x] 4.1 Recompilar o bundle frontend com `npm run build`.
- [x] 4.2 Publicar as alterações na VM de produção (`10.34.0.202`) e reiniciar o serviço `sistemalec`.
- [x] 4.3 Validar em todas as especialidades a listagem de médicos (sem duplicidade) e procedimentos do AGHU.
