# Tasks

## 1. Ajuste do Dropdown em Solicitações

- [x] 1.1 Atualizar a computed `procedimentosDaEspecialidade` em `InteracoesLec.vue` para restringir as opções exclusivamente ao catálogo oficial do AGHU (`listFromAghu`), preservando o procedimento atual durante edição caso seja legado
- [x] 1.2 Verificar que o filtro de procedimentos em `Pacientes.vue` permanece inalterado, mantendo procedimentos do AGHU e históricos locais para auditoria e busca

## 2. Validação e Testes

- [x] 2.1 Verificar a listagem de procedimentos em tela para a especialidade Geral e confirmar que opções espúrias sem ID (como "CERVICAL") não constam no formulário de inclusão
- [x] 2.2 Executar `npm run build` no frontend para validar ausência de erros de compilação e tipagem
