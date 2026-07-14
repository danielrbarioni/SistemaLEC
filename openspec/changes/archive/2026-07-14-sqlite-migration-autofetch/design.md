## Contexto

O backend atualmente lê e salva dados em arquivos CSV locais. Isso causa lentidão, conflitos de concorrência e impede buscas eficientes. Este design estabelece uma camada estruturada de banco de dados SQLite local para gerenciar todos os dados dinâmicos da aplicação (pacientes, solicitações e status locais).

## Objetivos / Não-Objetivos

**Objetivos:**
- Implementar modelos do SQLAlchemy para Paciente, Solicitação e StatusLocal.
- Migrar os provedores de dados da aplicação para utilizar o SQLite.
- Desenvolver um script para importar os registros dos CSVs atuais para o SQLite.
- Disponibilizar rota de API para consultar dados demográficos de pacientes no AGHU/PostgreSQL ou SQLite.
- Acoplar o recurso de autopreenchimento no formulário de solicitações no frontend.

**Não-Objetivos:**
- Excluir os códigos antigos de provedores CSV (permanecerão apenas para referência).
- Alterar as tabelas físicas do AGHU (a conexão com o AGHU será estritamente de leitura).

## Decisões

- **Mapeamento ORM**: Usar SQLAlchemy para modelar e gerenciar a conexão com a base local (`data/app.db`).
- **Migração de Dados**: Executar script Python independente para transferir os dados dos CSVs atuais para o SQLite.
- **Estratégia de Busca de Pacientes**: 
  - Se a variável `AD_URL` ou configurações do AGHU estiverem ativas (produção na VM), o sistema busca prioritariamente no banco do AGHU (PostgreSQL).
  - Caso contrário (ou se a busca no AGHU falhar), busca na tabela de pacientes do SQLite local (mock).

## Riscos / Alternativas

- **Risco**: Erros de conexão ou timeout na comunicação com o banco PostgreSQL do AGHU.
  - *Mitigação*: Implementar tratamento de exceções robusto na rota de busca para que, em caso de indisponibilidade do AGHU, o sistema faça fallback para a base local do SQLite sem travar a interface.
