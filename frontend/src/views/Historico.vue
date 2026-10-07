<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Histórico de Ações Realizadas</h1>
      <span class="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full border border-gray-200">
        Acompanhamento de Ações
      </span>
    </div>

    <!-- Filtros de Busca -->
    <Card>
      <div class="space-y-4">
        <div class="flex justify-between items-center border-b border-gray-100 pb-2">
          <h2 class="text-sm font-bold text-gray-700 uppercase tracking-wider">Filtros de Busca</h2>
          <button 
            @click="limparFiltros" 
            class="text-xs text-indigo-600 hover:text-indigo-800 font-semibold cursor-pointer"
          >
            🔄 Limpar Filtros
          </button>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          <!-- 1. Data De -->
          <div class="form-group">
            <label for="dataInicio" class="form-label font-semibold text-xs">Data De</label>
            <input id="dataInicio" v-model="dataInicio" type="date" class="form-control text-xs py-1.5" />
          </div>

          <!-- 2. Data Até -->
          <div class="form-group">
            <label for="dataFim" class="form-label font-semibold text-xs">Data Até</label>
            <input id="dataFim" v-model="dataFim" type="date" class="form-control text-xs py-1.5" />
          </div>

          <!-- 3. Origem / Menu -->
          <div class="form-group">
            <label for="filtroOrigemMenu" class="form-label font-semibold text-xs">Origem / Menu</label>
            <select id="filtroOrigemMenu" v-model="filtroOrigemMenu" class="form-control text-xs py-1.5">
              <option value="">Todas</option>
              <option value="Solicitações LEC">Solicitações LEC</option>
              <option value="Pacientes">Pacientes</option>
              <option value="Usuários">Usuários</option>
            </select>
          </div>

          <!-- 4. Prontuário / Paciente -->
          <div class="form-group">
            <label for="filtroPaciente" class="form-label font-semibold text-xs">Prontuário / Paciente</label>
            <input 
              id="filtroPaciente" 
              v-model="filtroPaciente" 
              type="text" 
              placeholder="Digite o prontuário ou nome..." 
              class="form-control text-xs py-1.5" 
            />
          </div>

          <!-- 5. Especialidade -->
          <div class="form-group">
            <label for="filtroEspecialidade" class="form-label font-semibold text-xs">Especialidade</label>
            <select 
              id="filtroEspecialidade" 
              v-model="filtroEspecialidade" 
              class="form-control text-xs py-1.5"
              :disabled="perfisStore.perfilAtivo?.tipo === 'ESPECIALIDADE'"
              :class="{ 'bg-gray-100 cursor-not-allowed': perfisStore.perfilAtivo?.tipo === 'ESPECIALIDADE' }"
            >
              <option v-if="perfisStore.perfilAtivo?.tipo !== 'ESPECIALIDADE'" value="">Todas</option>
              <option v-for="esp in especialidadesDisponiveis" :key="esp" :value="esp">
                {{ esp }}
              </option>
            </select>
          </div>

          <!-- 6. Ação -->
          <div class="form-group">
            <label for="filtroAcaoTipo" class="form-label font-semibold text-xs">Ação</label>
            <select id="filtroAcaoTipo" v-model="filtroAcaoTipo" class="form-control text-xs py-1.5">
              <option value="">Todas</option>
              <optgroup label="Menu Solicitações LEC ou Pacientes">
                <option value="INSERIR">Inclusão de Procedimento (Menu Solicitações LEC ou Pacientes)</option>
                <option value="EDITAR">Edição de Procedimento</option>
                <option value="STANDBY">Standby de Procedimento</option>
                <option value="EXCLUIR">Exclusão de Procedimento</option>
                <option value="SOLICITAR_APA">Solicitação APA</option>
              </optgroup>
              <optgroup label="Menu Usuários">
                <option value="CRIAR_PERFIL">Criação de Perfil</option>
                <option value="EXCLUIR_PERFIL">Exclusão de Perfil</option>
                <option value="CRIAR_USUARIO">Criação de Usuário</option>
                <option value="EDITAR_USUARIO">Edição de Usuário</option>
                <option value="EXCLUIR_USUARIO">Exclusão de Usuário</option>
                <option value="CRIAR_CATEGORIZACAO">Criação de Categorização</option>
                <option value="EDITAR_CATEGORIZACAO">Edição de Categorização</option>
                <option value="EXCLUIR_CATEGORIZACAO">Exclusão de Categorização</option>
              </optgroup>
            </select>
          </div>

          <!-- 7. Tipo de Evento -->
          <div class="form-group">
            <label for="filtroEventoTipo" class="form-label font-semibold text-xs">Tipo de Evento</label>
            <select id="filtroEventoTipo" v-model="filtroEventoTipo" class="form-control text-xs py-1.5">
              <option value="">Todas</option>
              <option value="SOLICITACAO">Solicitação</option>
              <option value="ALTERACAO">Alteração de Solicitação</option>
              <option value="CANCELAMENTO">Cancelamento de Solicitação</option>
              <option value="RESPOSTA">Resposta</option>
              <option value="EXECUCAO">Execução</option>
            </select>
          </div>

          <!-- 8. Status -->
          <div class="form-group">
            <label for="filtroStatus" class="form-label font-semibold text-xs">Status</label>
            <select id="filtroStatus" v-model="filtroStatus" class="form-control text-xs py-1.5">
              <option value="">Todos</option>
              <option value="PENDENTE">PENDENTE</option>
              <option value="APROVADO">APROVADO</option>
              <option value="REJEITADO">REJEITADO</option>
              <option value="CANCELADO">CANCELADO</option>
              <option value="CONCLUIDO">CONCLUÍDO</option>
            </select>
          </div>

          <!-- 9. Usuário Executor -->
          <div class="form-group sm:col-span-2 md:col-span-4">
            <label for="filtroUsuario" class="form-label font-semibold text-xs">Usuário Executor</label>
            <input 
              id="filtroUsuario" 
              v-model="filtroUsuario" 
              type="text" 
              placeholder="Digite o nome de usuário (ex.: nome.sobrenome)..." 
              class="form-control text-xs py-1.5" 
            />
          </div>
        </div>
      </div>
    </Card>

    <!-- Lista de Solicitações/Respostas -->
    <Card>
      <!-- Barra de Ferramentas / Cabeçalho Superior da Tabela -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-3 border-b border-gray-100 gap-2 mb-3">
        <div class="flex items-center space-x-2">
          <span class="text-xs text-gray-500 font-medium">
            Total de registros: <span class="font-bold text-gray-800">{{ solicitacoesFiltradas.length }}</span>
          </span>
          <span v-if="solicitacoesFiltradas.length !== solicitacoes.length" class="text-[11px] text-gray-400">
            (de {{ solicitacoes.length }} totais)
          </span>
        </div>
        <div v-if="podeExportarHistorico" class="self-end sm:self-auto">
          <button 
            @click="abrirModalExportar"
            class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-xs hover:shadow transition-all cursor-pointer"
            title="Exportar histórico filtrado para planilha Excel (.xlsx)"
          >
            <ArrowDownTrayIcon class="w-4 h-4" />
            <span>Exportar Histórico</span>
          </button>
        </div>
      </div>

      <div v-if="loading" class="flex justify-center items-center py-8">
        <LoadingIndicator />
      </div>
      <div v-else-if="solicitacoesFiltradas.length === 0" class="text-center py-10 text-gray-500">
        Nenhuma solicitação ou resposta encontrada para os filtros selecionados.
      </div>
      <div v-else class="w-full overflow-x-auto max-h-[calc(100vh-280px)] overflow-y-auto border border-gray-100 rounded-lg">
        <table class="w-full table-auto divide-y divide-gray-200 border-separate border-spacing-0 text-xs">
          <thead class="bg-gray-50 sticky top-0 z-10 shadow-xs">
            <tr>
              <th class="sticky top-0 bg-gray-50 z-10 px-2.5 py-2.5 text-left text-[11px] font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200 whitespace-nowrap">Data / Hora</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-2.5 py-2.5 text-center text-[11px] font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200 whitespace-nowrap">Origem / Menu</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-2.5 py-2.5 text-left text-[11px] font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200">Prontuário / Paciente</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-2.5 py-2.5 text-left text-[11px] font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200">Especialidade / Procedimento</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-2.5 py-2.5 text-center text-[11px] font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200 whitespace-nowrap">Ação</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-2.5 py-2.5 text-center text-[11px] font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200 whitespace-nowrap">Tipo de Evento</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-2.5 py-2.5 text-center text-[11px] font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200 whitespace-nowrap">Status</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-2.5 py-2.5 text-left text-[11px] font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200">Perfil / Usuário Executor</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-2.5 py-2.5 text-center text-[11px] font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200 whitespace-nowrap">Descrição da Ação</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="solic in solicitacoesPaginadas" :key="solic.id" class="hover:bg-slate-50/80 transition-colors">
              <!-- 1. Data/Hora -->
              <td class="px-2.5 py-2.5 whitespace-nowrap text-[11px] font-mono text-gray-600">
                {{ formatarDataHora(solic.data_criacao) }}
              </td>

              <!-- 2. Origem/Menu -->
              <td class="px-2.5 py-2.5 whitespace-nowrap text-center">
                <span class="px-2 py-0.5 rounded text-[10px] font-semibold text-indigo-700 bg-indigo-50 border border-indigo-100 inline-block">
                  {{ formatarOrigemMenu(solic.origem_menu) }}
                </span>
              </td>

              <!-- 3. Prontuário/Paciente -->
              <td class="px-2.5 py-2.5 text-[11px] max-w-[180px]">
                <div v-if="solic.codigo_paciente && String(solic.codigo_paciente) !== '0'" class="font-mono font-bold text-gray-800">
                  #{{ solic.codigo_paciente }}
                </div>
                <div class="text-gray-900 font-medium truncate" :title="solic.nome_paciente">
                  {{ solic.nome_paciente && solic.nome_paciente !== '—' && !String(solic.nome_paciente).startsWith('Paciente #0') ? solic.nome_paciente : '—' }}
                </div>
              </td>

              <!-- 4. Especialidade/Procedimento -->
              <td class="px-2.5 py-2.5 text-[11px] text-gray-700 max-w-[210px] break-words leading-tight">
                <div class="font-bold text-gray-800">{{ solic.especialidade || '—' }}</div>
                <div v-if="solic.procedimento && solic.procedimento !== '—'" class="text-gray-600 mt-0.5">
                  <span v-if="solic.procedimento_anterior && solic.procedimento_anterior !== solic.procedimento" class="text-gray-400 line-through mr-1 text-[10px]">
                    {{ solic.procedimento_anterior }}
                  </span>
                  <span v-if="solic.procedimento_anterior && solic.procedimento_anterior !== solic.procedimento" class="font-bold text-blue-700 mr-1 text-[10px]">
                    ➔
                  </span>
                  <span :class="solic.procedimento_anterior && solic.procedimento_anterior !== solic.procedimento ? 'font-bold text-blue-800' : ''">
                    {{ solic.procedimento }}
                  </span>
                </div>
              </td>

              <!-- 5. Ação/Tipo -->
              <td class="px-2.5 py-2.5 whitespace-nowrap text-center">
                <span :class="getTipoBadgeClass(solic.tipo)">{{ formatarTipo(solic.tipo) }}</span>
              </td>

              <!-- 6. Tipo de Evento (Solicitação, Execução, Alteração de Solicitação, Cancelamento de Solicitação, Resposta) -->
              <td class="px-2.5 py-2.5 whitespace-nowrap text-center">
                <div class="inline-flex flex-col items-center justify-center">
                  <span v-if="solic.evento_tipo === 'CANCELAMENTO' || (solic.status === 'CANCELADO' && (solic.detalhes?.toLowerCase().includes('cancelou') || solic.evento_tipo === 'CANCELAMENTO'))" class="px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800 border border-red-200">
                    Cancelamento de Solicitação
                  </span>
                  <span v-else-if="solic.evento_tipo === 'RESPOSTA' || solic.is_resposta" class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200">
                    Resposta
                  </span>
                  <span v-else-if="solic.evento_tipo === 'EXECUCAO' || solic.origem_menu === 'Pacientes' || solic.origem_menu === 'Importação Planilha'" class="px-2 py-0.5 rounded text-[10px] font-bold bg-teal-100 text-teal-800 border border-teal-200">
                    Execução
                  </span>
                  <span v-else-if="solic.evento_tipo === 'ALTERACAO' || solic.evento_tipo === 'EDICAO'" class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                    Alteração de Solicitação
                  </span>
                  <span v-else class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200">
                    Solicitação
                  </span>

                  <!-- Apenas para ações do menu Perfis: exibe o alvo (perfil/usuário/profissional) embaixo do badge -->
                  <div 
                    v-if="obterAlvoAcaoPerfis(solic)" 
                    class="mt-1 text-[10px] font-semibold text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200 truncate max-w-[140px]" 
                    :title="obterAlvoAcaoPerfis(solic)"
                  >
                    {{ obterAlvoAcaoPerfis(solic) }}
                  </div>
                </div>
              </td>

              <!-- 7. Status -->
              <td class="px-2.5 py-2.5 whitespace-nowrap text-center">
                <span :class="getStatusBadgeClass(solic.status)">{{ solic.status }}</span>
              </td>

              <!-- 8. Perfil executor/Usuário Executor (Usuário Ebserh) -->
              <td class="px-2.5 py-2.5 text-[11px] max-w-[150px]">
                <div v-if="solic.perfil_executor" class="mb-0.5">
                  <span class="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold border border-slate-200 text-[10px]">
                    {{ solic.perfil_executor }}
                  </span>
                </div>
                <div class="text-indigo-900 font-mono font-medium truncate" :title="solic.username || solic.usuario || solic.user">
                  {{ solic.username || solic.usuario || solic.user || '—' }}
                </div>
              </td>

              <!-- 9. Descrição da Ação (Clicável) -->
              <td class="px-2.5 py-2.5 whitespace-nowrap text-center">
                <button 
                  @click="abrirModalDetalhes(solic)"
                  class="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md bg-indigo-50 hover:bg-indigo-100 text-indigo-700 hover:text-indigo-900 font-semibold border border-indigo-200 transition-colors shadow-2xs cursor-pointer text-[11px]"
                  title="Ver todos os detalhes desta ação"
                >
                  <span>🔍</span>
                  <span>Ver Detalhes</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paginação (50 itens por página padrão) -->
      <div v-if="solicitacoesFiltradas.length > 0" class="mt-2 border border-gray-100 rounded-lg overflow-hidden">
        <Pagination
          :total-items="solicitacoesFiltradas.length"
          v-model:current-page="paginaAtual"
          v-model:items-per-page="itensPorPagina"
          item-name="ações no histórico"
        />
      </div>
    </Card>

    <!-- Modal de Descrição e Detalhes Completos da Ação -->
    <div v-if="modalDetalhes.aberto && modalDetalhes.solic" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6 space-y-4 border border-gray-200 animate-in fade-in zoom-in-95 duration-150">
        
        <!-- Cabeçalho do Modal -->
        <div class="flex justify-between items-start border-b border-gray-150 pb-3">
          <div>
            <div class="flex items-center space-x-2">
              <span :class="getTipoBadgeClass(modalDetalhes.solic.tipo)">
                {{ formatarTipo(modalDetalhes.solic.tipo) }}
              </span>
              <span class="text-xs font-mono text-gray-500 font-semibold">
                #{{ modalDetalhes.solic.id }}
              </span>
            </div>
            <h3 class="text-lg font-bold text-gray-900 mt-1">
              Detalhes da Ação
            </h3>
          </div>
          <button 
            @click="fecharModalDetalhes" 
            class="text-gray-400 hover:text-gray-600 text-xl font-bold p-1 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
            title="Fechar"
          >
            ✕
          </button>
        </div>

        <!-- Conteúdo do Modal (Scrollável) -->
        <div class="space-y-4 text-xs text-gray-700 max-h-[72vh] overflow-y-auto pr-1">
          
          <!-- Bloco 1: Visão Geral / Dados do Evento -->
          <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2.5">
            <span class="text-[11px] font-bold text-indigo-700 uppercase tracking-wider block border-b border-slate-200 pb-1">
              📌 Dados Gerais do Registro
            </span>

            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs">
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Data / Hora:</span>
                <span class="font-mono font-semibold text-gray-900">{{ formatarDataHora(modalDetalhes.solic.data_criacao) }}</span>
              </div>

              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Origem / Menu:</span>
                <span class="font-semibold text-indigo-700">{{ formatarOrigemMenu(modalDetalhes.solic.origem_menu) }}</span>
              </div>

              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Tipo de Evento:</span>
                <span v-if="modalDetalhes.solic.evento_tipo === 'CANCELAMENTO' || (modalDetalhes.solic.status === 'CANCELADO' && (modalDetalhes.solic.detalhes?.toLowerCase().includes('cancelou') || modalDetalhes.solic.evento_tipo === 'CANCELAMENTO'))" class="px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800 border border-red-200">
                  Cancelamento de Solicitação
                </span>
                <span v-else-if="modalDetalhes.solic.evento_tipo === 'RESPOSTA' || modalDetalhes.solic.is_resposta" class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200">
                  Resposta
                </span>
                <span v-else-if="modalDetalhes.solic.evento_tipo === 'EXECUCAO' || modalDetalhes.solic.origem_menu === 'Pacientes'" class="px-2 py-0.5 rounded text-[10px] font-bold bg-teal-100 text-teal-800 border border-teal-200">
                  Execução
                </span>
                <span v-else-if="modalDetalhes.solic.evento_tipo === 'ALTERACAO' || modalDetalhes.solic.evento_tipo === 'EDICAO'" class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                  Alteração de Solicitação
                </span>
                <span v-else class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200">
                  Solicitação
                </span>
              </div>

              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Status:</span>
                <span :class="getStatusBadgeClass(modalDetalhes.solic.status)">{{ modalDetalhes.solic.status }}</span>
              </div>

              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Perfil Executor:</span>
                <span class="font-semibold text-gray-900">{{ modalDetalhes.solic.perfil_executor || '—' }}</span>
              </div>

              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Usuário Executor:</span>
                <span class="font-mono font-medium text-indigo-900">{{ modalDetalhes.solic.usuario || modalDetalhes.solic.username || '—' }}</span>
              </div>
            </div>

            <!-- Dados do Paciente (quando houver) -->
            <div 
              v-if="modalDetalhes.solic.codigo_paciente && String(modalDetalhes.solic.codigo_paciente) !== '0' && modalDetalhes.solic.nome_paciente && modalDetalhes.solic.nome_paciente !== '—'" 
              class="pt-2 border-t border-slate-200/80 grid grid-cols-2 gap-2 text-xs"
            >
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Nº Prontuário:</span>
                <span class="font-mono font-bold text-gray-900">#{{ modalDetalhes.solic.codigo_paciente }}</span>
              </div>
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Nome do Paciente:</span>
                <span class="font-bold text-gray-900">{{ modalDetalhes.solic.nome_paciente }}</span>
              </div>
            </div>

            <!-- Especialidade e Procedimento -->
            <div 
              v-if="(modalDetalhes.solic.especialidade && modalDetalhes.solic.especialidade !== '—') || (modalDetalhes.solic.procedimento && modalDetalhes.solic.procedimento !== '—')" 
              class="pt-2 border-t border-slate-200/80 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs"
            >
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Especialidade:</span>
                <span class="font-semibold text-gray-800">{{ modalDetalhes.solic.especialidade || '—' }}</span>
              </div>
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Procedimento:</span>
                <div v-if="modalDetalhes.solic.procedimento_anterior && modalDetalhes.solic.procedimento_anterior !== modalDetalhes.solic.procedimento" class="space-y-0.5">
                  <div class="text-[11px] text-gray-400 line-through">{{ modalDetalhes.solic.procedimento_anterior }}</div>
                  <div class="font-bold text-blue-800 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 inline-block text-xs">
                    ➔ {{ modalDetalhes.solic.procedimento }}
                  </div>
                </div>
                <span v-else class="font-semibold text-gray-800">{{ modalDetalhes.solic.procedimento || '—' }}</span>
              </div>
            </div>
          </div>

          <!-- Bloco 2: Detalhes Específicos por Tipo de Ação -->

          <!-- CASO A: Edição de Procedimento (com lista de campos alterados estruturada) -->
          <div 
            v-if="isAcaoEdicaoProcedimento(modalDetalhes.solic)" 
            class="p-3.5 bg-amber-50/90 border border-amber-200 rounded-xl space-y-2.5"
          >
            <div class="flex items-center space-x-1.5 text-amber-900 font-bold text-xs border-b border-amber-200/80 pb-1">
              <span>✏️</span>
              <span>Campos Alterados nesta Ação de Edição:</span>
            </div>

            <div v-if="obterMudancasCompletas(modalDetalhes.solic).length > 0" class="space-y-1.5">
              <div 
                v-for="mudanca in obterMudancasCompletas(modalDetalhes.solic)" 
                :key="mudanca.campo"
                class="flex flex-col sm:flex-row sm:items-center text-xs text-amber-950 bg-white/90 p-2 rounded-lg border border-amber-200/70"
              >
                <span class="font-bold text-amber-900 sm:w-44 shrink-0">{{ mudanca.campo }}:</span>
                <div class="flex items-center space-x-1.5 flex-wrap">
                  <span class="text-gray-500 line-through text-[11px]">{{ mudanca.anterior || '—' }}</span>
                  <span class="font-bold text-blue-800 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 text-xs">
                    ➔ {{ mudanca.novo }}
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="text-gray-600 italic text-[11px] bg-white/80 p-2 rounded-lg border border-amber-200/50">
              Atualização de justificativa clínica / indicação.
            </div>
          </div>

          <!-- CASO B: Parâmetros Clínicos de Procedimento (Inclusão, Standby, Exclusão, Solicitação APA) -->
          <div 
            v-if="isAcaoProcedimento(modalDetalhes.solic) && !isAcaoEdicaoProcedimento(modalDetalhes.solic)" 
            class="p-3.5 bg-blue-50/60 border border-blue-200 rounded-xl space-y-2.5"
          >
            <span class="text-[11px] font-bold text-blue-900 uppercase tracking-wider block border-b border-blue-200 pb-1">
              🩺 Parâmetros Cirúrgicos da Solicitação
            </span>

            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs">
              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Prioridade Swalis:</span>
                <span v-if="modalDetalhes.solic.swallis || modalDetalhes.solic.swalis" :class="getSwalisClass(modalDetalhes.solic.swallis || modalDetalhes.solic.swalis)">
                  {{ modalDetalhes.solic.swallis || modalDetalhes.solic.swalis }}
                </span>
                <span v-else class="text-gray-400 italic">—</span>
              </div>

              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Judicialização:</span>
                <span class="font-medium text-gray-900">{{ modalDetalhes.solic.judicializado || 'Não' }}</span>
              </div>

              <div>
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Lateralidade:</span>
                <span class="font-medium text-gray-900">{{ modalDetalhes.solic.lateralidade || 'Indefinida' }}</span>
              </div>

              <div v-if="modalDetalhes.solic.tempo_standby">
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Tempo de Standby:</span>
                <span class="font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded border border-amber-300">
                  {{ modalDetalhes.solic.tempo_standby }} dias
                </span>
              </div>

              <div class="col-span-2">
                <span class="font-bold text-gray-500 uppercase text-[10px] block">
                  {{ isBucoMaxiloEsp(modalDetalhes.solic?.especialidade) ? 'Dentista Responsável:' : 'Médico Responsável:' }}
                </span>
                <span class="font-semibold text-gray-900">{{ modalDetalhes.solic.medico_responsavel || 'Não informado' }}</span>
              </div>

              <div v-if="modalDetalhes.solic.categorizacao" class="col-span-2">
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Categorização Profissional:</span>
                <span class="font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200 inline-block">
                  🏷️ {{ modalDetalhes.solic.categorizacao }}
                </span>
              </div>
            </div>
          </div>

          <!-- CASO C: Ações do Menu Perfis (Usuários, Perfis, Categorizações) -->
          <div 
            v-if="modalDetalhes.solic.origem_menu === 'Perfis' || modalDetalhes.solic.tipo.startsWith('CRIAR_') || modalDetalhes.solic.tipo.startsWith('EDITAR_') || modalDetalhes.solic.tipo.startsWith('EXCLUIR_')" 
            class="p-3.5 bg-purple-50/70 border border-purple-200 rounded-xl space-y-2.5"
          >
            <span class="text-[11px] font-bold text-purple-900 uppercase tracking-wider block border-b border-purple-200 pb-1">
              ⚙️ Detalhes Administrativos
            </span>

            <div class="space-y-2 text-xs">
              <div class="bg-white p-2.5 rounded-lg border border-purple-100 text-purple-950 font-medium">
                {{ modalDetalhes.solic.detalhes }}
              </div>
            </div>
          </div>

          <!-- CASO D: Resposta da Gestão LEC (quando for evento RESPOSTA ou concluído com justificativa) -->
          <div 
            v-if="modalDetalhes.solic.evento_tipo === 'RESPOSTA' || modalDetalhes.solic.is_resposta || modalDetalhes.solic.status === 'REJEITADO' || modalDetalhes.solic.status === 'CANCELADO'" 
            class="p-3.5 rounded-xl border space-y-2"
            :class="modalDetalhes.solic.status === 'REJEITADO' ? 'bg-red-50/70 border-red-200' : modalDetalhes.solic.status === 'APROVADO' ? 'bg-emerald-50/70 border-emerald-200' : 'bg-gray-50 border-gray-200'"
          >
            <div 
              class="flex justify-between items-center border-b pb-1"
              :class="modalDetalhes.solic.status === 'REJEITADO' ? 'border-red-200 text-red-900' : modalDetalhes.solic.status === 'APROVADO' ? 'border-emerald-200 text-emerald-900' : 'border-gray-200 text-gray-800'"
            >
              <span class="text-[11px] font-bold uppercase tracking-wider">
                💬 Decisão / Resposta
              </span>
              <span :class="getStatusBadgeClass(modalDetalhes.solic.status)">{{ modalDetalhes.solic.status }}</span>
            </div>

            <div>
              <label class="block font-bold text-[11px] mb-1 text-gray-700">
                {{ modalDetalhes.solic.status === 'REJEITADO' ? 'Motivo / Justificativa da Rejeição:' : 'Desfecho / Justificativa:' }}
              </label>
              <div class="p-2.5 bg-white border rounded-lg text-xs leading-relaxed whitespace-pre-wrap font-medium text-slate-800">
                {{ extrairJustificativaResposta(modalDetalhes.solic) }}
              </div>
            </div>
          </div>

          <!-- Bloco 3: Justificativa Clínica / Descrição Completa Original -->
          <div v-if="modalDetalhes.solic.evento_tipo !== 'RESPOSTA' && modalDetalhes.solic.detalhes" class="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
            <label class="block font-bold text-gray-700 text-[11px]">Descrição Original / Justificativa Clínica:</label>
            <div class="p-2.5 bg-white border border-slate-200 rounded-lg text-slate-800 text-xs leading-relaxed whitespace-pre-wrap font-medium">
              {{ modalDetalhes.solic.detalhes }}
            </div>
          </div>

        </div>

        <!-- Rodapé do Modal -->
        <div class="flex justify-end pt-3 border-t border-gray-150">
          <button 
            @click="fecharModalDetalhes" 
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-xs hover:shadow transition-colors cursor-pointer"
          >
            Fechar
          </button>
        </div>

      </div>
    </div>

    <!-- Modal de Intervalo de Datas para Exportação em Excel -->
    <div v-if="modalExportar.aberto" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-4 border border-gray-200 animate-in fade-in zoom-in-95 duration-150">
        
        <!-- Cabeçalho do Modal -->
        <div class="flex justify-between items-center border-b border-gray-150 pb-3">
          <div class="flex items-center space-x-2.5">
            <div class="p-2 bg-emerald-50 rounded-lg border border-emerald-200 text-emerald-600">
              <ArrowDownTrayIcon class="w-5 h-5" />
            </div>
            <div>
              <h3 class="text-base font-bold text-gray-900 leading-tight">Exportar Histórico para Excel</h3>
              <p class="text-xs text-gray-500">Defina o período das ações a exportar</p>
            </div>
          </div>
          <button 
            @click="fecharModalExportar" 
            class="text-gray-400 hover:text-gray-600 text-xl font-bold p-1 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
            title="Fechar"
          >
            ✕
          </button>
        </div>

        <!-- Formulário do Modal -->
        <div class="space-y-4 text-xs text-gray-700 py-1">
          <p class="text-gray-600 leading-relaxed">
            A exportação respeitará todos os filtros ativos na tela. Escolha o intervalo de datas das ações:
          </p>

          <div class="grid grid-cols-2 gap-3 bg-gray-50 p-3.5 rounded-xl border border-gray-200">
            <div class="form-group">
              <label for="exportDataInicio" class="form-label font-bold text-xs text-gray-700">Data de</label>
              <input 
                id="exportDataInicio" 
                v-model="modalExportar.dataInicio" 
                type="date" 
                class="form-control text-xs py-1.5 bg-white" 
              />
            </div>
            <div class="form-group">
              <label for="exportDataFim" class="form-label font-bold text-xs text-gray-700">Data até</label>
              <input 
                id="exportDataFim" 
                v-model="modalExportar.dataFim" 
                type="date" 
                class="form-control text-xs py-1.5 bg-white" 
              />
            </div>
          </div>

          <div v-if="resumoFiltrosAtivos" class="bg-slate-50 p-3 rounded-lg border border-slate-200 text-[11px] text-slate-600">
            <span class="font-bold text-slate-700 block mb-0.5">Demais filtros aplicados:</span>
            <span>{{ resumoFiltrosAtivos }}</span>
          </div>
        </div>

        <!-- Rodapé do Modal -->
        <div class="flex justify-end space-x-2 pt-3 border-t border-gray-150">
          <button 
            @click="fecharModalExportar" 
            class="px-3.5 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
          >
            Cancelar
          </button>
          <button 
            @click="executarExportacaoExcel" 
            :disabled="modalExportar.loading"
            class="inline-flex items-center space-x-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-xs hover:shadow transition-colors cursor-pointer disabled:opacity-50"
          >
            <ArrowDownTrayIcon class="w-4 h-4" />
            <span>{{ modalExportar.loading ? 'Gerando...' : 'Exportar (.xlsx)' }}</span>
          </button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import { ArrowDownTrayIcon } from '@heroicons/vue/24/outline';
