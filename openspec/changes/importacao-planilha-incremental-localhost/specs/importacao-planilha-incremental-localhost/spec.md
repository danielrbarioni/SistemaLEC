## ADDED Requirements

### Requirement: Importação Incremental de Planilha Excel pelo Gestor LEC
O sistema DEVE permitir que o usuário com perfil Gestão LEC envie novas planilhas Excel pela interface web em ambiente localhost, realizando a comparação incremental automática.

#### Scenario: Comparação de nova planilha com solicitações existentes
- **WHEN** o gestor envia uma nova planilha contendo registros novos e registros previamente cadastrados
- **THEN** o sistema DEVE atualizar os registros existentes com as novas informações da planilha, criar apenas as novas solicitações excedentes e apresentar o relatório detalhado de criadas vs atualizadas.

#### Scenario: Isolamento do ambiente localhost
- **WHEN** o gestor realiza a importação na interface local
- **THEN** as alterações DEVEM ser aplicadas estritamente no banco de dados local `data/app.db`, sem qualquer sincronização ou gravação no banco de dados da VM de produção.
