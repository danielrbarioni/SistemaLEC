<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Fila por Especialidade Cirúrgica</h1>
      <span class="px-3 py-1 bg-teal-100 text-teal-800 text-xs font-semibold rounded-full">Gestão Assistencial Local</span>
    </div>

    <!-- Abas de Especialidades -->
    <div class="flex border-b border-gray-300 bg-white p-2 rounded-t-lg shadow-sm overflow-x-auto">
      <button 
        v-for="esp in especialidades" 
        :key="esp" 
        @click="especialidadeAtiva = esp"
        :class="[
          'px-6 py-3 text-sm font-semibold rounded-md transition duration-200 whitespace-nowrap mr-2',
          especialidadeAtiva === esp 
            ? 'bg-paper-sidebar text-white shadow-md' 
            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
        ]"
      >
        {{ esp }}
      </button>
    </div>

    <!-- Filtros e Controles -->
    <Card class="rounded-t-none">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Busca por texto -->
        <div class="form-group">
          <label for="filtroBusca" class="form-label font-semibold">Pesquisar Paciente</label>
          <input 
            id="filtroBusca" 
            v-model="filtroBusca" 
            type="text" 
            placeholder="Nome ou Prontuário..." 
            class="form-control"
          />
        </div>

        <!-- Filtro Status Sede (Nacional) -->
        <div class="form-group">
          <label for="filtroStatusSede" class="form-label font-semibold">Status Nacional (Sistema Sede)</label>
          <select id="filtroStatusSede" v-model="filtroStatusSede" class="form-control">
            <option value="">Todos</option>
            <option v-for="status in statusSedeOpcoes" :key="status" :value="status">
              {{ status }}
            </option>
          </select>
        </div>

        <!-- Filtro Status Local (HC-UFPE) -->
        <div class="form-group">
          <label for="filtroStatusLocal" class="form-label font-semibold">Status Local (Acompanhamento HC)</label>
          <select id="filtroStatusLocal" v-model="filtroStatusLocal" class="form-control">
            <option value="">Todos</option>
            <option value="Sem Pendências">Sem Pendências</option>
            <option v-for="status in statusLocalOpcoes" :key="status" :value="status">
              {{ status }}
            </option>
          </select>
        </div>
      </div>
    </Card>

    <!-- Tabela de Pacientes -->
    <Card>
      <div v-if="loading" class="flex justify-center items-center py-8">
        <LoadingIndicator />
      </div>
      <div v-else-if="pacientesFiltrados.length === 0" class="text-center py-10 text-gray-500">
        Nenhum paciente encontrado com os filtros selecionados para esta especialidade.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prontuário</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Procedimento</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status Nacional</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status Local (HC-UFPE)</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200 text-sm">
            <tr v-for="paciente in pacientesFiltrados" :key="paciente.codigo">
              <td class="px-6 py-4 whitespace-nowrap text-gray-800 font-mono">{{ paciente.codigo }}</td>
              <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{{ paciente.nome }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-600">{{ paciente.procedimento || 'Não informado' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
                  {{ paciente.status_consulta || 'NA FILA' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusLocalBadgeClass(paciente.status_local)">
                  {{ paciente.status_local || 'Sem Pendências' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <Button @click="abrirModalStatus(paciente)" variant="info" size="sm" class="flex items-center space-x-1">
                  <span>Atualizar Status</span>
                </Button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Modal para Atualizar Status Local -->
    <Modal :show="mostrarModal" @close="mostrarModal = false">
      <template #header>
        Atualizar Acompanhamento Local
      </template>

      <div class="space-y-4" v-if="pacienteSelecionado">
        <div>
          <p class="text-sm text-gray-500">Paciente</p>
          <p class="font-bold text-gray-800">{{ pacienteSelecionado.nome }} ({{ pacienteSelecionado.codigo }})</p>
        </div>

        <div class="form-group">
          <label for="novoStatusLocal" class="form-label font-semibold">Novo Status Local</label>
          <select id="novoStatusLocal" v-model="novoStatusLocal" class="form-control">
            <option value="Sem Pendências">Sem Pendências (Pronto para cirurgia)</option>
            <option v-for="status in statusLocalOpcoes" :key="status" :value="status">
              {{ status }}
            </option>
          </select>
        </div>
      </div>

      <template #footer>
        <Button @click="mostrarModal = false" variant="secondary">Cancelar</Button>
        <Button @click="salvarStatusLocal" :disabled="salvando" variant="primary">
          {{ salvando ? 'Salvando...' : 'Salvar Alteração' }}
        </Button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import api from '../services/api';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import Modal from '../components/Modal.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';

const toast = useToast();

const especialidades = ref([
  'Clínica Médica',
  'Ortopedia',
  'Dermatologia',
  'Cardiologia',
  'Cirurgia Geral',
]);

const especialidadeAtiva = ref('Clínica Médica');
const filtroBusca = ref('');
const filtroStatusSede = ref('');
const filtroStatusLocal = ref('');

const statusLocalOpcoes = [
  'Pendente Exames Diagnósticos',
  'Exames Realizados - Resultado Divulgado',
  'Aguardando Avaliação Pré-Anestésica',
  'Aprovado na Avaliação Pré-Anestésica',
  'Pendente Parecer Cardiológico',
  'Paciente com Contato Pendente',
];

const statusSedeOpcoes = ref<string[]>([]);
const pacientes = ref<any[]>([]);
const statusLocais = ref<Record<string, string>>({});
const loading = ref(false);

// Modal state
const mostrarModal = ref(false);
const pacienteSelecionado = ref<any | null>(null);
const novoStatusLocal = ref('Sem Pendências');
const salvando = ref(false);

const carregarDados = async () => {
  loading.value = true;
  try {
    // 1. Carrega todos os pacientes
    const resPacientes = await api.get('/api/pacientes');
    pacientes.value = resPacientes.data;

    // Extrai opções de status nacional/sede únicos
    const statusSet = new Set<string>();
    pacientes.value.forEach((p: any) => {
      if (p.status_consulta) statusSet.add(p.status_consulta);
    });
    statusSedeOpcoes.value = Array.from(statusSet);

    // 2. Carrega todos os status locais salvos no servidor
    const resStatusLocais = await api.get('/api/pacientes/status-locais');
    statusLocais.value = resStatusLocais.data;
  } catch (error) {
    toast.error('Erro ao carregar dados dos pacientes e status locais.');
  } finally {
    loading.value = false;
  }
};

const pacientesFiltrados = computed(() => {
  return pacientes.value
    .map(p => ({
      ...p,
      status_local: statusLocais.value[p.codigo.toString()] || 'Sem Pendências'
    }))
    .filter(p => {
      // Filtra por Especialidade Ativa
      const matchEsp = p.especialidade === especialidadeAtiva.value;
      
      // Filtra por Busca (Nome ou Código)
      const matchBusca = !filtroBusca.value || 
        p.nome.toLowerCase().includes(filtroBusca.value.toLowerCase()) ||
        p.codigo.toString().includes(filtroBusca.value);

      // Filtra por Status Sede
      const matchSede = !filtroStatusSede.value || p.status_consulta === filtroStatusSede.value;

      // Filtra por Status Local
      const matchLocal = !filtroStatusLocal.value || p.status_local === filtroStatusLocal.value;

      return matchEsp && matchBusca && matchSede && matchLocal;
    });
});

const abrirModalStatus = (paciente: any) => {
  pacienteSelecionado.value = paciente;
  novoStatusLocal.value = paciente.status_local;
  mostrarModal.value = true;
};

const salvarStatusLocal = async () => {
  if (!pacienteSelecionado.value) return;
  salvando.value = true;
  try {
    const cod = pacienteSelecionado.value.codigo.toString();
    await api.post(`/api/pacientes/${cod}/status-local`, {
      status_local: novoStatusLocal.value
    });
    // Atualiza localmente
    statusLocais.value[cod] = novoStatusLocal.value;
    toast.success('Status local de acompanhamento atualizado!');
    mostrarModal.value = false;
  } catch (error) {
    toast.error('Erro ao salvar status local.');
  } finally {
    salvando.value = false;
  }
};

const getStatusLocalBadgeClass = (status: string) => {
  switch (status) {
    case 'Sem Pendências': return 'px-2 py-0.5 rounded text-xs font-semibold bg-gray-100 text-gray-800';
    case 'Exames Realizados - Resultado Divulgado': return 'px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800';
    case 'Pendente Exames Diagnósticos': return 'px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-800';
    case 'Aguardando Avaliação Pré-Anestésica': return 'px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800';
    case 'Aprovado na Avaliação Pré-Anestésica': return 'px-2 py-0.5 rounded text-xs font-semibold bg-teal-100 text-teal-800';
    default: return 'px-2 py-0.5 rounded text-xs font-semibold bg-yellow-100 text-yellow-800';
  }
};

onMounted(() => {
  carregarDados();
});
</script>