import * as XLSX from 'xlsx-js-style';
import api from '../services/api';
import Card from '../components/Card.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';
import Pagination from '../components/Pagination.vue';
import { usePerfisStore } from '../stores/perfis';

const toast = useToast();
const perfisStore = usePerfisStore();

const paginaAtual = ref(1);
const itensPorPagina = ref(50);

const solicitacoes = ref<any[]>([]);
const pacientesBase = ref<any[]>([]);
const usuariosLocais = ref<any[]>([]);
const loading = ref(false);

// Estado do Modal de Detalhes da Ação
const modalDetalhes = ref<{ aberto: boolean; solic: any }>({
  aberto: false,
  solic: null
});

const abrirModalDetalhes = (solic: any) => {
  modalDetalhes.value = {
    aberto: true,
    solic: solic
  };
};

const fecharModalDetalhes = () => {
  modalDetalhes.value = {
    aberto: false,
    solic: null
  };
};

// Controle de Acesso: Apenas ADMIN ou GESTÃO LEC podem exportar o histórico
const podeExportarHistorico = computed(() => {
  const p = perfisStore.perfilAtivo;
  if (!p) return false;
  const tipo = (p.tipo || '').toUpperCase();
  const nome = (p.nome || '').toUpperCase();
  const id = (p.id || '').toUpperCase();
  return (
    tipo === 'ADMIN' ||
    tipo === 'GESTAO_LEC' ||
    nome === 'ADMIN' ||
    nome.includes('GESTAO') ||
    nome.includes('GESTÃO') ||
    id === 'ADMIN' ||
    id === 'GESTAO_LEC'
  );
});

