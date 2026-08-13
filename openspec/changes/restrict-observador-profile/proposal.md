# Proposal: Restringir Perfil 'OBSERVADOR' (Renomeado para 'NENHUM') e Registrar Solicitações no Histórico

## Summary
Modificação das permissões e nomenclatura do perfil `OBSERVADOR` para `NENHUM`, limitando seu acesso exclusivamente ao menu **Perfis**. Tentativas de acesso aos menus Comunicação LEC, Navegação, Pacientes e Histórico serão bloqueadas com mensagem de orientação. Além disso, as criações ou aprovações de solicitações de criação de usuário e perfil passarão a ser registradas no menu **Histórico**.

## Why
Garantir o controle de acesso e segurança de acordo com a política do sistema, assegurando que usuários sem perfil definido (agora chamados 'NENHUM') só possam solicitar vinculação de perfil. Adicionalmente, registrar auditoria completa de solicitações e aprovações de novos usuários e perfis no histórico de ações do sistema.

## Key Changes
1. **Renomear Perfil**: Alterar a denominação de `OBSERVADOR` para `NENHUM`.
2. **Restrição de Acesso**:
   - Manter visível/acessível apenas o menu **Perfis**.
   - Ocultar/desabilitar menus Comunicação LEC, Navegação, Pacientes e Histórico para o perfil NENHUM.
   - Caso o usuário tente acessar diretamente qualquer uma dessas rotas/menus restritos, exibir a mensagem: `'Solicite criação de usuário e associação a um perfil, no menu Perfis'`.
3. **Registro no Histórico**:
   - Gravar eventos de auditoria no menu **Histórico** ao criar ou aprovar solicitações de criação de usuário e de perfil.
4. **Preservação de Dados da VM**:
   - Manter intactos os dados existentes e o banco de dados da VM sem reset/truncate, preservando os registros de pacientes e ações já realizadas.

## Impact & Scope
- Afeta controle de acesso de frontend e backend guard/middlewares.
- Afeta exibição de menus de navegação.
- Afeta serviço de registro de Histórico/Auditoria para solicitações de perfil e usuário.
