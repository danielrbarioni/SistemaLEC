<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Interações Diretas com a LEC</h1>
      <span class="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">Assistencial -> Gestão da LEC</span>
    </div>

    <!-- Abas Principais -->
    <div class="flex border-b border-gray-300 bg-white p-2 rounded-t-lg shadow-sm">
      <button 
        v-for="aba in abas" 
        :key="aba.id" 
        @click="abaAtiva = aba.id"
        :class="[
          'flex-1 py-3 text-sm font-semibold rounded-md transition duration-200',
          abaAtiva === aba.id 
            ? 'bg-paper-sidebar text-white shadow-md' 
            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
        ]"
      >
        <span class="flex items-center justify-center space-x-2">
          <component :is="aba.icon" class="h-5 w-5" />
          <span>{{ aba.nome }}</span>
        </span>
      </button>
    </div>

    <!-- Formulários das Abas -->
    <Card class="rounded-t-none">
      <template #header>
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-bold text-gray-800">Nova Solicitação de {{ tipoSolicitacaoNome }}</h2>
          <span class="text-xs text-gray-500">HC-UFPE</span>
        </div>
      </template>

      <form @submit.prevent="enviarSolicitacao" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Código do Paciente (Prontuário) -->
          <div class="form-group">
            <label for="codigo_paciente" class="form-label font-semibold">Nº Prontuário (Código AGHU)</label>
            <div class="flex space-x-2">
              <input 
                id="codigo_paciente" 
                v-model="form.codigo_paciente" 
                type="text" 
                placeholder="Digite o código" 
                class="form-control"
                required
              />
              <Button type="button" @click="buscarPaciente" :disabled="loadingBusca" variant="info" class="whitespace-nowrap">
                {{ loadingBusca ? 'Buscando...' : 'Buscar Nome' }}
              </Button>
            </div>
          </div>

          <!-- Nome do Paciente -->
          <div class="form-group md:col-span-2">
            <label for="nome_paciente" class="form-label font-semibold">Nome Completo do Paciente</label>
            <input 
              id="nome_paciente" 
              v-model="form.nome_paciente" 
              type="text" 
              placeholder="Preenchido automaticamente ou digitado" 
              class="form-control"
              required
            />
          </div>
        </div>

        <!-- Detalhes / Justificativa da Solicitação -->
        <div class="form-group">
          <label for="detalhes" class="form-label font-semibold">
            {{ labelDetalhes }}
          </label>
          <textarea 
            id="detalhes" 
            v-model="form.detalhes" 
            rows="4" 
            placeholder="Descreva detalhes clínicos, indicação de urgência, ou justificativas para a alteração..." 
            class="form-control"
            required
          ></textarea>
        </div>

        <div class="flex justify-end space-x-3 pt-2">
          <Button type="button" @click="limparFormulario" variant="secondary">
            Limpar
          </Button>
          <Button type="submit" :disabled="submitting" variant="primary">
            {{ submitting ? 'Enviando...' : 'Enviar Solicitação' }}
          </Button>
        </div>
      </form>
    </Card>

    <!-- Tabela de Solicitações Enviadas -->
    <Card>
      <template #header>
        <h2 class="text-lg font-bold text-gray-800">Acompanhamento das Solicitações</h2>
      </template>

      <div v-if="loadingSolicitacoes" class="flex justify-center items-center py-6">
        <LoadingIndicator />
      </div>
      <div v-else-if="solicitacoes.length === 0" class="text-center py-8 text-gray-500">
        Nenhuma solicitação enviada até o momento.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prontuário</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Paciente</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Justificativa / Detalhes</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200 text-sm">
            <tr v-for="solic in solicitacoes" :key="solic.id">
              <td class="px-6 py-4 whitespace-nowrap text-gray-500 font-mono text-xs">#{{ solic.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getTipoBadgeClass(solic.tipo)">
                  {{ solic.tipo }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-800">{{ solic.codigo_paciente }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-800 font-medium">{{ solic.nome_paciente }}</td>
              <td class="px-6 py-4 text-gray-600 max-w-xs truncate" :title="solic.detalhes">{{ solic.detalhes }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusBadgeClass(solic.status)">
                  {{ solic.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-500 text-xs">{{ solic.data_criacao }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-xs">
                <!-- Se for equipe de gestão, exibe botões para Aprovar/Rejeitar -->
                <div v-if="solic.status === 'PENDENTE'" class="flex space-x-1">
                  <Button @click="atualizarStatus(solic.id, 'APROVADO')" variant="success" size="sm">Aprovar</Button>
                  <Button @click="atualizarStatus(solic.id, 'REJEITADO')" variant="danger" size="sm">Rejeitar</Button>
                </div>
                <span v-else class="text-gray-400">-</span>
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
  UserPlusIcon, 
  TrashIcon, 
  PencilSquareIcon, 
  PauseIcon 
} from '@heroicons/vue/24/outline';
import api from '../services/api';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';

const toast = useToast();

const abas = [
  { id: 'INSERIR', nome: 'Solicitar Inclusão', icon: UserPlusIcon },
  { id: 'EDITAR', nome: 'Solicitar Edição', icon: PencilSquareIcon },
  { id: 'EXCLUIR', nome: 'Solicitar Exclusão', icon: TrashIcon },
  { id: 'STANDBY', nome: 'Colocar Stand-by', icon: PauseIcon },
];

const abaAtiva = ref('INSERIR');
const loadingBusca = ref(false);
const submitting = ref(false);
const loadingSolicitacoes = ref(false);
const solicitacoes = ref<any[]>([]);

const form = ref({
  codigo_paciente: '',
  nome_paciente: '',
  detalhes: '',
});

const tipoSolicitacaoNome = computed(() => {
  const match = abas.find(a => a.id === abaAtiva.value);
  return match ? match.nome.replace('Solicitar ', '') : '';
});

const labelDetalhes = computed(() => {
  switch (abaAtiva.value) {
    case 'INSERIR':
      return 'Justificativa e Indicação Clínica para Inclusão';
    case 'EDITAR':
      return 'Campos e Dados que precisam ser atualizados e o motivo';
    case 'EXCLUIR':
      return 'Motivo detalhado para a Exclusão da Lista de Espera';
    case 'STANDBY':
      return 'Motivo clínico ou administrativo para suspensão temporária (Stand-by)';
    default:
      return 'Detalhes da Solicitação';
  }
});

// Limpa formulário
const limparFormulario = () => {
  form.value = {
    codigo_paciente: '',
    nome_paciente: '',
    detalhes: '',
  };
};

// Busca nome do paciente no AGHU usando endpoint do backend
const buscarPaciente = async () => {
  if (!form.value.codigo_paciente) {
    toast.error('Por favor, digite o número do prontuário.');
    return;
  }
  loadingBusca.value = true;
  try {
    const { data } = await api.get(`/api/pacientes/${form.value.codigo_paciente}`);
    form.value.nome_paciente = data.nome;
    toast.success(`Paciente localizado: ${data.nome}`);
  } catch (error) {
    toast.error('Paciente não localizado no AGHU. Digite o nome manualmente.');
  } finally {
    loadingBusca.value = false;
  }
};

// Carrega lista de solicitações
const carregarSolicitacoes = async () => {
  loadingSolicitacoes.value = true;
  try {
    const { data } = await api.get('/api/solicitacoes');
    solicitacoes.value = data;
  } catch (error) {
    toast.error('Erro ao carregar solicitações.');
  } finally {
    loadingSolicitacoes.value = false;
  }
};

// Envia a solicitação
const enviarSolicitacao = async () => {
  submitting.value = true;
  try {
    await api.post('/api/solicitacoes', {
      tipo: abaAtiva.value,
      codigo_paciente: form.value.codigo_paciente,
      nome_paciente: form.value.nome_paciente,
      detalhes: form.value.detalhes,
    });
    toast.success('Solicitação registrada com sucesso!');
    limparFormulario();
    await carregarSolicitacoes();
  } catch (error) {
    toast.error('Erro ao registrar solicitação.');
  } finally {
    submitting.value = false;
  }
};

// Atualiza status da solicitação (aprovar/rejeitar)
const atualizarStatus = async (id: string, status: string) => {
  try {
    await api.put(`/api/solicitacoes/${id}/status`, { status });
    toast.success(`Solicitação ${status.toLowerCase()} com sucesso!`);
    await carregarSolicitacoes();
  } catch (error) {
    toast.error('Erro ao atualizar status.');
  }
};

const getTipoBadgeClass = (tipo: string) => {
  switch (tipo) {
    case 'INSERIR': return 'px-2 py-0.5 rounded text-xs font-semibold bg-green-100 text-green-800';
    case 'EDITAR': return 'px-2 py-0.5 rounded text-xs font-semibold bg-yellow-100 text-yellow-800';
    case 'EXCLUIR': return 'px-2 py-0.5 rounded text-xs font-semibold bg-red-100 text-red-800';
    case 'STANDBY': return 'px-2 py-0.5 rounded text-xs font-semibold bg-purple-100 text-purple-800';
    default: return 'px-2 py-0.5 rounded text-xs font-semibold bg-gray-100 text-gray-800';
  }
};

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'PENDENTE': return 'px-2 py-0.5 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-800';
    case 'APROVADO': return 'px-2 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-800';
    case 'REJEITADO': return 'px-2 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800';
    default: return 'px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-800';
  }
};

onMounted(() => {
  carregarSolicitacoes();
});
</script>