// Modal e Lógica de Exportação para Excel
const modalExportar = ref({
  aberto: false,
  dataInicio: '',
  dataFim: '',
  loading: false
});

const obterHojeString = () => {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const calcularDataMaisAntiga = () => {
  let maisAntiga = '';
  for (const s of solicitacoes.value) {
    if (s.data_criacao) {
      const match = String(s.data_criacao).match(/^(\d{4}-\d{2}-\d{2})/);
      if (match) {
        const dt = match[1];
        if (!maisAntiga || dt < maisAntiga) {
          maisAntiga = dt;
        }
      }
    }
  }
  return maisAntiga || obterHojeString();
};

const abrirModalExportar = () => {
  modalExportar.value = {
    aberto: true,
    dataInicio: dataInicio.value || calcularDataMaisAntiga(),
    dataFim: dataFim.value || obterHojeString(),
    loading: false
  };
};

const fecharModalExportar = () => {
  modalExportar.value.aberto = false;
  modalExportar.value.loading = false;
};

const resumoFiltrosAtivos = computed(() => {
  const f: string[] = [];
  if (perfisStore.perfilAtivo?.tipo === 'ESPECIALIDADE') {
    f.push(`Especialidade: ${perfisStore.perfilAtivo.especialidade || perfisStore.perfilAtivo.nome}`);
  } else if (filtroEspecialidade.value) {
    f.push(`Especialidade: ${filtroEspecialidade.value}`);
  }
  if (filtroOrigemMenu.value) f.push(`Origem: ${filtroOrigemMenu.value}`);
  if (filtroPaciente.value) f.push(`Prontuário/Paciente: ${filtroPaciente.value}`);
  if (filtroAcaoTipo.value) f.push(`Ação: ${formatarTipo(filtroAcaoTipo.value)}`);
  if (filtroEventoTipo.value) f.push(`Tipo de Evento: ${filtroEventoTipo.value}`);
  if (filtroStatus.value) f.push(`Status: ${filtroStatus.value}`);
  if (filtroUsuario.value) f.push(`Usuário: ${filtroUsuario.value}`);
  return f.join(' | ');
});

const obterEventoTipoTexto = (solic: any) => {
  if (solic.evento_tipo === 'CANCELAMENTO' || (solic.status === 'CANCELADO' && (solic.detalhes?.toLowerCase().includes('cancelou') || solic.evento_tipo === 'CANCELAMENTO'))) {
    return 'Cancelamento de Solicitação';
  }
  if (solic.evento_tipo === 'RESPOSTA' || solic.is_resposta) {
    return 'Resposta';
  }
  if (solic.evento_tipo === 'EXECUCAO' || solic.origem_menu === 'Pacientes' || solic.origem_menu === 'Importação Planilha') {
    return 'Execução';
  }
  if (solic.evento_tipo === 'ALTERACAO' || solic.evento_tipo === 'EDICAO') {
    return 'Alteração de Solicitação';
  }
  return 'Solicitação';
};

const extrairProcedimentoTexto = (solic: any) => {
  if (!solic.procedimento || solic.procedimento === '—' || String(solic.procedimento).trim() === '') {
    return 'NA';
  }
  if (solic.procedimento_anterior && solic.procedimento_anterior !== solic.procedimento) {
    return `${solic.procedimento_anterior} ➔ ${solic.procedimento}`;
  }
  return String(solic.procedimento).trim();
};

const extrairProntuarioTexto = (solic: any) => {
  if (solic.codigo_paciente && String(solic.codigo_paciente) !== '0' && String(solic.codigo_paciente).trim() !== '') {
    return String(solic.codigo_paciente).trim();
  }
  return 'NA';
};

const extrairPacienteTexto = (solic: any) => {
  if (solic.nome_paciente && solic.nome_paciente !== '—' && !String(solic.nome_paciente).startsWith('Paciente #0') && String(solic.nome_paciente).trim() !== '') {
    return String(solic.nome_paciente).trim();
  }
  return 'NA';
};

const extrairEspecialidadeTexto = (solic: any) => {
  if (solic.especialidade && solic.especialidade !== '—' && String(solic.especialidade).trim() !== '') {
    return String(solic.especialidade).trim();
  }
  return 'NA';
};

const extrairPerfilExecutorTexto = (solic: any) => {
  if (solic.perfil_executor && String(solic.perfil_executor).trim() !== '') {
    return String(solic.perfil_executor).trim();
  }
  return 'NA';
};

const extrairUsuarioExecutorTexto = (solic: any) => {
  const u = solic.username || solic.usuario || solic.user;
  if (u && String(u).trim() !== '' && u !== '—') {
    return String(u).trim();
  }
  return 'NA';
};

const formatarDataBR = (dtStr: string) => {
  if (!dtStr) return '—';
  const parts = dtStr.split('-');
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }
  return dtStr;
};

