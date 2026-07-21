<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Histórico de Solicitações</h1>
      <span class="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full border border-gray-200">
        Acompanhamento de Ações
      </span>
    </div>

    <!-- Filtros -->
    <Card>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Filtro por Especialidade -->
        <div class="form-group">
          <label for="filtroEspecialidade" class="form-label font-semibold">Especialidade</label>
          <select id="filtroEspecialidade" v-model="filtroEspecialidade" class="form-control">
            <option value="">Todas</option>
            <option v-for="esp in especialidades" :key="esp" :value="esp">
              {{ esp }}
            </option>
          </select>
        </div>

        <!-- Filtro por Data Inicial -->
        <div class="form-group">
          <label for="dataInicio" class="form-label font-semibold">Data De</label>
          <input id="dataInicio" v-model="dataInicio" type="date" class="form-control" />
        </div>

        <!-- Filtro por Data Final -->
        <div class="form-group">
          <label for="dataFim" class="form-label font-semibold">Data Até</label>
          <input id="dataFim" v-model="dataFim" type="date" class="form-control" />
        </div>
      </div>
    </Card>

    <!-- Lista de Solicitações -->
    <Card>
      <div v-if="loading" class="flex justify-center items-center py-8">
        <LoadingIndicator />
      </div>
      <div v-else-if="solicitacoesFiltradas.length === 0" class="text-center py-10 text-gray-500">
        Nenhuma solicitação encontrada para os filtros selecionados.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data / Hora</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Origem / Menu</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prontuário / Paciente</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ação / Tipo</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Detalhes / Justificativa</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Perfil Executor</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuário Executor</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200 text-sm">
            <tr v-for="solic in solicitacoesFiltradas" :key="solic.id">
              <td class="px-4 py-4 whitespace-nowrap text-xs font-mono text-gray-600">
                {{ formatarDataHora(solic.data_criacao) }}
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-xs font-semibold text-indigo-700">
                <span class="px-2 py-1 rounded bg-indigo-50 border border-indigo-100">
                  {{ solic.origem_menu || 'Sistema LEC' }}
                </span>
              </td>
              <td class="px-4 py-4 text-xs">
                <div class="font-mono font-semibold text-gray-800">#{{ solic.codigo_paciente }}</div>
                <div class="text-gray-900 font-medium">{{ solic.nome_paciente }}</div>
              </td>
              <td class="px-4 py-4 whitespace-nowrap">
                <span :class="getTipoBadgeClass(solic.tipo)">{{ formatarTipo(solic.tipo) }}</span>
              </td>
              <td class="px-4 py-4 text-xs text-gray-700">
                <div class="font-semibold">{{ solic.especialidade || '—' }}</div>
                <div class="text-gray-400">
                  <span v-if="solic.procedimento_anterior && solic.procedimento_anterior !== solic.procedimento">
                    {{ solic.procedimento_anterior }} ➔ 
                  </span>
                  {{ solic.procedimento || '—' }}
                </div>
              </td>
              <td class="px-4 py-4 text-xs text-gray-600 max-w-xs truncate" :title="solic.detalhes">
                {{ solic.detalhes || '—' }}
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-xs">
                <span v-if="solic.perfil_executor" class="px-2 py-1 rounded bg-slate-100 text-slate-700 font-semibold border border-slate-200">
                  {{ solic.perfil_executor }}
                </span>
                <span v-else class="text-gray-400">—</span>
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-xs text-gray-700 font-medium">
                {{ solic.usuario || solic.username || solic.user || '—' }}
              </td>
              <td class="px-4 py-4 whitespace-nowrap">
                <span :class="getStatusBadgeClass(solic.status)">{{ solic.status }}</span>
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

const toast = useToast();

const solicitacoes = ref<any[]>([]);
const loading = ref(false);

const filtroEspecialidade = ref('');
const dataInicio = ref('');
const dataFim = ref('');

const especialidades = [
  'Cardiologia',
  'Cirurgia Geral',
  'Ginecologia',
  'Neurocirurgia',
  'Oftalmologia',
  'Ortopedia',
  'Otorrinolaringologia',
  'Plástica',
  'Torácica',
  'Urologia'
];

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
      // 1. Filtro de Especialidade (case insensitive / partial matching)
      let matchEsp = true;
      if (filtroEspecialidade.value) {
        matchEsp = !!(s.especialidade && s.especialidade.toLowerCase().includes(filtroEspecialidade.value.toLowerCase()));
      }

      // 2. Filtro de Data
      let matchData = true;
      if (s.data_criacao) {
        const solicDataOnly = s.data_criacao.split(' ')[0]; // YYYY-MM-DD
        if (dataInicio.value && solicDataOnly < dataInicio.value) {
          matchData = false;
        }
        if (dataFim.value && solicDataOnly > dataFim.value) {
          matchData = false;
        }
      }

      return matchEsp && matchData;
    })
    // Ordena do mais recente para o mais antigo (descending)
    .sort((a, b) => b.data_criacao.localeCompare(a.data_criacao));
});

onMounted(() => {
  carregarHistorico();
});
</script>
