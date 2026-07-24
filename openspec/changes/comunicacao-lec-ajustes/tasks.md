## 1. Nomenclatura do Menu

- [x] 1.1 Atualizar rótulo do menu e cabeçalhos de "Sistema LEC" para "Comunicação LEC" no Frontend Vue 3 (Sidebar, Navbar, views).

## 2. Integração Prontuário / AGHU na Inclusão

- [x] 2.1 Investigar e corrigir a chamada do endpoint de busca de paciente por prontuário na aba "Solicitar Inclusão".
- [x] 2.2 Garantir o correto mapeamento dos campos `nome`, `dataNascimento` e `nomeMae` retornados pela consulta do AGHU/Oracle.

## 3. Controle de Acesso e Permissões

- [x] 3.1 Restringir acesso ao menu/rota Comunicação LEC para o perfil com função Enfermeiro, exibindo aviso de que a funcionalidade é voltada para Médicos e Residentes.
- [x] 3.2 Liberar acesso completo no menu Comunicação LEC para o perfil GESTÃO LEC às abas de nova solicitação (Inclusão, Edição, Standby e Exclusão).
