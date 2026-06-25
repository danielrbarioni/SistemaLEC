<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Central de Marcação e Priorização</h1>
      <span class="px-3 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded-full">Aceleração de Exames e Consultas</span>
    </div>

    <!-- Info Box -->
    <Card class="bg-gradient-to-r from-red-50 to-orange-50 border-red-100">
      <div class="flex items-start space-x-3">
        <ExclamationTriangleIcon class="h-6 w-6 text-red-600 shrink-0 mt-0.5" />
        <div>
          <h3 class="text-sm font-semibold text-red-800">Priorização de Pacientes Cirúrgicos (LEC)</h3>
          <p class="text-xs text-red-700 mt-1">
            Esta tela consolida solicitações de exames e consultas pendentes no AGHU. Os pacientes marcados como 
            <strong>"Cirúrgico (LEC)"</strong> devem ter seus agendamentos priorizados com celeridade para evitar atrasos no pré-operatório.
          </p>
        </div>
      </div>
    </Card>

    <!-- Filtros -->
    <Card>
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex flex-wrap gap-2">
          <Button 
            @click="filtroFila = 'TODOS'" 
            :variant="filtroFila === 'TODOS' ? 'primary' : 'secondary'"
            size="sm"
          >
            Todos os Pedidos ({{ totalPedidos }})
          </Button>
          <Button 
            @click="filtroFila = 'CIRURGICO'" 
            :variant="filtroFila === 'CIRURGICO' ? 'danger' : 'secondary'"
            size="sm"
            class="flex items-center space-x-1"
          >
            <span>Apenas Cirúrgicos ({{ totalCirurgicos }})</span>
          </Button>
        </div>
        
        <div class="w-full md:w-64">
          <input 
            v-model="busca" 
            type="text" 
            placeholder="Buscar prontuário ou nome..." 
            class="form-control"
          />
        </div>
      </div>
    </Card>

    <!-- Tabela de Solicitações de Agendamento -->
    <Card>
      <div v-if="loading" class="flex justify-center items-center py-8">
        <LoadingIndicator />
      </div>
      <div v-else-if="pedidosFiltrados.length === 0" class="text-center py-10 text-gray-500">
        Nenhum pedido de marcação pendente encontrado.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prioridade</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prontuário</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Paciente</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Solicitação</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Especialidade</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vínculo LEC</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200 text-sm">
            <tr 
              v-for="pedido in pedidosFiltrados" 
              :key="pedido.id"
              :class="pedido.isCirurgico ? 'bg-red-50/30' : ''"
            >
              <!-- Prioridade Badge -->
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  :class="[
                    'px-2 py-0.5 rounded-full text-xs font-bold',
                    pedido.isCirurgico 
                      ? 'bg-red-100 text-red-800 animate-pulse' 
                      : 'bg-gray-100 text-gray-800'
                  ]"
                >
                  {{ pedido.isCirurgico ? 'CRÍTICO' : 'NORMAL' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap font-mono text-gray-800">{{ pedido.codigo_paciente }}</td>
              <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{{ pedido.nome_paciente }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-gray-900 font-semibold">{{ pedido.item_solicitado }}</div>
                <div class="text-xs text-gray-500">Solicitado em: {{ pedido.data_solicitacao }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-600">{{ pedido.especialidade }}</td>
              <!-- Vínculo LEC -->
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  v-if="pedido.isCirurgico"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-orange-100 text-orange-800"
                >
                  <SparklesIcon class="h-3 w-3 mr-1" />
                  Paciente Cirúrgico (LEC)
                </span>
                <span v-else class="text-gray-400 text-xs">Clínico Geral</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-xs">
                <Button @click="agendarPedido(pedido.id)" variant="success" size="sm">
                  Marcar como Agendado
                </Button>
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
import { 
  ExclamationTriangleIcon, 
  SparklesIcon 
} from '@heroicons/vue/24/outline';
import api from '../services/api';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';

const toast = useToast();

const busca = ref('');
const filtroFila = ref('TODOS'); // TODOS, CIRURGICO
const loading = ref(false);
const pacientesLec = ref<any[]>([]);

// Mock de exames/consultas solicitados no AGHU pendentes de agendamento
const pedidosAgendamento = ref([
  { id: 1, codigo_paciente: '10000016', nome_paciente: 'CARLA DIAS (CSV)', item_solicitado: 'Ressonância Magnética de Joelho', especialidade: 'Clínica Médica', data_solicitacao: '2026-06-20', status: 'PENDENTE' },
  { id: 2, codigo_paciente: '77002', nome_paciente: 'BRUNO LIMA (CSV)', item_solicitado: 'Avaliação Pré-Anestésica', especialidade: 'Ortopedia', data_solicitacao: '2026-06-22', status: 'PENDENTE' },
  { id: 3, codigo_paciente: '77004', nome_paciente: 'LUCAS ALMEIDA (CSV)', item_solicitado: 'Ecocardiograma Transtorácico', especialidade: 'Cardiologia', data_solicitacao: '2026-06-23', status: 'PENDENTE' },
  { id: 4, codigo_paciente: '99021', nome_paciente: 'JOÃO BATISTA', item_solicitado: 'Consulta Geral de Retorno', especialidade: 'Clínica Médica', data_solicitacao: '2026-06-24', status: 'PENDENTE' },
  { id: 5, codigo_paciente: '77003', nome_paciente: 'FERNANDA COSTA (CSV)', item_solicitado: 'Biópsia Incisional de Pele', especialidade: 'Dermatologia', data_solicitacao: '2026-06-25', status: 'PENDENTE' },
]);

const carregarPacientesLec = async () => {
  loading.value = true;
  try {
    const { data } = await api.get('/api/pacientes');
    pacientesLec.value = data;
  } catch (error) {
    toast.error('Erro ao carregar dados da LEC para verificação.');
  } finally {
    loading.value = false;
  }
};

// Mapeia se o paciente solicitado está de fato na fila cirúrgica (LEC)
const pedidosProcessados = computed(() => {
  const codigosLec = new Set(pacientesLec.value.map(p => p.codigo.toString()));
  return pedidosAgendamento.value.map(p => ({
    ...p,
    isCirurgico: codigosLec.has(p.codigo_paciente)
  })).sort((a, b) => {
    // Ordena colocando os cirúrgicos críticos no topo
    if (a.isCirurgico && !b.isCirurgico) return -1;
    if (!a.isCirurgico && b.isCirurgico) return 1;
    return 0;
  });
});

const pedidosFiltrados = computed(() => {
  return pedidosProcessados.value.filter(p => {
    const matchBusca = !busca.value || 
      p.nome_paciente.toLowerCase().includes(busca.value.toLowerCase()) ||
      p.codigo_paciente.includes(busca.value);
      
    const matchFila = filtroFila.value === 'TODOS' || (filtroFila.value === 'CIRURGICO' && p.isCirurgico);
    
    return matchBusca && matchFila && p.status === 'PENDENTE';
  });
});

const totalPedidos = computed(() => pedidosAgendamento.value.filter(p => p.status === 'PENDENTE').length);
const totalCirurgicos = computed(() => pedidosProcessados.value.filter(p => p.isCirurgico && p.status === 'PENDENTE').length);

const agendarPedido = (id: number) => {
  const index = pedidosAgendamento.value.findIndex(p => p.id === id);
  if (index !== -1) {
    pedidosAgendamento.value[index].status = 'AGENDADO';
    toast.success('Paciente agendado com prioridade com sucesso!');
  }
};

onMounted(() => {
  carregarPacientesLec();
});
</script>