const executarExportacaoExcel = () => {
  if (modalExportar.value.dataInicio && modalExportar.value.dataFim && modalExportar.value.dataInicio > modalExportar.value.dataFim) {
    toast.error('A data inicial não pode ser posterior à data final.');
    return;
  }

  modalExportar.value.loading = true;

  try {
    // 1. Filtragem com base em todos os filtros ativos e no intervalo de datas do modal
    const registrosFiltrados = solicitacoes.value.filter(s => {
      // Especialidade
      if (perfisStore.perfilAtivo?.tipo === 'ESPECIALIDADE' && (perfisStore.perfilAtivo.especialidade || perfisStore.perfilAtivo.nome)) {
        const espAtiva = perfisStore.perfilAtivo.especialidade || perfisStore.perfilAtivo.nome;
        if (!(s.especialidade && isSameSpecialty(s.especialidade, espAtiva))) {
          return false;
        }
      } else if (filtroEspecialidade.value && !(s.especialidade && isSameSpecialty(s.especialidade, filtroEspecialidade.value))) {
        return false;
      }

      // Intervalo de Datas do Modal
      if (s.data_criacao) {
        const solicDataOnly = s.data_criacao.split(' ')[0];
        if (modalExportar.value.dataInicio && solicDataOnly < modalExportar.value.dataInicio) return false;
        if (modalExportar.value.dataFim && solicDataOnly > modalExportar.value.dataFim) return false;
      } else if (modalExportar.value.dataInicio || modalExportar.value.dataFim) {
        return false;
      }

      // Origem / Menu
      if (filtroOrigemMenu.value) {
        const origem = formatarOrigemMenu(s.origem_menu);
        if (origem.toLowerCase() !== filtroOrigemMenu.value.toLowerCase()) return false;
      }

      // Prontuário / Paciente
      if (filtroPaciente.value) {
        const term = filtroPaciente.value.toLowerCase();
        const codMatch = String(s.codigo_paciente || '').toLowerCase().includes(term);
        const nomeMatch = (s.nome_paciente || '').toLowerCase().includes(term);
        if (!codMatch && !nomeMatch) return false;
      }

      // Ação / Tipo
      if (filtroAcaoTipo.value) {
        if (filtroAcaoTipo.value === 'INSERIR' && !(s.tipo === 'INSERIR' || s.tipo === 'INCLUSAO')) return false;
        else if (filtroAcaoTipo.value === 'EDITAR' && !(s.tipo === 'EDITAR' || s.tipo === 'EDICAO')) return false;
        else if (filtroAcaoTipo.value === 'EXCLUIR' && !(s.tipo === 'EXCLUIR' || s.tipo === 'EXCLUSAO')) return false;
        else if (filtroAcaoTipo.value !== 'INSERIR' && filtroAcaoTipo.value !== 'EDITAR' && filtroAcaoTipo.value !== 'EXCLUIR' && s.tipo !== filtroAcaoTipo.value) return false;
      }

      // Tipo de Evento
      if (filtroEventoTipo.value) {
        const isCanc = s.evento_tipo === 'CANCELAMENTO' || (s.status === 'CANCELADO' && (s.detalhes?.toLowerCase().includes('cancelou') || s.evento_tipo === 'CANCELAMENTO'));
        const isResp = (s.evento_tipo === 'RESPOSTA' || s.is_resposta) && !isCanc;
        const isAlt = s.evento_tipo === 'ALTERACAO' || s.evento_tipo === 'EDICAO';
        const isExec = s.evento_tipo === 'EXECUCAO' || s.origem_menu === 'Pacientes' || s.origem_menu === 'Importação Planilha';
        const isSolic = (s.evento_tipo === 'SOLICITACAO' || !s.evento_tipo) && !isResp && !isAlt && !isExec && !isCanc;

        if (filtroEventoTipo.value === 'CANCELAMENTO' && !isCanc) return false;
        if (filtroEventoTipo.value === 'RESPOSTA' && !isResp) return false;
        if (filtroEventoTipo.value === 'EXECUCAO' && !isExec) return false;
        if (filtroEventoTipo.value === 'ALTERACAO' && !isAlt) return false;
        if (filtroEventoTipo.value === 'SOLICITACAO' && !isSolic) return false;
      }

      // Status
      if (filtroStatus.value && s.status !== filtroStatus.value) {
        return false;
      }

      // Usuário Executor
      if (filtroUsuario.value) {
        const termUser = filtroUsuario.value.toLowerCase();
        const uName = (s.username || s.usuario || s.user || '').toLowerCase();
        if (!uName.includes(termUser)) return false;
      }

      return true;
    }).sort((a, b) => {
      const dataA = a.data_criacao || '';
      const dataB = b.data_criacao || '';
      if (dataA && dataB) return dataB.localeCompare(dataA);
      if (dataA && !dataB) return -1;
      if (!dataA && dataB) return 1;
      return 0;
    });

    if (registrosFiltrados.length === 0) {
      toast.warning('Nenhum registro encontrado para os filtros e intervalo selecionados.');
      modalExportar.value.loading = false;
      return;
    }

    // 2. Metadados do cabeçalho
    const agora = new Date();
    const agoraFormatado = `${String(agora.getDate()).padStart(2, '0')}/${String(agora.getMonth() + 1).padStart(2, '0')}/${agora.getFullYear()} ${String(agora.getHours()).padStart(2, '0')}:${String(agora.getMinutes()).padStart(2, '0')}:${String(agora.getSeconds()).padStart(2, '0')}`;
    const intervaloTexto = `${formatarDataBR(modalExportar.value.dataInicio)} até ${formatarDataBR(modalExportar.value.dataFim)}`;
    const textoFiltros = resumoFiltrosAtivos.value || 'Nenhum outro filtro aplicado';

    // 3. Montagem das 11 colunas exatas
    const linhasDados = registrosFiltrados.map(solic => [
      solic.data_criacao ? formatarDataHora(solic.data_criacao) : 'NA',
      formatarOrigemMenu(solic.origem_menu) || 'NA',
      extrairProntuarioTexto(solic),
      extrairPacienteTexto(solic),
      extrairEspecialidadeTexto(solic),
      extrairProcedimentoTexto(solic),
      formatarTipo(solic.tipo) || 'NA',
      obterEventoTipoTexto(solic),
      solic.status || 'CONCLUIDO',
      extrairPerfilExecutorTexto(solic),
      extrairUsuarioExecutorTexto(solic)
    ]);

    const cabecalhoTabela = [
      'DATA/HORA',
      'ORIGEM/MENU',
      'PRONTUÁRIO',
      'PACIENTE',
      'ESPECIALIDADE',
      'PROCEDIMENTO',
      'AÇÃO',
      'TIPO DE EVENTO',
      'STATUS',
      'PERFIL EXECUTOR',
      'USUÁRIO EXECUTOR'
    ];

    const aoa = [
      ['SISTEMA COMUNICAÇÃO CIRÚRGICA HC-UFPE - RELATÓRIO DO HISTÓRICO DE AÇÕES'],
      [`Data/Hora da Exportação: ${agoraFormatado}`],
      [`Intervalo da Exportação: ${intervaloTexto}`],
      [`Filtros Aplicados: ${textoFiltros}`],
      [], // Linha em branco separando os metadados da tabela
      cabecalhoTabela,
      ...linhasDados
    ];

    // 4. Criação e estilização da planilha com xlsx-js-style
    const ws = XLSX.utils.aoa_to_sheet(aoa);

    // Linha 1 a 4: Informações institucionais e metadados em negrito
    ['A1', 'A2', 'A3', 'A4'].forEach((cellRef, idx) => {
      if (ws[cellRef]) {
        ws[cellRef].s = {
          font: {
            name: 'Calibri',
            sz: idx === 0 ? 12 : 10,
            bold: true,
            color: { rgb: idx === 0 ? '0F172A' : '334155' }
          }
        };
      }
    });

    // Colunas da tabela (A até K)
    const colunas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'];

    // Linha 6: Cabeçalho da tabela com formato de tabela em negrito
    colunas.forEach(col => {
      const cellRef = `${col}6`;
      if (ws[cellRef]) {
        ws[cellRef].s = {
          font: { name: 'Calibri', sz: 10, bold: true, color: { rgb: 'FFFFFF' } },
          fill: { fgColor: { rgb: '1E3A8A' } },
          alignment: { vertical: 'center', horizontal: 'center', wrapText: true },
          border: {
            top: { style: 'thin', color: { rgb: '0F172A' } },
            bottom: { style: 'medium', color: { rgb: '0F172A' } },
            left: { style: 'thin', color: { rgb: '1E3A8A' } },
            right: { style: 'thin', color: { rgb: '1E3A8A' } }
          }
        };
      }
    });

    // Linhas de dados (linhas 7 até total): formatação com bordas finas e zebrado
    const totalLinhas = 6 + linhasDados.length;
    for (let r = 7; r <= totalLinhas; r++) {
      colunas.forEach((col, cIdx) => {
        const cellRef = `${col}${r}`;
        if (ws[cellRef]) {
          const isCenter = [1, 2, 6, 7, 8].includes(cIdx); // ORIGEM/MENU, PRONTUÁRIO, AÇÃO, TIPO DE EVENTO, STATUS
          ws[cellRef].s = {
            font: { name: 'Calibri', sz: 10, color: { rgb: '1E293B' } },
            fill: { fgColor: { rgb: r % 2 === 0 ? 'F8FAFC' : 'FFFFFF' } },
            alignment: {
              vertical: 'center',
              horizontal: isCenter ? 'center' : 'left'
            },
            border: {
              top: { style: 'thin', color: { rgb: 'E2E8F0' } },
              bottom: { style: 'thin', color: { rgb: 'E2E8F0' } },
              left: { style: 'thin', color: { rgb: 'E2E8F0' } },
              right: { style: 'thin', color: { rgb: 'E2E8F0' } }
            }
          };
        }
      });
    }

    // Configuração de autofiltro na tabela (linha 6 com setas de filtro ativas até a última linha de dados)
    ws['!autofilter'] = { ref: `A6:K${totalLinhas}` };

    // Largura das colunas para visualização ideal
    ws['!cols'] = [
      { wch: 18 }, // DATA/HORA
      { wch: 18 }, // ORIGEM/MENU
      { wch: 14 }, // PRONTUÁRIO
      { wch: 32 }, // PACIENTE
      { wch: 22 }, // ESPECIALIDADE
      { wch: 36 }, // PROCEDIMENTO
      { wch: 28 }, // AÇÃO
      { wch: 25 }, // TIPO DE EVENTO
      { wch: 14 }, // STATUS
      { wch: 22 }, // PERFIL EXECUTOR
      { wch: 20 }  // USUÁRIO EXECUTOR
    ];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Histórico');

    const nomeArquivo = `Historico_ComCir_${agora.getFullYear()}-${String(agora.getMonth() + 1).padStart(2, '0')}-${String(agora.getDate()).padStart(2, '0')}_${String(agora.getHours()).padStart(2, '0')}-${String(agora.getMinutes()).padStart(2, '0')}.xlsx`;
    XLSX.writeFile(wb, nomeArquivo);

    toast.success(`Exportação concluída com sucesso! ${registrosFiltrados.length} registros exportados.`);
    fecharModalExportar();
  } catch (err: any) {
    console.error('Erro ao exportar histórico para Excel:', err);
    toast.error('Erro ao gerar o arquivo Excel: ' + (err?.message || 'erro inesperado'));
  } finally {
    modalExportar.value.loading = false;
  }
};

