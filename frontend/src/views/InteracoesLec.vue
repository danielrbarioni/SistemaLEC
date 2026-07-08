<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-xl font-bold text-gray-800">Interações com o sistema LEC da Rede HU Brasil</h1>
      <span class="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">Assistencial → Gestão da LEC</span>
    </div>

    <!-- Abas Principais -->
    <div class="flex border-b border-gray-300 bg-white p-2 rounded-t-lg shadow-sm overflow-x-auto">
      <button 
        v-for="aba in abas" 
        :key="aba.id" 
        @click="selecionarAba(aba.id)"
        :class="[
          'flex-1 py-3 text-sm font-semibold rounded-md transition duration-200 whitespace-nowrap px-2',
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

    <!-- Formulário -->
    <Card v-if="perfisStore.perfilAtivo.tipo !== 'GESTAO_LEC'" class="rounded-t-none">
      <template #header>
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-bold text-gray-800">Nova Solicitação de {{ tipoSolicitacaoNome }}</h2>
          <span class="text-xs text-gray-500">HC-UFPE</span>
        </div>
      </template>

      <!-- Alerta indicando a origem dos dados quando buscados na Sede -->
      <div v-if="abaAtiva !== 'INSERIR' && formCarregadoDaSede" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-xs text-green-800 flex items-center space-x-2">
        <span>✅ Dados da solicitação ativa carregados com sucesso do <strong>Sistema LEC Sede</strong>.</span>
      </div>

      <form @submit.prevent="enviarSolicitacao" class="space-y-5">

        <!-- Linha de Busca/Identificação do Paciente -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="form-group">
            <label for="codigo_paciente" class="form-label font-semibold">Nº Prontuário <span class="text-red-500">*</span></label>
            <div class="flex space-x-2">
              <input 
                id="codigo_paciente" 
                v-model="form.codigo_paciente" 
                type="text" 
                placeholder="Prontuário" 
                class="form-control"
                required
              />
              <Button type="button" @click="buscarDados" :disabled="loadingBusca" variant="info" class="whitespace-nowrap">
                {{ loadingBusca ? '...' : 'Buscar' }}
              </Button>
            </div>
            <p class="text-xs text-gray-400 mt-1">
              {{ abaAtiva === 'INSERIR' ? 'Busca dados no AGHU' : 'Puxa dados do módulo Pacientes' }}
            </p>
          </div>

          <div class="form-group md:col-span-2">
            <label for="nome_paciente" class="form-label font-semibold">Nome Completo do Paciente <span class="text-red-500">*</span></label>
            <input 
              id="nome_paciente" 
              v-model="form.nome_paciente" 
              type="text" 
              placeholder="Preenchido automaticamente ou digitado manualmente" 
              class="form-control"
              required
              :disabled="abaAtiva !== 'INSERIR'"
            />
            <p v-if="abaAtiva === 'INSERIR'" class="text-xs text-gray-400 mt-1">Futuramente integrado ao AGHU</p>
          </div>
        </div>

        <!-- Seleção de Procedimento para Edição (quando há múltiplos) -->
        <div v-if="abaAtiva === 'EDITAR' && procedimentosPaciente.length > 1" class="p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <label class="form-label font-semibold text-amber-800">Qual procedimento deseja editar?</label>
          <div class="mt-2 space-y-2">
            <label 
              v-for="(proc, idx) in procedimentosPaciente" 
              :key="idx" 
              class="flex items-center space-x-3 p-3 bg-white rounded-lg border border-amber-200 cursor-pointer hover:bg-amber-50 transition"
              :class="{ 'border-amber-500 bg-amber-50 ring-1 ring-amber-400': procedimentoSelecionadoParaEdicao === idx }"
            >
              <input 
                type="radio" 
                :value="idx" 
                v-model="procedimentoSelecionadoParaEdicao"
                class="h-4 w-4 text-amber-600"
                @change="preencherCamposDoProc(proc)"
              />
              <div class="text-sm">
                <div class="font-semibold text-gray-800">{{ proc.procedimento }}</div>
                <div class="text-xs text-gray-500">{{ proc.especialidade }} · Swallis: {{ proc.swallis || '—' }}</div>
              </div>
            </label>
          </div>
        </div>

        <!-- Linha 2: Especialidade + Procedimento (Fila) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-group">
            <label for="especialidade" class="form-label font-semibold">Especialidade <span class="text-red-500">*</span></label>
            <select
              id="especialidade"
              v-model="form.especialidade"
              class="form-control"
              :class="{ 'bg-gray-100 cursor-not-allowed opacity-75': camposDesabilitados || perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' }"
              required
              @change="form.procedimento = ''"
              :disabled="camposDesabilitados || perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE'"
            >
              <option value="" disabled>Selecione a especialidade...</option>
              <option v-for="esp in especialidades" :key="esp.nome" :value="esp.nome">
                {{ esp.nome }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="procedimento" class="form-label font-semibold">Procedimento (Fila de Espera) <span class="text-red-500">*</span></label>
            <!-- Campo combinado: digitar ou selecionar -->
            <div class="relative">
              <input
                id="procedimento"
                v-model="form.procedimento"
                type="text"
                list="procedimentos-lista"
                :placeholder="form.especialidade ? 'Digite ou selecione o procedimento...' : 'Selecione a especialidade primeiro'"
                class="form-control"
                :class="{ 'bg-gray-100 cursor-not-allowed opacity-75': camposDesabilitados || !form.especialidade }"
                required
                :disabled="camposDesabilitados || !form.especialidade"
              />
              <datalist id="procedimentos-lista">
                <option v-for="proc in procedimentosDaEspecialidade" :key="proc" :value="proc">{{ proc }}</option>
              </datalist>
            </div>
          </div>
        </div>

        <!-- Linha 3: Judicializado + Swallis + Médico Responsável -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-start">

          <!-- Judicializado -->
          <div class="form-group">
            <label class="form-label font-semibold">Judicializado? <span class="text-red-500">*</span></label>
            <div class="flex items-center space-x-6 mt-2 p-3 border border-gray-200 rounded-lg" :class="camposDesabilitados ? 'bg-gray-100 cursor-not-allowed opacity-75' : 'bg-gray-50'">
              <label class="flex items-center space-x-2" :class="camposDesabilitados ? 'cursor-not-allowed' : 'cursor-pointer'">
                <input
                  type="radio"
                  name="judicializado"
                  value="Sim"
                  v-model="form.judicializado"
                  class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  required
                  :disabled="camposDesabilitados"
                />
                <span class="text-sm font-medium text-gray-700">Sim</span>
              </label>
              <label class="flex items-center space-x-2" :class="camposDesabilitados ? 'cursor-not-allowed' : 'cursor-pointer'">
                <input
                  type="radio"
                  name="judicializado"
                  value="Não"
                  v-model="form.judicializado"
                  class="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  :disabled="camposDesabilitados"
                />
                <span class="text-sm font-medium text-gray-700">Não</span>
              </label>
            </div>
            <div v-if="form.judicializado === 'Sim'" class="mt-2 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 font-medium">
              ⚠️ Paciente com determinação judicial — prioridade legal
            </div>
          </div>

          <!-- Swallis -->
          <div class="form-group">
            <label for="swallis" class="form-label font-semibold">
              Swallis (Priorização) <span class="text-red-500">*</span>
            </label>
            <select
              id="swallis"
              v-model="form.swallis"
              class="form-control"
              :class="{ 'bg-gray-100 cursor-not-allowed opacity-75': camposDesabilitados }"
              required
              :disabled="camposDesabilitados"
            >
              <option value="" disabled>Selecione...</option>
              <option value="A1">A1 — Prioridade Máxima</option>
              <option value="A2">A2 — Alta Prioridade</option>
              <option value="B">B — Prioridade Intermediária</option>
              <option value="C">C — Prioridade Padrão</option>
              <option value="D">D — Eletivo / Baixa Prioridade</option>
            </select>
            <div v-if="form.swallis" class="mt-2 px-3 py-2 rounded-lg text-xs font-semibold" :class="swallisBadgeClass">
              Classificação: {{ form.swallis }}
            </div>
          </div>

          <!-- Médico Responsável -->
          <div class="form-group">
            <label for="medico_responsavel" class="form-label font-semibold">Médico Responsável <span class="text-red-500">*</span></label>
            <input
              id="medico_responsavel"
              v-model="form.medico_responsavel"
              type="text"
              list="medicos-lista"
              placeholder="Digite o nome do médico solicitante"
              class="form-control"
              :class="{ 'bg-gray-100 cursor-not-allowed opacity-75': camposDesabilitados }"
              required
              :disabled="camposDesabilitados"
            />
            <datalist id="medicos-lista">
              <option v-for="med in medicosConhecidos" :key="med" :value="med">{{ med }}</option>
            </datalist>
            <p v-if="abaAtiva === 'INSERIR'" class="text-xs text-gray-400 mt-1">Futuramente integrado ao AGHU</p>
          </div>
        </div>

        <!-- Linha Opcional: Tempo de Standby (Apenas na aba STANDBY) -->
        <div v-if="abaAtiva === 'STANDBY'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="form-group md:col-span-1">
            <label for="tempo_standby" class="form-label font-semibold">Tempo de Standby (em dias) <span class="text-red-500">*</span></label>
            <input
              id="tempo_standby"
              v-model.number="form.tempo_standby"
              type="number"
              min="1"
              max="90"
              placeholder="Ex: 30"
              class="form-control text-lg font-bold text-center"
              required
            />
            <p class="text-xs text-red-500 mt-1 font-semibold">⚠️ Limite máximo permitido de 90 dias.</p>
          </div>
        </div>

        <!-- Justificativa / Detalhes -->
        <div class="form-group">
          <label for="detalhes" class="form-label font-semibold">
            {{ labelDetalhes }} <span class="text-red-500">*</span>
          </label>
          <textarea 
            id="detalhes" 
            v-model="form.detalhes" 
            rows="3" 
            placeholder="Descreva a justificativa clínica para esta solicitação..." 
            class="form-control"
            required
          ></textarea>
        </div>

        <!-- Botões -->
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
      <div v-else-if="solicitacoesFiltradas.length === 0" class="text-center py-8 text-gray-500">
        Nenhuma solicitação enviada até o momento.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Especialidade / Procedimento</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prontuário / Paciente</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Judicial</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Swallis</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Médico</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Info Extra</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200 text-sm">
            <tr v-for="solic in solicitacoesFiltradas" :key="solic.id">
              <td class="px-4 py-4 whitespace-nowrap text-gray-500 font-mono text-xs">#{{ solic.id }}</td>
              <td class="px-4 py-4 whitespace-nowrap">
                <span :class="getTipoBadgeClass(solic.tipo)">{{ solic.tipo }}</span>
              </td>
              <td class="px-4 py-4 text-gray-700 text-xs">
                <div class="font-semibold">{{ solic.especialidade || '—' }}</div>
                <div class="text-gray-400">{{ solic.procedimento || '—' }}</div>
              </td>
              <td class="px-4 py-4 text-gray-700 text-xs">
                <div class="font-mono">{{ solic.codigo_paciente }}</div>
                <div class="font-medium">{{ solic.nome_paciente }}</div>
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-xs">
                <span v-if="solic.judicializado === 'Sim'" class="px-2 py-0.5 rounded-full font-semibold bg-amber-100 text-amber-800">⚖️ Sim</span>
                <span v-else class="text-gray-400">Não</span>
              </td>
              <td class="px-4 py-4 whitespace-nowrap">
                <span v-if="solic.swallis" :class="getSwallisClass(solic.swallis)">{{ solic.swallis }}</span>
                <span v-else class="text-gray-400">—</span>
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-xs text-gray-600">{{ solic.medico_responsavel || '—' }}</td>
              <td class="px-4 py-4 whitespace-nowrap">
                <span :class="getStatusBadgeClass(solic.status)">{{ solic.status }}</span>
              </td>
              <td class="px-4 py-4 text-xs text-gray-600">
                <div v-if="solic.tempo_standby" class="font-semibold text-purple-700 bg-purple-50 px-2 py-1 rounded">
                  ⏱️ {{ solic.tempo_standby }} dias
                </div>
                <div v-else class="text-gray-400">—</div>
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-xs">
                <div v-if="solic.status === 'PENDENTE' && (perfisStore.perfilAtivo.tipo === 'GESTAO_LEC' || perfisStore.perfilAtivo.tipo === 'ADMIN')" class="flex space-x-1">
                  <Button @click="atualizarStatus(solic.id, 'APROVADO')" variant="success" size="sm">
                    {{ perfisStore.perfilAtivo.tipo === 'GESTAO_LEC' ? 'Dar Baixa' : 'Aprovar' }}
                  </Button>
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
import { ref, computed, onMounted, watch } from 'vue';
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
import { usePerfisStore } from '../stores/perfis';

const toast = useToast();
const perfisStore = usePerfisStore();

// -------------------------------------------------------
// Especialidades e Procedimentos
// -------------------------------------------------------
const especialidades = ref([
  {
    nome: 'Cardiologia / Cirurgia Cardíaca',
    procedimentos: ['Revascularização do Miocárdio (Ponte de Safena)', 'Troca de Valva Aórtica', 'Troca de Valva Mitral', 'Implante de Marcapasso', 'Correção de CIA / CIV']
  },
  {
    nome: 'Cirurgia Geral',
    procedimentos: ['Colecistectomia', 'Herniorrafia Inguinal', 'Apendicectomia', 'Gastrectomia', 'Colostomia']
  },
  {
    nome: 'Ginecologia',
    procedimentos: ['Histerectomia', 'Miomectomia', 'Laparoscopia Diagnóstica', 'Colpoperineoplastia', 'Ooforectomia']
  },
  {
    nome: 'Neurocirurgia',
    procedimentos: ['Craniectomia Descompressiva', 'Clipagem de Aneurisma', 'Derivação Ventrículo-Peritoneal', 'Microdiscectomia', 'Tumor Cerebral — Ressecção']
  },
  {
    nome: 'Oftalmologia',
    procedimentos: ['Facoemulsificação (Catarata)', 'Trabeculectomia (Glaucoma)', 'Vitrectomia', 'Transplante de Córnea', 'Fotocoagulação a Laser']
  },
  {
    nome: 'Ortopedia',
    procedimentos: ['Artroplastia Total de Quadril', 'Artroplastia Total de Joelho', 'Artroscopia de Joelho', 'Fixação de Fratura de Fêmur', 'Osteossíntese de Coluna']
  },
  {
    nome: 'Otorrinolaringologia',
    procedimentos: ['Septoplastia', 'Amigdalectomia', 'Timpanoplastia', 'Adenoidectomia', 'Microcirurgia de Laringe']
  },
  {
    nome: 'Plástica',
    procedimentos: ['Mamoplastia', 'Rinoplastia', 'Blefaroplastia', 'Reconstrução Mamária', 'Abdominoplastia']
  },
  {
    nome: 'Torácica',
    procedimentos: ['Lobectomia', 'Pleuroscopia', 'Simpatectomia', 'Ressecção de Nódulo Pulmonar', 'Broncoscopia']
  },
  {
    nome: 'Urologia',
    procedimentos: ['Prostatectomia Radical', 'Nefrectomia', 'Ureteroscopia', 'Litotripsia', 'Ressecção Transuretral de Próstata (RTUP)']
  }
]);

// Procedimentos filtrados pela especialidade selecionada
const procedimentosDaEspecialidade = computed(() => {
  const esp = especialidades.value.find(e => e.nome === form.value.especialidade);
  return esp ? esp.procedimentos : [];
});

// Médicos conhecidos extraídos das solicitações (para o autocomplete)
const medicosConhecidos = computed(() => {
  const nomes = solicitacoes.value
    .map(s => s.medico_responsavel)
    .filter(n => n && n !== '—' && n !== 'Não informado');
  return [...new Set(nomes)].sort();
});

// -------------------------------------------------------
// Abas
// -------------------------------------------------------
const abas = [
  { id: 'INSERIR', nome: 'Solicitar Inclusão', icon: UserPlusIcon },
  { id: 'EDITAR', nome: 'Solicitar Edição', icon: PencilSquareIcon },
  { id: 'EXCLUIR', nome: 'Solicitar Exclusão', icon: TrashIcon },
  { id: 'STANDBY', nome: 'Solicitar Standby', icon: PauseIcon }
];

const abaAtiva = ref('INSERIR');
const loadingBusca = ref(false);
const submitting = ref(false);
const loadingSolicitacoes = ref(false);
const solicitacoes = ref<any[]>([]);
const formCarregadoDaSede = ref(false);

// Para aba EDITAR com múltiplos procedimentos
const procedimentosPaciente = ref<any[]>([]);
const procedimentoSelecionadoParaEdicao = ref<number | null>(null);

// -------------------------------------------------------
// Formulário
// -------------------------------------------------------
const form = ref({
  especialidade: '',
  procedimento: '',
  procedimento_anterior: '', // Armazena o procedimento original antes de editar
  codigo_paciente: '',
  nome_paciente: '',
  judicializado: '',
  swallis: '',
  medico_responsavel: '',
  detalhes: '',
  tempo_standby: undefined as number | undefined
});

const selecionarAba = (id: string) => {
  abaAtiva.value = id;
  limparFormulario();
};

// Determina se os campos devem ser somente-leitura na aba selecionada
const camposDesabilitados = computed(() => {
  return abaAtiva.value === 'EXCLUIR' || abaAtiva.value === 'STANDBY';
});

// Filtra a lista de solicitações de acordo com o perfil ativo
const solicitacoesFiltradas = computed(() => {
  if (perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' && perfisStore.perfilAtivo.especialidade) {
    const activeSpecialtyName = perfisStore.perfilAtivo.especialidade.toLowerCase();
    return solicitacoes.value.filter(s => 
      s.especialidade && s.especialidade.toLowerCase().includes(activeSpecialtyName)
    );
  }
  return solicitacoes.value;
});

// Trava a especialidade da nova solicitação caso o perfil ativo seja de uma especialidade específica
watch(() => perfisStore.perfilAtivo, (newProfile) => {
  if (newProfile.tipo === 'ESPECIALIDADE' && newProfile.especialidade) {
    const found = especialidades.value.find(e => e.nome.toLowerCase().includes(newProfile.especialidade!.toLowerCase()));
    if (found) {
      form.value.especialidade = found.nome;
    } else {
      form.value.especialidade = newProfile.especialidade;
    }
  } else {
    form.value.especialidade = '';
  }
}, { immediate: true });

const tipoSolicitacaoNome = computed(() => {
  const match = abas.find(a => a.id === abaAtiva.value);
  return match ? match.nome.replace('Solicitar ', '') : '';
});

const labelDetalhes = computed(() => {
  switch (abaAtiva.value) {
    case 'INSERIR':  return 'Justificativa e Indicação Clínica para Inclusão';
    case 'EDITAR':   return 'Campos e Dados que precisam ser atualizados e o motivo';
    case 'EXCLUIR':  return 'Motivo detalhado para a Exclusão da Lista de Espera';
    case 'STANDBY':  return 'Motivo clínico ou administrativo para suspensão temporária (Standby)';
    default:         return 'Detalhes da Solicitação';
  }
});

const swallisBadgeClass = computed(() => {
  switch (form.value.swallis) {
    case 'A1': return 'bg-red-100 text-red-800';
    case 'A2': return 'bg-orange-100 text-orange-800';
    case 'B':  return 'bg-yellow-100 text-yellow-800';
    case 'C':  return 'bg-blue-100 text-blue-800';
    case 'D':  return 'bg-gray-100 text-gray-700';
    default:   return 'bg-gray-100 text-gray-700';
  }
});

const limparFormulario = () => {
  form.value = {
    especialidade: '',
    procedimento: '',
    procedimento_anterior: '',
    codigo_paciente: '',
    nome_paciente: '',
    judicializado: '',
    swallis: '',
    medico_responsavel: '',
    detalhes: '',
    tempo_standby: undefined
  };
  formCarregadoDaSede.value = false;
  procedimentosPaciente.value = [];
  procedimentoSelecionadoParaEdicao.value = null;

  // Reaplica especialidade travada pelo perfil
  const profile = perfisStore.perfilAtivo;
  if (profile.tipo === 'ESPECIALIDADE' && profile.especialidade) {
    const found = especialidades.value.find(e => e.nome.toLowerCase().includes(profile.especialidade!.toLowerCase()));
    form.value.especialidade = found ? found.nome : profile.especialidade;
  }
};

// Preenche o formulário ao selecionar o procedimento para edição
const preencherCamposDoProc = (proc: any) => {
  form.value.procedimento_anterior = proc.procedimento;
  form.value.procedimento = proc.procedimento;
  form.value.especialidade = proc.especialidade;
  form.value.judicializado = proc.judicializado || 'Não';
  form.value.swallis = proc.swallis || '';
  form.value.medico_responsavel = proc.medico_responsavel || '';
};

// Busca unificada com base no prontuário e na aba selecionada
const buscarDados = async () => {
  if (!form.value.codigo_paciente) {
    toast.error('Por favor, digite o número do prontuário.');
    return;
  }
  loadingBusca.value = true;
  formCarregadoDaSede.value = false;
  procedimentosPaciente.value = [];
  procedimentoSelecionadoParaEdicao.value = null;

  try {
    if (abaAtiva.value === 'INSERIR') {
      // Busca no AGHU
      const { data } = await api.get(`/api/pacientes/${form.value.codigo_paciente}`);
      form.value.nome_paciente = data.nome;
      toast.success(`Paciente localizado no AGHU: ${data.nome}`);
    } else if (abaAtiva.value === 'EDITAR') {
      // Busca procedimentos do paciente no módulo Pacientes
      const { data: solicsData } = await api.get('/api/solicitacoes');
      const especialidadeAtual = perfisStore.perfilAtivo.tipo === 'ESPECIALIDADE' && perfisStore.perfilAtivo.especialidade
        ? perfisStore.perfilAtivo.especialidade.toLowerCase()
        : null;

      // Reconstrução dos procedimentos do paciente (igual ao módulo Pacientes)
      const allSolics: any[] = solicsData;
      const codProntuario = String(form.value.codigo_paciente);

      // Pega o nome do paciente
      const solicsDosPac = allSolics.filter(s => String(s.codigo_paciente) === codProntuario);
      if (solicsDosPac.length === 0) {
        toast.error('Paciente não encontrado no Sistema LEC.');
        limparFormulario();
        return;
      }
      form.value.nome_paciente = solicsDosPac[0].nome_paciente;

      // Reconstrói a lista de procedimentos aprovados do paciente
      const procMap = new Map<string, any>();
      const approvedSolics = solicsDosPac
        .filter(s => s.status === 'APROVADO')
        .sort((a: any, b: any) => a.data_criacao.localeCompare(b.data_criacao));

      for (const s of approvedSolics) {
        const key = `${s.especialidade}||${s.procedimento}`;
        if (s.tipo === 'INSERIR') {
          procMap.set(key, {
            especialidade: s.especialidade,
            procedimento: s.procedimento,
            judicializado: s.judicializado || 'Não',
            swallis: s.swallis || '—',
            medico_responsavel: s.medico_responsavel || 'Não informado',
            status: 'ATIVO'
          });
        } else if (s.tipo === 'EDITAR') {
          const oldKey = `${s.especialidade}||${s.procedimento_anterior || s.procedimento}`;
          const existing = procMap.get(oldKey);
          if (existing) {
            procMap.delete(oldKey);
            procMap.set(key, {
              ...existing,
              procedimento: s.procedimento,
              judicializado: s.judicializado || 'Não',
              swallis: s.swallis || '—',
              medico_responsavel: s.medico_responsavel || 'Não informado'
            });
          }
        } else if (s.tipo === 'EXCLUIR') {
          procMap.delete(key);
        }
      }

      let procs = Array.from(procMap.values());

      // Filtra por especialidade se o perfil for ESPECIALIDADE
      if (especialidadeAtual) {
        procs = procs.filter(p => p.especialidade && p.especialidade.toLowerCase().includes(especialidadeAtual));
      }

      if (procs.length === 0) {
        toast.error('Nenhum procedimento ativo encontrado para este paciente' + (especialidadeAtual ? ' nesta especialidade' : '') + '.');
        limparFormulario();
        return;
      }

      procedimentosPaciente.value = procs;
      formCarregadoDaSede.value = true;

      // Se houver apenas um procedimento, preenchemos automaticamente
      if (procs.length === 1) {
        procedimentoSelecionadoParaEdicao.value = 0;
        preencherCamposDoProc(procs[0]);
        toast.success(`Procedimento encontrado: ${procs[0].procedimento}`);
      } else {
        toast.info(`${procs.length} procedimentos encontrados para este paciente. Selecione qual deseja editar.`);
      }
    } else {
      // EXCLUIR / STANDBY: Busca no Sistema LEC Sede (última solicitação aprovada)
      const { data } = await api.get(`/api/solicitacoes/paciente/${form.value.codigo_paciente}`);
      form.value.nome_paciente = data.nome_paciente;
      form.value.especialidade = data.especialidade || '';
      form.value.procedimento = data.procedimento || '';
      form.value.judicializado = data.judicializado || 'Não';
      form.value.swallis = data.swallis || '';
      form.value.medico_responsavel = data.medico_responsavel || '';
      
      formCarregadoDaSede.value = true;
      toast.success('Solicitação ativa localizada no Sistema LEC!');
    }
  } catch (error: any) {
    if (abaAtiva.value === 'INSERIR') {
      toast.error('Paciente não localizado no AGHU. Digite o nome manualmente.');
    } else {
      toast.error('Prontuário sem dados ativos no Sistema LEC. Não é possível prosseguir.');
      limparFormulario();
    }
  } finally {
    loadingBusca.value = false;
  }
};

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

const enviarSolicitacao = async () => {
  // Validação do limite de tempo do standby
  if (abaAtiva.value === 'STANDBY') {
    if (!form.value.tempo_standby || form.value.tempo_standby < 1 || form.value.tempo_standby > 90) {
      toast.error('O tempo de standby deve ser entre 1 e 90 dias.');
      return;
    }
  }

  // Valida que para EDITAR o procedimento foi selecionado
  if (abaAtiva.value === 'EDITAR' && procedimentosPaciente.value.length > 1 && procedimentoSelecionadoParaEdicao.value === null) {
    toast.error('Selecione qual procedimento deseja editar.');
    return;
  }

  submitting.value = true;
  try {
    await api.post('/api/solicitacoes', {
      tipo: abaAtiva.value,
      especialidade: form.value.especialidade,
      procedimento: form.value.procedimento,
      codigo_paciente: form.value.codigo_paciente,
      nome_paciente: form.value.nome_paciente,
      judicializado: form.value.judicializado,
      swallis: form.value.swallis,
      medico_responsavel: form.value.medico_responsavel,
      detalhes: form.value.detalhes,
      tempo_standby: form.value.tempo_standby || undefined,
      perfil_executor: perfisStore.perfilAtivo.nome,
      procedimento_anterior: form.value.procedimento_anterior || undefined
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
    case 'EDITAR':  return 'px-2 py-0.5 rounded text-xs font-semibold bg-yellow-100 text-yellow-800';
    case 'EXCLUIR': return 'px-2 py-0.5 rounded text-xs font-semibold bg-red-100 text-red-800';
    case 'STANDBY': return 'px-2 py-0.5 rounded text-xs font-semibold bg-purple-100 text-purple-800';
    default:        return 'px-2 py-0.5 rounded text-xs font-semibold bg-gray-100 text-gray-800';
  }
};

const getSwallisClass = (swallis: string) => {
  const base = 'px-2 py-0.5 rounded font-bold text-xs';
  switch (swallis) {
    case 'A1': return `${base} bg-red-100 text-red-800`;
    case 'A2': return `${base} bg-orange-100 text-orange-800`;
    case 'B':  return `${base} bg-yellow-100 text-yellow-800`;
    case 'C':  return `${base} bg-blue-100 text-blue-800`;
    case 'D':  return `${base} bg-gray-100 text-gray-700`;
    default:   return `${base} bg-gray-100 text-gray-700`;
  }
};

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'PENDENTE':  return 'px-2 py-0.5 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-800';
    case 'APROVADO':  return 'px-2 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-800';
    case 'REJEITADO': return 'px-2 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800';
    default:          return 'px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-800';
  }
};

onMounted(() => {
  carregarSolicitacoes();
});
</script>
