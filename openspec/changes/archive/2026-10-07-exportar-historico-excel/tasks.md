# Tasks: Exportar Histórico para Excel

## 1. Dependências do Frontend

- [x] 1.1 Instalar biblioteca `xlsx` no projeto frontend (`frontend/package.json`) e verificar resolução de tipos e instalação com `npm install`

## 2. Interface e Modal de Intervalo de Datas

- [x] 2.1 Adicionar o botão "Exportar Histórico" estilizado no canto superior direito da tabela do histórico em `Historico.vue` (abaixo dos filtros), visível exclusivamente para perfis ADMIN e GESTÃO LEC, e verificar abertura do modal ao clicar
- [x] 2.2 Criar modal de parametrização de exportação com campos `Data de` e `Data até`, com cálculo automático da data mais antiga como default e herança de datas pré-selecionadas nos filtros

## 3. Formatação, Mapeamento das 11 Colunas e Geração do Excel

- [x] 3.1 Implementar a função de extração e mapeamento dos registros aplicando cumulativamente todos os filtros ativos e o intervalo de datas, preenchendo as 11 colunas e aplicando `NA` para campos não aplicáveis
- [x] 3.2 Implementar a composição do arquivo `.xlsx` com bloco de metadados acima da tabela (Data/Hora de exportação, Intervalo de datas, Filtros aplicados) e download automático no navegador

## 4. Validação, Build e Deploy na VM

- [x] 4.1 Executar compilação de produção (`npm run build`) garantindo ausência de erros TypeScript ou de empacotamento
- [x] 4.2 Executar deploy seguro para a VM (`10.34.0.202`) via `scripts/deploy_to_vm.py`, preservando 100% o banco de produção da VM