const normalizeEsp = (e?: string) => {
  if (!e) return '';
  const n = e.normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().toUpperCase();
  if (n === 'CIRURGIA GERAL' || n === 'CIRURGIA_GERAL') return 'GERAL';
  return n;
};

const isSameSpecialty = (e1?: string, e2?: string) => {
  if (!e1 || !e2) return false;
  return normalizeEsp(e1) === normalizeEsp(e2);
};

const isBucoMaxiloEsp = (esp?: string) => {
  if (!esp) return false;
  return normalizeEsp(esp).includes('BUCOMAXILO');
};

// Filtros
const filtroEspecialidade = ref('');
const dataInicio = ref('');
const dataFim = ref('');
const filtroOrigemMenu = ref('');
const filtroPaciente = ref('');
const filtroAcaoTipo = ref('');
const filtroEventoTipo = ref('');
const filtroStatus = ref('');
const filtroUsuario = ref('');

watch(() => perfisStore.perfilAtivo, (newProfile) => {
  if (newProfile?.tipo === 'ESPECIALIDADE' && (newProfile.especialidade || newProfile.nome)) {
    filtroEspecialidade.value = normalizeEsp(newProfile.especialidade || newProfile.nome);
  }
}, { immediate: true });

const especialidadesDisponiveis = computed(() => {
  const perfisEspecialidades = perfisStore.perfis
    .filter(p => p.tipo === 'ESPECIALIDADE')
    .map(p => normalizeEsp(p.especialidade || p.nome))
    .filter(Boolean);

  const solicitacoesEsp = solicitacoes.value
    .map(s => normalizeEsp(s.especialidade))
    .filter((e): e is string => Boolean(e) && e !== '—');

  return Array.from(new Set([...perfisEspecialidades, ...solicitacoesEsp])).sort((a, b) => a.localeCompare(b, 'pt-BR'));
});

