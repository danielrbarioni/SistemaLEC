<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Histórico de Solicitações/Respostas</h1>
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
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- 1. Data De -->
          <div class="form-group">
            <label for="dataInicio" class="form-label font-semibold">Data De</label>
            <input id="dataInicio" v-model="dataInicio" type="date" class="form-control text-xs" />
          </div>

          <!-- 2. Data Até -->
          <div class="form-group">
            <label for="dataFim" class="form-label font-semibold">Data Até</label>
            <input id="dataFim" v-model="dataFim" type="date" class="form-control text-xs" />
          </div>

          <!-- 3. Origem / Menu -->
          <div class="form-group">
            <label for="filtroOrigemMenu" class="form-label font-semibold">Origem / Menu</label>
            <select id="filtroOrigemMenu" v-model="filtroOrigemMenu" class="form-control text-xs">
              <option value="">Todas</option>
              <option value="Solicitações LEC">Solicitações LEC</option>
              <option value="Perfis">Perfis</option>
              <option value="Pacientes">Pacientes</option>
            </select>
          </div>

          <!-- 4. Prontuário / Paciente -->
          <div class="form-group">
            <label for="filtroPaciente" class="form-label font-semibold">Prontuário / Paciente</label>
            <input 
              id="filtroPaciente" 
              v-model="filtroPaciente" 
              type="text" 
              placeholder="Digite o prontuário ou nome..." 
              class="form-control text-xs" 
            />
          </div>

          <!-- 5. Especialidade -->
          <div class="form-group">
            <label for="filtroEspecialidade" class="form-label font-semibold">Especialidade</label>
            <select 
              id="filtroEspecialidade" 
              v-model="filtroEspecialidade" 
              class="form-control text-xs"
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
            <label for="filtroAcaoTipo" class="form-label font-semibold">Ação</label>
            <select id="filtroAcaoTipo" v-model="filtroAcaoTipo" class="form-control text-xs">
              <option value="">Todas</option>
              <optgroup label="Menu Solicitações LEC ou Pacientes">
                <option value="INSERIR">Inclusão de Procedimento (Menu Solicitações LEC ou Pacientes)</option>
                <option value="EDITAR">Edição de Procedimento</option>
                <option value="STANDBY">Standby de Procedimento</option>
                <option value="EXCLUIR">Exclusão de Procedimento</option>
                <option value="SOLICITAR_APA">Solicitação APA</option>
              </optgroup>
              <optgroup label="Menu Perfis">
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
            <label for="filtroEventoTipo" class="form-label font-semibold">Tipo de Evento</label>
            <select id="filtroEventoTipo" v-model="filtroEventoTipo" class="form-control text-xs">
              <option value="">Todas</option>
              <option value="SOLICITACAO">Solicitação</option>
              <option value="RESPOSTA">Resposta</option>
              <option value="EXECUCAO">Execução</option>
              <option value="ALTERACAO">Alteração (Edição)</option>
            </select>
          </div>

          <!-- 8. Status -->
          <div class="form-group">
            <label for="filtroStatus" class="form-label font-semibold">Status</label>
            <select id="filtroStatus" v-model="filtroStatus" class="form-control text-xs">
              <option value="">Todos</option>
              <option value="PENDENTE">PENDENTE</option>
              <option value="APROVADO">APROVADO</option>
              <option value="REJEITADO">REJEITADO</option>
              <option value="CANCELADO">CANCELADO</option>
              <option value="CONCLUIDO">CONCLUÍDO</option>
            </select>
          </div>

          <!-- 9. Usuário Executor -->
          <div class="form-group md:col-span-4">
            <label for="filtroUsuario" class="form-label font-semibold">Usuário Executor</label>
            <input 
              id="filtroUsuario" 
              v-model="filtroUsuario" 
              type="text" 
              placeholder="Digite o nome de usuário (ex.: nome.sobrenome)..." 
              class="form-control text-xs" 
            />
          </div>
        </div>
      </div>
    </Card>

    <!-- Lista de Solicitações/Respostas -->
    <Card>
      <div v-if="loading" class="flex justify-center items-center py-8">
        <LoadingIndicator />
      </div>
      <div v-else-if="solicitacoesFiltradas.length === 0" class="text-center py-10 text-gray-500">
        Nenhuma solicitação ou resposta encontrada para os filtros selecionados.
      </div>
      <div v-else class="overflow-x-auto max-h-[calc(100vh-280px)] overflow-y-auto border border-gray-100 rounded-lg">
        <table class="min-w-full divide-y divide-gray-200 border-separate border-spacing-0">
          <thead class="bg-gray-50 sticky top-0 z-10 shadow-sm">
            <tr>
              <th class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200">Data / Hora</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200">Origem / Menu</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200">Prontuário / Paciente</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200">Especialidade / Procedimento</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200">Ação</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200">Tipo de Evento</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200">Status</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200">Perfil Executor / Usuário Executor</th>
              <th class="sticky top-0 bg-gray-50 z-10 px-4 py-3 text-center text-xs font-bold text-gray-600 uppercase tracking-wider border-b border-gray-200">Descrição da Ação</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200 text-sm">
            <tr v-for="solic in solicitacoesFiltradas" :key="solic.id" class="hover:bg-slate-50/70 transition-colors">
              <!-- 1. Data/Hora -->
              <td class="px-4 py-4 whitespace-nowrap text-xs font-mono text-gray-600">
                {{ formatarDataHora(solic.data_criacao) }}
              </td>

              <!-- 2. Origem/Menu -->
              <td class="px-4 py-4 whitespace-nowrap text-xs font-semibold text-indigo-700">
                <span class="px-2 py-1 rounded bg-indigo-50 border border-indigo-100">
                  {{ formatarOrigemMenu(solic.origem_menu) }}
                </span>
              </td>

              <!-- 3. Prontuário/Paciente -->
              <td class="px-4 py-4 text-xs">
                <div v-if="solic.codigo_paciente && String(solic.codigo_paciente) !== '0'" class="font-mono font-semibold text-gray-800">
                  #{{ solic.codigo_paciente }}
                </div>
                <div class="text-gray-900 font-medium">
                  {{ solic.nome_paciente && solic.nome_paciente !== '—' && !String(solic.nome_paciente).startsWith('Paciente #0') ? solic.nome_paciente : '—' }}
                </div>
              </td>

              <!-- 4. Especialidade/Procedimento -->
              <td class="px-4 py-4 text-xs text-gray-700 max-w-xs break-words whitespace-normal leading-snug">
                <div class="font-semibold">{{ solic.especialidade || '—' }}</div>
                <div v-if="solic.procedimento && solic.procedimento !== '—'" class="text-gray-600 mt-0.5">
                  <span v-if="solic.procedimento_anterior && solic.procedimento_anterior !== solic.procedimento" class="text-gray-400 line-through mr-1">
                    {{ solic.procedimento_anterior }}
                  </span>
                  <span v-if="solic.procedimento_anterior && solic.procedimento_anterior !== solic.procedimento" class="font-bold text-blue-700 mr-1">
                    ➔
                  </span>
                  <span :class="solic.procedimento_anterior && solic.procedimento_anterior !== solic.procedimento ? 'font-bold text-blue-800' : ''">
                    {{ solic.procedimento }}
                  </span>
                </div>
              </td>

              <!-- 5. Ação/Tipo -->
              <td class="px-4 py-4 whitespace-nowrap">
                <span :class="getTipoBadgeClass(solic.tipo)">{{ formatarTipo(solic.tipo) }}</span>
              </td>

              <!-- 6. Solicitação, Alteração, Execução ou Resposta -->
              <td class="px-4 py-4 text-xs text-gray-600 max-w-xs" :title="solic.detalhes">
                <div class="flex items-center space-x-1.5 mb-1">
                  <span v-if="solic.evento_tipo === 'RESPOSTA' || solic.is_resposta" class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200">
                    Resposta
                  </span>
                  <span v-else-if="solic.evento_tipo === 'EXECUCAO' || solic.origem_menu === 'Pacientes' || solic.origem_menu === 'Importação Planilha'" class="px-2 py-0.5 rounded text-[10px] font-bold bg-teal-100 text-teal-800 border border-teal-200">
                    Execução
                  </span>
                  <span v-else-if="solic.evento_tipo === 'ALTERACAO' || solic.evento_tipo === 'EDICAO'" class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                    ✏️ Alteração
                  </span>
                  <span v-else class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200">
                    Solicitação
                  </span>
                </div>
                <div class="truncate font-mono text-[11px]">{{ solic.detalhes || '—' }}</div>
              </td>

              <!-- 7. Status -->
              <td class="px-4 py-4 whitespace-nowrap">
                <span :class="getStatusBadgeClass(solic.status)">{{ solic.status }}</span>
              </td>

              <!-- 8. Perfil executor/Usuário Executor (Usuário Ebserh) -->
              <td class="px-4 py-4 text-xs">
                <div v-if="solic.perfil_executor" class="mb-0.5">
                  <span class="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-semibold border border-slate-200">
                    {{ solic.perfil_executor }}
                  </span>
                </div>
                <div class="text-indigo-900 font-mono font-medium">
                  {{ solic.username || solic.usuario || solic.user || '—' }}
                </div>
              </td>

              <!-- 9. Descrição da Ação (Clicável) -->
              <td class="px-4 py-4 whitespace-nowrap text-center text-xs">
                <button 
                  @click="abrirModalDetalhes(solic)"
                  class="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 hover:text-indigo-900 font-semibold border border-indigo-200 transition-colors shadow-xs cursor-pointer"
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
                <span v-if="modalDetalhes.solic.evento_tipo === 'RESPOSTA' || modalDetalhes.solic.is_resposta" class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200">
                  Resposta
                </span>
                <span v-else-if="modalDetalhes.solic.evento_tipo === 'EXECUCAO' || modalDetalhes.solic.origem_menu === 'Pacientes'" class="px-2 py-0.5 rounded text-[10px] font-bold bg-teal-100 text-teal-800 border border-teal-200">
                  Execução
                </span>
                <span v-else-if="modalDetalhes.solic.evento_tipo === 'ALTERACAO' || modalDetalhes.solic.evento_tipo === 'EDICAO'" class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                  ✏️ Alteração
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

              <div v-if="modalDetalhes.solic.tempo_standby">
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Tempo de Standby:</span>
                <span class="font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded border border-amber-300">
                  {{ modalDetalhes.solic.tempo_standby }} dias
                </span>
              </div>

              <div class="col-span-2">
                <span class="font-bold text-gray-500 uppercase text-[10px] block">Médico Responsável:</span>
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

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import api from '../services/api';
import Card from '../components/Card.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';
import { usePerfisStore } from '../stores/perfis';

