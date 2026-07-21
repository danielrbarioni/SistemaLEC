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
              <option value="Sistema LEC">Sistema LEC</option>
              <option value="Pacientes">Pacientes</option>
              <option value="Perfis">Perfis</option>
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
            <select id="filtroEspecialidade" v-model="filtroEspecialidade" class="form-control text-xs">
              <option value="">Todas</option>
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
              <option value="INSERIR">Inclusão</option>
              <option value="EDITAR">Edição</option>
              <option value="STANDBY">Standby</option>
              <option value="EXCLUIR">Exclusão</option>
              <option value="SOLICITAR_APA">Solicitação APA</option>
            </select>
          </div>

          <!-- 7. Solicitação ou Resposta -->
          <div class="form-group">
            <label for="filtroEventoTipo" class="form-label font-semibold">Solicitação ou Resposta</label>
            <select id="filtroEventoTipo" v-model="filtroEventoTipo" class="form-control text-xs">
              <option value="">Todas</option>
              <option value="SOLICITACAO">Solicitação</option>
              <option value="RESPOSTA">Resposta</option>
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
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data / Hora</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Origem / Menu</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prontuário / Paciente</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Especialidade / Procedimento</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ação</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Solicitação ou Resposta</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Perfil Executor / Usuário Executor</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200 text-sm">
            <tr v-for="solic in solicitacoesFiltradas" :key="solic.id">
              <!-- 1. Data/Hora -->
              <td class="px-4 py-4 whitespace-nowrap text-xs font-mono text-gray-600">
                {{ formatarDataHora(solic.data_criacao) }}
              </td>

              <!-- 2. Origem/Menu -->
              <td class="px-4 py-4 whitespace-nowrap text-xs font-semibold text-indigo-700">
                <span class="px-2 py-1 rounded bg-indigo-50 border border-indigo-100">
                  {{ solic.origem_menu || 'Sistema LEC' }}
                </span>
              </td>

              <!-- 3. Prontuário/Paciente -->
              <td class="px-4 py-4 text-xs">
                <div class="font-mono font-semibold text-gray-800">#{{ solic.codigo_paciente }}</div>
                <div class="text-gray-900 font-medium">{{ solic.nome_paciente }}</div>
              </td>

              <!-- 4. Especialidade/Procedimento -->
              <td class="px-4 py-4 text-xs text-gray-700">
                <div class="font-semibold">{{ solic.especialidade || '—' }}</div>
                <div class="text-gray-400">
                  <span v-if="solic.procedimento_anterior && solic.procedimento_anterior !== solic.procedimento">
                    {{ solic.procedimento_anterior }} ➔ 
                  </span>
                  {{ solic.procedimento || '—' }}
                </div>
              </td>

              <!-- 5. Ação/Tipo -->
              <td class="px-4 py-4 whitespace-nowrap">
                <span :class="getTipoBadgeClass(solic.tipo)">{{ formatarTipo(solic.tipo) }}</span>
              </td>

              <!-- 6. Solicitação ou Resposta -->
              <td class="px-4 py-4 text-xs text-gray-600 max-w-xs" :title="solic.detalhes">
                <div class="flex items-center space-x-1.5 mb-1">
                  <span v-if="solic.evento_tipo === 'RESPOSTA' || solic.is_resposta" class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200">
                    Resposta
                  </span>
                  <span v-else class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200">
                    Solicitação
                  </span>
                </div>
                <div class="truncate">{{ solic.detalhes || '—' }}</div>
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
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import api from '../services/api';
import Card from '../components/Card.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';
import { usePerfisStore } from '../stores/perfis';

const toast = useToast();
const perfisStore = usePerfisStore();

const solicitacoes = ref<any[]>([]);
const loading = ref(false);

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

const especialidadesDisponiveis = computed(() => {
  const perfisEspecialidades = perfisStore.perfis
    .filter(p => p.tipo === 'ESPECIALIDADE')
    .map(p => p.especialidade || p.nome)
    .filter(Boolean);

  return Array.from(new Set(perfisEspecialidades)).sort((a, b) => a.localeCompare(b, 'pt-BR'));
});

const limparFiltros = () => {
  filtroEspecialidade.value = '';
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
    const { data } = await api.get('/api/solicitacoes');
    solicitacoes.value = data;
  } catch (error) {
    toast.error('Erro ao carregar o histórico de solicitações.');
  } finally {
    loading.value = false;
  }
};

const formatarDataHora = (dataStr: string) => {
  if (!dataStr) return '—';
  try {
    const [data, hora] = dataStr.split(' ');
    const [ano, mes, dia] = data.split('-');
    return `${dia}/${mes}/${ano} ${hora.substring(0, 5)}`;
  } catch (e) {
    return dataStr;
  }
};

const formatarTipo = (tipo: string) => {
  switch (tipo) {
    case 'INSERIR': return 'Inclusão';
    case 'EDITAR': return 'Edição';
    case 'EXCLUIR': return 'Exclusão';
    case 'STANDBY': return 'Standby';
    case 'SOLICITAR_APA':
    case 'APA': return 'Solicitação APA';
    default: return tipo;
  }
};

const getTipoBadgeClass = (tipo: string) => {
  switch (tipo) {
    case 'INSERIR': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-green-800 border border-green-200';
    case 'EDITAR': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200';
    case 'EXCLUIR': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-800 border border-red-200';
    case 'STANDBY': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-yellow-100 text-yellow-800 border border-yellow-200';
    case 'SOLICITAR_APA':
    case 'APA': return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200';
    default: return 'px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-800';
  }
};

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'PENDENTE': return 'px-2 py-0.5 text-xs font-semibold rounded bg-yellow-100 text-yellow-800 border border-yellow-200';
    case 'APROVADO': return 'px-2 py-0.5 text-xs font-semibold rounded bg-green-100 text-green-800 border border-green-200';
    case 'REJEITADO': return 'px-2 py-0.5 text-xs font-semibold rounded bg-red-100 text-red-800 border border-red-200';
    default: return 'px-2 py-0.5 text-xs font-semibold rounded bg-gray-100 text-gray-800';
  }
};

const solicitacoesFiltradas = computed(() => {
  return solicitacoes.value
    .filter(s => {
      // 1. Especialidade
      if (filtroEspecialidade.value && !(s.especialidade && s.especialidade.toLowerCase().includes(filtroEspecialidade.value.toLowerCase()))) {
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
        const origem = s.origem_menu || 'Sistema LEC';
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
      if (filtroAcaoTipo.value && s.tipo !== filtroAcaoTipo.value) {
        return false;
      }

      // 6. Solicitação ou Resposta
      if (filtroEventoTipo.value) {
        const isResp = s.evento_tipo === 'RESPOSTA' || s.is_resposta;
        if (filtroEventoTipo.value === 'RESPOSTA' && !isResp) return false;
        if (filtroEventoTipo.value === 'SOLICITACAO' && isResp) return false;
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
    .sort((a, b) => b.data_criacao.localeCompare(a.data_criacao));
});

onMounted(() => {
  perfisStore.fetchPerfis();
  carregarHistorico();
});
</script>