const limparFiltros = () => {
  if (perfisStore.perfilAtivo?.tipo === 'ESPECIALIDADE' && (perfisStore.perfilAtivo.especialidade || perfisStore.perfilAtivo.nome)) {
    filtroEspecialidade.value = normalizeEsp(perfisStore.perfilAtivo.especialidade || perfisStore.perfilAtivo.nome);
  } else {
    filtroEspecialidade.value = '';
  }
  dataInicio.value = '';
  dataFim.value = '';
  filtroOrigemMenu.value = '';
  filtroPaciente.value = '';
  filtroAcaoTipo.value = '';
  filtroEventoTipo.value = '';
  filtroStatus.value = '';
  filtroUsuario.value = '';
  paginaAtual.value = 1;
};

const carregarHistorico = async () => {
  loading.value = true;
  try {
    const [solicRes, pacRes, userRes] = await Promise.allSettled([
      api.get('/api/solicitacoes'),
      api.get('/api/pacientes'),
      api.get('/api/usuarios')
    ]);

    const solicitacoesData = solicRes.status === 'fulfilled' ? solicRes.value.data : [];
    const pacientesData = pacRes.status === 'fulfilled' ? pacRes.value.data : [];
    usuariosLocais.value = userRes.status === 'fulfilled' ? userRes.value.data : [];
    pacientesBase.value = pacientesData;

    const pacMap = new Map<string, string>();
    for (const p of pacientesData) {
      const cod = String(p.codigo || p.prontuario || '').trim();
      const nome = p.nome || p.nome_paciente;
      if (cod && nome) {
        pacMap.set(cod, nome);
      }
    }

    // Mapa com o status da solicitação principal para manter sincronizado com suas alterações
    const statusMap = new Map<string, string>();
    for (const s of solicitacoesData) {
      if (s.evento_tipo === 'SOLICITACAO' || !s.evento_tipo) {
        statusMap.set(String(s.id), s.status);
      }
    }

    solicitacoes.value = solicitacoesData.map((s: any) => {
      const codStr = String(s.codigo_paciente || s.codigo || s.prontuario || '').trim();
      let nomeReal = s.nome_paciente || s.nome;
      if (!nomeReal || nomeReal.startsWith('Paciente #') || nomeReal === 'Não informado') {
        if (pacMap.has(codStr) && codStr !== '0') {
          nomeReal = pacMap.get(codStr);
        }
      }

      // Se for alteração de solicitação, sincroniza o status com a solicitação original
      let statusFinal = s.status;
      if (s.evento_tipo === 'ALTERACAO' || s.evento_tipo === 'EDICAO') {
        const matchId = (s.detalhes || '').match(/solicitação\s+#([a-zA-Z0-9_-]+)/i);
        if (matchId && matchId[1] && statusMap.has(matchId[1])) {
          statusFinal = statusMap.get(matchId[1]);
        }
      }

      return {
        ...s,
        status: statusFinal,
        nome_paciente: nomeReal || (codStr && codStr !== '0' ? `Paciente #${codStr}` : '—')
      };
    });
  } catch (error) {
    toast.error('Erro ao carregar o histórico de solicitações.');
  } finally {
    loading.value = false;
  }
};

const formatarOrigemMenu = (origem?: string) => {
  if (!origem || origem === 'Sistema LEC') return 'Solicitações LEC';
  if (origem === 'Importação Planilha' || origem === 'Pacientes') return 'Pacientes';
  if (origem === 'Perfis' || origem === 'Usuários') return 'Usuários';
  return origem;
};

const formatarDataHora = (dataStr: string) => {
  if (!dataStr) return '—';
  try {
    const cleaned = String(dataStr).trim().replace('T', ' ');
    const parts = cleaned.split(' ');
    const dataPart = parts[0];
    const horaPart = parts[1] || '';

    let dataFormatada = dataPart;
    if (dataPart.includes('-')) {
      const p = dataPart.split('-');
      if (p[0].length === 4) {
        dataFormatada = `${p[2]}-${p[1]}-${p[0]}`;
      } else {
        dataFormatada = `${p[0]}-${p[1]}-${p[2]}`;
      }
    } else if (dataPart.includes('/')) {
      const p = dataPart.split('/');
      if (p[0].length === 4) {
        dataFormatada = `${p[2]}-${p[1]}-${p[0]}`;
      } else {
        dataFormatada = `${p[0]}-${p[1]}-${p[2]}`;
      }
    }

    let horaFormatada = '';
    if (horaPart) {
      const hParts = horaPart.split(':');
      if (hParts.length >= 2) {
        horaFormatada = `${hParts[0].padStart(2, '0')}:${hParts[1].padStart(2, '0')}`;
      }
    }

    return horaFormatada ? `${dataFormatada} ${horaFormatada}` : dataFormatada;
  } catch (e) {
    return dataStr;
  }
};

const formatarTipo = (tipo: string) => {
  switch (tipo) {
    case 'INSERIR':
    case 'INCLUSAO': return 'Inclusão de Procedimento';
    case 'EDITAR':
    case 'EDICAO': return 'Edição de Procedimento';
    case 'EXCLUIR':
    case 'EXCLUSAO': return 'Exclusão de Procedimento';
    case 'STANDBY': return 'Standby de Procedimento';
    case 'CANCELAR_STANDBY': return 'Cancelamento de Standby';
    case 'SOLICITAR_APA':
    case 'APA': return 'Solicitação APA';
    
    // Ações do menu Perfis
    case 'CRIAR_PERFIL': return 'Criação de Perfil';
    case 'EXCLUIR_PERFIL': return 'Exclusão de Perfil';
    case 'CRIAR_USUARIO': return 'Criação de Usuário';
    case 'EDITAR_USUARIO': return 'Edição de Usuário';
    case 'EXCLUIR_USUARIO': return 'Exclusão de Usuário';
    case 'CRIAR_CATEGORIZACAO': return 'Criação de Categorização';
    case 'EDITAR_CATEGORIZACAO': return 'Edição de Categorização';
    case 'EXCLUIR_CATEGORIZACAO': return 'Exclusão de Categorização';
    
    default: return tipo;
  }
};

const getTipoBadgeClass = (tipo: string) => {
  switch (tipo) {
    // Procedimentos
    case 'INSERIR':
    case 'INCLUSAO': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-green-800 border border-green-200';
    case 'EDITAR':
    case 'EDICAO': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200';
    case 'EXCLUIR':
    case 'EXCLUSAO': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-800 border border-red-200';
    case 'STANDBY': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-yellow-100 text-yellow-800 border border-yellow-200';
    case 'CANCELAR_STANDBY': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200';
    case 'SOLICITAR_APA':
    case 'APA': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200';
    
    // Perfis (Lilás)
    case 'CRIAR_PERFIL': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-300';
    case 'EXCLUIR_PERFIL': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-red-700 border border-purple-300';
    
    // Usuários (Laranja Claro)
    case 'CRIAR_USUARIO': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-orange-100 text-orange-800 border border-orange-300';
    case 'EDITAR_USUARIO': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-orange-100 text-blue-800 border border-orange-300';
    case 'EXCLUIR_USUARIO': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-orange-100 text-red-700 border border-orange-300';
    
    // Categorização (Marrom Claro)
    case 'CRIAR_CATEGORIZACAO': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300';
    case 'EDITAR_CATEGORIZACAO': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-blue-800 border border-amber-300';
    case 'EXCLUIR_CATEGORIZACAO': return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-red-700 border border-amber-300';
    
    default: return 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-800';
  }
};

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'PENDENTE': return 'px-2 py-0.5 text-[10px] font-bold rounded bg-yellow-100 text-yellow-800 border border-yellow-200';
    case 'APROVADO': return 'px-2 py-0.5 text-[10px] font-bold rounded bg-green-100 text-green-800 border border-green-200';
    case 'CONCLUIDO': return 'px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-100 text-emerald-800 border border-emerald-200';
    case 'REJEITADO': return 'px-2 py-0.5 text-[10px] font-bold rounded bg-red-100 text-red-800 border border-red-200';
    case 'CANCELADO': return 'px-2 py-0.5 text-[10px] font-bold rounded bg-gray-100 text-gray-800 border border-gray-300';
    default: return 'px-2 py-0.5 text-[10px] font-bold rounded bg-gray-100 text-gray-800';
  }
};