const toast = useToast();
const perfisStore = usePerfisStore();

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
    filtroEspecialidade.value = newProfile.especialidade || newProfile.nome;
  }
}, { immediate: true });

const especialidadesDisponiveis = computed(() => {
  const perfisEspecialidades = perfisStore.perfis
    .filter(p => p.tipo === 'ESPECIALIDADE')
    .map(p => p.especialidade || p.nome)
    .filter(Boolean);

  const solicitacoesEsp = solicitacoes.value
    .map(s => s.especialidade)
    .filter((e): e is string => Boolean(e) && e !== '—');

  return Array.from(new Set([...perfisEspecialidades, ...solicitacoesEsp])).sort((a, b) => a.localeCompare(b, 'pt-BR'));
});

const limparFiltros = () => {
  if (perfisStore.perfilAtivo?.tipo === 'ESPECIALIDADE' && (perfisStore.perfilAtivo.especialidade || perfisStore.perfilAtivo.nome)) {
    filtroEspecialidade.value = perfisStore.perfilAtivo.especialidade || perfisStore.perfilAtivo.nome;
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

    solicitacoes.value = solicitacoesData.map((s: any) => {
      const codStr = String(s.codigo_paciente || s.codigo || s.prontuario || '').trim();
      let nomeReal = s.nome_paciente || s.nome;
      if (!nomeReal || nomeReal.startsWith('Paciente #') || nomeReal === 'Não informado') {
        if (pacMap.has(codStr) && codStr !== '0') {
          nomeReal = pacMap.get(codStr);
        }
      }
      return {
        ...s,
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
    case 'INCLUSAO': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-green-800 border border-green-200';
    case 'EDITAR':
    case 'EDICAO': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200';
    case 'EXCLUIR':
    case 'EXCLUSAO': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-800 border border-red-200';
    case 'STANDBY': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-yellow-100 text-yellow-800 border border-yellow-200';
    case 'CANCELAR_STANDBY': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200';
    case 'SOLICITAR_APA':
    case 'APA': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200';
    
    // Perfis (Lilás)
    case 'CRIAR_PERFIL': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-300';
    case 'EXCLUIR_PERFIL': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-red-700 border border-purple-300';
    
    // Usuários (Laranja Claro)
    case 'CRIAR_USUARIO': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-orange-100 text-orange-800 border border-orange-300';
    case 'EDITAR_USUARIO': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-orange-100 text-blue-800 border border-orange-300';
    case 'EXCLUIR_USUARIO': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-orange-100 text-red-700 border border-orange-300';
    
    // Categorização (Marrom Claro)
    case 'CRIAR_CATEGORIZACAO': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300';
    case 'EDITAR_CATEGORIZACAO': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-blue-800 border border-amber-300';
    case 'EXCLUIR_CATEGORIZACAO': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-red-700 border border-amber-300';
    
    default: return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-800';
  }
};

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'PENDENTE': return 'px-2 py-0.5 text-xs font-semibold rounded bg-yellow-100 text-yellow-800 border border-yellow-200';
    case 'APROVADO': return 'px-2 py-0.5 text-xs font-semibold rounded bg-green-100 text-green-800 border border-green-200';
    case 'CONCLUIDO': return 'px-2 py-0.5 text-xs font-semibold rounded bg-emerald-100 text-emerald-800 border border-emerald-200';
    case 'REJEITADO': return 'px-2 py-0.5 text-xs font-semibold rounded bg-red-100 text-red-800 border border-red-200';
    case 'CANCELADO': return 'px-2 py-0.5 text-xs font-semibold rounded bg-gray-100 text-gray-800 border border-gray-300';
    default: return 'px-2 py-0.5 text-xs font-semibold rounded bg-gray-100 text-gray-800';
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
  if (!solic) return { especialidade: '', procedimento: '', judicializado: 'Não', swalis: '', medico_responsavel: '', categorizacao: '' };
  const pacienteBase = pacientesBase.value.find(p => String(p.prontuario || p.codigo) === String(solic.codigo_paciente));
  
  let estado = {
    especialidade: pacienteBase ? pacienteBase.especialidade : '',
    procedimento: pacienteBase ? pacienteBase.procedimento : '',
    judicializado: pacienteBase ? (pacienteBase.judicializado || 'Não') : 'Não',
    swalis: pacienteBase ? (pacienteBase.swalis || pacienteBase.swallis || pacienteBase.Swalis || '') : '',
    medico_responsavel: pacienteBase ? (pacienteBase.medico_responsavel || '') : '',
    categorizacao: pacienteBase ? (pacienteBase.categorizacao || '') : ''
  };
  
  const aprovadasAnteriores = solicitacoes.value
    .filter(s => 
      String(s.codigo_paciente) === String(solic.codigo_paciente) && 
      s.status === 'APROVADO' && 
      (s.data_criacao || '') < (solic.data_criacao || '')
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
    } else if (s.tipo === 'EDITAR' || s.tipo === 'EDICAO') {
      if (s.especialidade) estado.especialidade = s.especialidade;
      if (s.procedimento) estado.procedimento = s.procedimento;
      if (s.judicializado) estado.judicializado = s.judicializado;
      const sw = s.swalis || s.swallis || s.Swalis;
      if (sw) estado.swalis = sw;
      if (s.medico_responsavel) estado.medico_responsavel = s.medico_responsavel;
      if (s.categorizacao !== undefined) estado.categorizacao = s.categorizacao || '';
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
    if (ant && novo && ant !== novo) {
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
  if (mMed) mudancasCalculadas.push({ campo: 'Médico Responsável', anterior: mMed.anterior, novo: mMed.novo });

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
        const espAtivaNorm = (perfisStore.perfilAtivo.especialidade || perfisStore.perfilAtivo.nome).toLowerCase().trim();
        if (!(s.especialidade && s.especialidade.toLowerCase().includes(espAtivaNorm))) {
          return false;
        }
      } else if (filtroEspecialidade.value && !(s.especialidade && s.especialidade.toLowerCase().includes(filtroEspecialidade.value.toLowerCase()))) {
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
        let origem = (s.origem_menu || 'Solicitações LEC').trim();
        if (origem === 'Sistema LEC') origem = 'Solicitações LEC';
        if (origem === 'Importação Planilha') origem = 'Pacientes';
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

      // 6. Solicitação, Execução, Alteração ou Resposta
      if (filtroEventoTipo.value) {
        const isResp = s.evento_tipo === 'RESPOSTA' || s.is_resposta;
        const isAlt = s.evento_tipo === 'ALTERACAO' || s.evento_tipo === 'EDICAO';
        const isExec = s.evento_tipo === 'EXECUCAO' || s.origem_menu === 'Pacientes' || s.origem_menu === 'Importação Planilha';
        const isSolic = (s.evento_tipo === 'SOLICITACAO' || !s.evento_tipo) && !isResp && !isAlt && !isExec;

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

onMounted(() => {
  perfisStore.fetchPerfis();
  carregarHistorico();
});
</script>