const getSwalisClass = (swallis?: string) => {
  const base = 'px-2 py-0.5 rounded font-bold text-xs inline-block';
  switch (swallis) {
    case 'A1': return `${base} bg-red-100 text-red-800 border border-red-200`;
    case 'A2': return `${base} bg-orange-100 text-orange-800 border border-orange-200`;
    case 'B':  return `${base} bg-yellow-100 text-yellow-800 border border-yellow-200`;
    case 'C':  return `${base} bg-blue-100 text-blue-800 border border-blue-200`;
    case 'D':  return `${base} bg-gray-100 text-gray-700 border border-gray-200`;
    default:   return `${base} bg-gray-100 text-gray-700 border border-gray-200`;
  }
};

// Extrai o alvo da ação do menu Usuários (Nome do Médico da Categorização, Nome/Username do Usuário, ou Nome do Perfil)
const obterAlvoAcaoPerfis = (solic: any) => {
  if (!solic) return '';
  const tipo = (solic.tipo || '').toUpperCase();
  const origem = formatarOrigemMenu(solic.origem_menu);
  
  const isMenuPerfis = origem === 'Usuários' || tipo.startsWith('CRIAR_') || tipo.startsWith('EDITAR_') || tipo.startsWith('EXCLUIR_');
  if (!isMenuPerfis) return '';
  
  const det = solic.detalhes || '';
  
  // 1. Categorização
  if (tipo.includes('CATEGORIZACAO')) {
    const matchCat = det.match(/profissional\s+([A-Za-zÀ-ÿ\s.'-]+?)(?:\s+na especialidade|\s+editad|\s+excluíd|:|$)/i);
    if (matchCat && matchCat[1]) {
      return matchCat[1].trim();
    }
  }
  
  // 2. Usuário
  if (tipo.includes('USUARIO')) {
    const matchUserComNome = det.match(/usuário\s+"?([^"(]+?)"?\s*\(([^)]+)\)/i);
    if (matchUserComNome) {
      const uName = matchUserComNome[2].trim();
      const uLogin = matchUserComNome[1].trim();
      return uName || uLogin;
    }
    const matchUser = det.match(/usuário\s+"([^"]+)"/i);
    if (matchUser && matchUser[1]) {
      return matchUser[1].trim();
    }
  }
  
  // 3. Perfil
  if (tipo.includes('PERFIL')) {
    const matchPerfil = det.match(/perfil\s+"([^"]+)"/i);
    if (matchPerfil && matchPerfil[1]) {
      return matchPerfil[1].trim();
    }
  }
  
  return '';
};

const isAcaoProcedimento = (solic: any) => {
  if (!solic) return false;
  const t = (solic.tipo || '').toUpperCase();
  return t === 'INSERIR' || t === 'INCLUSAO' || t === 'EDITAR' || t === 'EDICAO' || t === 'EXCLUIR' || t === 'EXCLUSAO' || t === 'STANDBY' || t === 'CANCELAR_STANDBY' || t === 'SOLICITAR_APA' || t === 'APA';
};

const isAcaoEdicaoProcedimento = (solic: any) => {
  if (!solic) return false;
  const t = (solic.tipo || '').toUpperCase();
  const ev = (solic.evento_tipo || '').toUpperCase();
  return t === 'EDITAR' || t === 'EDICAO' || ev === 'ALTERACAO' || ev === 'EDICAO' || (solic.detalhes && (solic.detalhes.includes('->') || solic.detalhes.includes('➔')));
};

// Reconstrói estado anterior do paciente para apurar mudanças
const obterEstadoAnterior = (solic: any) => {
  if (!solic) return { especialidade: '', procedimento: '', judicializado: 'Não', swalis: '', medico_responsavel: '', categorizacao: '', lateralidade: 'Indefinida' };

  const targetProc = (solic.procedimento_anterior || solic.procedimento || '').trim().toLowerCase();
  const espTarget = (solic.especialidade || '').trim();

  const pacienteBase = pacientesBase.value.find(p => 
    String(p.prontuario || p.codigo) === String(solic.codigo_paciente) &&
    (espTarget ? isSameSpecialty(p.especialidade, espTarget) : true) &&
    (targetProc ? (p.procedimento || '').toLowerCase().trim() === targetProc : true)
  ) || pacientesBase.value.find(p => String(p.prontuario || p.codigo) === String(solic.codigo_paciente));
  
  let estado = {
    especialidade: pacienteBase ? pacienteBase.especialidade : '',
    procedimento: pacienteBase ? pacienteBase.procedimento : '',
    judicializado: pacienteBase ? (pacienteBase.judicializado || 'Não') : 'Não',
    swalis: pacienteBase ? (pacienteBase.swalis || pacienteBase.swallis || pacienteBase.Swalis || '') : '',
    medico_responsavel: pacienteBase ? (pacienteBase.medico_responsavel || '') : '',
    categorizacao: pacienteBase ? (pacienteBase.categorizacao || '') : '',
    lateralidade: pacienteBase ? (pacienteBase.lateralidade || 'Indefinida') : 'Indefinida'
  };
  
  const aprovadasAnteriores = solicitacoes.value
    .filter(s => 
      String(s.codigo_paciente) === String(solic.codigo_paciente) && 
      s.status === 'APROVADO' && 
      (s.data_criacao || '') < (solic.data_criacao || '') &&
      (espTarget ? isSameSpecialty(s.especialidade, espTarget) : true) &&
      (targetProc ? (
        (s.procedimento || '').toLowerCase().trim() === targetProc || 
        (s.procedimento_anterior || '').toLowerCase().trim() === targetProc
      ) : true)
    )
    .sort((a, b) => (a.data_criacao || '').localeCompare(b.data_criacao || ''));
    
  for (const s of aprovadasAnteriores) {
    if (s.tipo === 'INSERIR' || s.tipo === 'INCLUSAO') {
      estado.especialidade = s.especialidade;
      estado.procedimento = s.procedimento;
      estado.judicializado = s.judicializado || 'Não';
      estado.swalis = s.swalis || s.swallis || s.Swalis || '';
      estado.medico_responsavel = s.medico_responsavel || '';
      estado.categorizacao = s.categorizacao || '';
      estado.lateralidade = s.lateralidade || 'Indefinida';
    } else if (s.tipo === 'EDITAR' || s.tipo === 'EDICAO') {
      if (s.especialidade) estado.especialidade = s.especialidade;
      if (s.procedimento) estado.procedimento = s.procedimento;
      if (s.judicializado) estado.judicializado = s.judicializado;
      const sw = s.swalis || s.swallis || s.Swalis;
      if (sw) estado.swalis = sw;
      if (s.medico_responsavel) estado.medico_responsavel = s.medico_responsavel;
      if (s.categorizacao !== undefined) estado.categorizacao = s.categorizacao || '';
      if (s.lateralidade !== undefined) estado.lateralidade = s.lateralidade || 'Indefinida';
    }
  }
  
  if (solic.procedimento_anterior) {
    estado.procedimento = solic.procedimento_anterior;
  }
  
  return estado;
};

const obterMudancaCampo = (solic: any, campo: string) => {
  if (!solic) return null;
  const estAnt = obterEstadoAnterior(solic);
  
  if (campo === 'procedimento') {
    const ant = (solic.procedimento_anterior || estAnt.procedimento || '').trim();
    const novo = (solic.procedimento || '').trim();
    if (ant && novo && ant !== novo) {
      return { anterior: ant, novo };
    }
  } else if (campo === 'judicializado') {
    const ant = (estAnt.judicializado || 'Não').trim();
    const novo = (solic.judicializado || 'Não').trim();
    if (ant && novo && ant !== novo) {
      return { anterior: ant, novo };
    }
  } else if (campo === 'swalis') {
    const ant = (estAnt.swalis || '').trim();
    const novo = (solic.swalis || solic.swallis || solic.Swalis || '').trim();
    if (ant && novo && ant !== novo) {
      return { anterior: ant, novo };
    }
  } else if (campo === 'medico_responsavel') {
    const ant = (estAnt.medico_responsavel || '').trim();
    const novo = (solic.medico_responsavel || '').trim();
    if (ant && novo && ant.toLowerCase() !== novo.toLowerCase()) {
      return { anterior: ant, novo };
    }
  } else if (campo === 'especialidade') {
    const ant = (estAnt.especialidade || '').trim();
    const novo = (solic.especialidade || '').trim();
    if (ant && novo && !isSameSpecialty(ant, novo)) {
      return { anterior: ant, novo };
    }
  } else if (campo === 'lateralidade') {
    const ant = (estAnt.lateralidade || 'Indefinida').trim();
    const novo = (solic.lateralidade || 'Indefinida').trim();
    if (ant.toLowerCase() !== novo.toLowerCase()) {
      return { anterior: ant, novo };
    }
  } else if (campo === 'categorizacao') {
    const ant = (estAnt.categorizacao || '').trim();
    const novo = (solic.categorizacao || '').trim();
    if (ant !== novo) {
      return { anterior: ant || 'Sem categorização', novo: novo || 'Sem categorização' };
    }
  }
  return null;
};

// Parser textual para extrair quaisquer alterações gravadas no padrão "Campo: val1 -> val2"
const parsearMudancasDeTexto = (detalhes?: string) => {
  if (!detalhes) return [];
  const mudancas: { campo: string; anterior: string; novo: string }[] = [];
  
  const regex = /([A-Za-zÀ-ÿ\s/()_-]+):\s*([^->\n;]+?)\s*(?:->|➔)\s*([^;\n.]+)/g;
  let match;
  while ((match = regex.exec(detalhes)) !== null) {
    const campo = match[1].trim();
    const ant = match[2].trim();
    const novo = match[3].trim();
    if (campo && (ant || novo)) {
      mudancas.push({ campo, anterior: ant || '—', novo: novo || '—' });
    }
  }
  return mudancas;
};

const obterMudancasCompletas = (solic: any) => {
  if (!solic) return [];
  const mudancasCalculadas: { campo: string; anterior: string; novo: string }[] = [];

  const mProc = obterMudancaCampo(solic, 'procedimento');
  if (mProc) mudancasCalculadas.push({ campo: 'Procedimento', anterior: mProc.anterior, novo: mProc.novo });

  const mEsp = obterMudancaCampo(solic, 'especialidade');
  if (mEsp) mudancasCalculadas.push({ campo: 'Especialidade', anterior: mEsp.anterior, novo: mEsp.novo });

  const mJud = obterMudancaCampo(solic, 'judicializado');
  if (mJud) mudancasCalculadas.push({ campo: 'Judicialização', anterior: mJud.anterior, novo: mJud.novo });

  const mSwalis = obterMudancaCampo(solic, 'swalis');
  if (mSwalis) mudancasCalculadas.push({ campo: 'Swalis (Priorização)', anterior: mSwalis.anterior, novo: mSwalis.novo });

  const mMed = obterMudancaCampo(solic, 'medico_responsavel');
  if (mMed) {
    const isBuco = isBucoMaxiloEsp(solic.especialidade);
    mudancasCalculadas.push({ campo: isBuco ? 'Dentista Responsável' : 'Médico Responsável', anterior: mMed.anterior, novo: mMed.novo });
  }

  const mLat = obterMudancaCampo(solic, 'lateralidade');
  if (mLat) mudancasCalculadas.push({ campo: 'Lateralidade', anterior: mLat.anterior, novo: mLat.novo });

  const mCat = obterMudancaCampo(solic, 'categorizacao');
  if (mCat) mudancasCalculadas.push({ campo: 'Categorização Profissional', anterior: mCat.anterior, novo: mCat.novo });

  // Combina com mudanças extraídas do texto de detalhes
  const mudancasTexto = parsearMudancasDeTexto(solic.detalhes);
  
  const mapaCampos = new Map<string, { campo: string; anterior: string; novo: string }>();
  for (const m of mudancasCalculadas) {
    mapaCampos.set(m.campo.toLowerCase().trim(), m);
  }
  for (const m of mudancasTexto) {
    const key = m.campo.toLowerCase().trim();
    if (!mapaCampos.has(key)) {
      mapaCampos.set(key, m);
    }
  }

  return Array.from(mapaCampos.values());
};

const extrairJustificativaResposta = (solic: any) => {
  if (!solic) return '—';
  const detalhes = solic.detalhes || '';
  if (detalhes.includes('Justificativa:')) {
    return detalhes.split('Justificativa:')[1].trim();
  }
  if (detalhes.includes('Motivo:')) {
    return detalhes.split('Motivo:')[1].trim();
  }
  if (solic.evento_tipo === 'RESPOSTA' || solic.is_resposta) {
    return detalhes;
  }
  return detalhes || 'Nenhuma justificativa detalhada registrada.';
};

const solicitacoesFiltradas = computed(() => {
  return solicitacoes.value
    .filter(s => {
      // 1. Especialidade
      if (perfisStore.perfilAtivo?.tipo === 'ESPECIALIDADE' && (perfisStore.perfilAtivo.especialidade || perfisStore.perfilAtivo.nome)) {
        const espAtiva = perfisStore.perfilAtivo.especialidade || perfisStore.perfilAtivo.nome;
        if (!(s.especialidade && isSameSpecialty(s.especialidade, espAtiva))) {
          return false;
        }
      } else if (filtroEspecialidade.value && !(s.especialidade && isSameSpecialty(s.especialidade, filtroEspecialidade.value))) {
        return false;
      }

      // 2. Filtro de Data
      if (s.data_criacao) {
        const solicDataOnly = s.data_criacao.split(' ')[0]; // YYYY-MM-DD
        if (dataInicio.value && solicDataOnly < dataInicio.value) return false;
        if (dataFim.value && solicDataOnly > dataFim.value) return false;
      }

      // 3. Origem / Menu
      if (filtroOrigemMenu.value) {
        const origem = formatarOrigemMenu(s.origem_menu);
        if (origem.toLowerCase() !== filtroOrigemMenu.value.toLowerCase()) return false;
      }

      // 4. Prontuário / Paciente
      if (filtroPaciente.value) {
        const term = filtroPaciente.value.toLowerCase();
        const codMatch = String(s.codigo_paciente || '').toLowerCase().includes(term);
        const nomeMatch = (s.nome_paciente || '').toLowerCase().includes(term);
        if (!codMatch && !nomeMatch) return false;
      }

      // 5. Ação / Tipo
      if (filtroAcaoTipo.value) {
        if (filtroAcaoTipo.value === 'INSERIR' && !(s.tipo === 'INSERIR' || s.tipo === 'INCLUSAO')) return false;
        else if (filtroAcaoTipo.value === 'EDITAR' && !(s.tipo === 'EDITAR' || s.tipo === 'EDICAO')) return false;
        else if (filtroAcaoTipo.value === 'EXCLUIR' && !(s.tipo === 'EXCLUIR' || s.tipo === 'EXCLUSAO')) return false;
        else if (filtroAcaoTipo.value !== 'INSERIR' && filtroAcaoTipo.value !== 'EDITAR' && filtroAcaoTipo.value !== 'EXCLUIR' && s.tipo !== filtroAcaoTipo.value) return false;
      }

      // 6. Solicitação, Execução, Alteração de Solicitação, Cancelamento de Solicitação ou Resposta
      if (filtroEventoTipo.value) {
        const isCanc = s.evento_tipo === 'CANCELAMENTO' || (s.status === 'CANCELADO' && (s.detalhes?.toLowerCase().includes('cancelou') || s.evento_tipo === 'CANCELAMENTO'));
        const isResp = (s.evento_tipo === 'RESPOSTA' || s.is_resposta) && !isCanc;
        const isAlt = s.evento_tipo === 'ALTERACAO' || s.evento_tipo === 'EDICAO';
        const isExec = s.evento_tipo === 'EXECUCAO' || s.origem_menu === 'Pacientes' || s.origem_menu === 'Importação Planilha';
        const isSolic = (s.evento_tipo === 'SOLICITACAO' || !s.evento_tipo) && !isResp && !isAlt && !isExec && !isCanc;

        if (filtroEventoTipo.value === 'CANCELAMENTO' && !isCanc) return false;
        if (filtroEventoTipo.value === 'RESPOSTA' && !isResp) return false;
        if (filtroEventoTipo.value === 'EXECUCAO' && !isExec) return false;
        if (filtroEventoTipo.value === 'ALTERACAO' && !isAlt) return false;
        if (filtroEventoTipo.value === 'SOLICITACAO' && !isSolic) return false;
      }

      // 7. Status
      if (filtroStatus.value && s.status !== filtroStatus.value) {
        return false;
      }

      // 8. Usuário Executor
      if (filtroUsuario.value) {
        const termUser = filtroUsuario.value.toLowerCase();
        const uName = (s.username || s.usuario || s.user || '').toLowerCase();
        if (!uName.includes(termUser)) return false;
      }

      return true;
    })
    // Ordena do mais recente para o mais antigo (descending)
    // Para itens sem data (início do histórico): Categorizações -> Usuários -> Perfis (no fundo de tudo)
    .sort((a, b) => {
      const dataA = a.data_criacao || '';
      const dataB = b.data_criacao || '';
      
      if (dataA && dataB) {
        return dataB.localeCompare(dataA);
      }
      
      if (dataA && !dataB) return -1;
      if (!dataA && dataB) return 1;

      // Ambos sem data: Ordem: Categorizações (topo do bloco sem data) -> Usuários -> Perfis (fundo absoluto)
      const getPriority = (item: any) => {
        if (item.tipo === 'CRIAR_PERFIL') return 3;
        if (item.tipo === 'CRIAR_USUARIO' || item.tipo === 'EDITAR_USUARIO') return 2;
        if (item.tipo === 'CRIAR_CATEGORIZACAO' || item.tipo === 'EDITAR_CATEGORIZACAO') return 1;
        return 0;
      };

      const prioA = getPriority(a);
      const prioB = getPriority(b);
      if (prioA !== prioB) {
        return prioA - prioB;
      }

      return (a.detalhes || '').localeCompare(b.detalhes || '');
    });
});

const solicitacoesPaginadas = computed(() => {
  const inicio = (paginaAtual.value - 1) * itensPorPagina.value;
  return solicitacoesFiltradas.value.slice(inicio, inicio + itensPorPagina.value);
});

// Reseta para a primeira página sempre que qualquer filtro de busca for alterado
watch([
  filtroEspecialidade,
  dataInicio,
  dataFim,
  filtroOrigemMenu,
  filtroPaciente,
  filtroAcaoTipo,
  filtroEventoTipo,
  filtroStatus,
  filtroUsuario,
  itensPorPagina
], () => {
  paginaAtual.value = 1;
});

onMounted(() => {
  perfisStore.fetchPerfis();
  carregarHistorico();
});
</script>
