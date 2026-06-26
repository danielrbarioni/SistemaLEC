<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Gestão por Especialidade Cirúrgica</h1>
      <span class="px-3 py-1 bg-teal-100 text-teal-800 text-xs font-semibold rounded-full">Gestão Assistencial Local</span>
    </div>

    <!-- Abas de Especialidades -->
    <div class="flex border-b border-gray-300 bg-white p-2 rounded-t-lg shadow-sm overflow-x-auto">
      <button 
        v-for="esp in especialidades" 
        :key="esp" 
        @click="selecionarEspecialidade(esp)"
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
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- 1. Paciente (Prontuário) -->
        <div class="form-group">
          <label for="filtroBusca" class="form-label font-semibold">Paciente (Prontuário)</label>
          <input 
            id="filtroBusca" 
            v-model="filtroBusca" 
            type="text" 
            placeholder="Nome ou Prontuário..." 
            class="form-control"
          />
        </div>

        <!-- 2. Procedimento (Lista de Espera) -->
        <div class="form-group">
          <label for="filtroProcedimento" class="form-label font-semibold">Procedimento (Lista de Espera)</label>
          <select id="filtroProcedimento" v-model="filtroProcedimento" class="form-control">
            <option value="">Todos</option>
            <option v-for="proc in procedimentosDaEspecialidadeAtiva" :key="proc" :value="proc">
              {{ proc }}
            </option>
          </select>
        </div>

        <!-- 3. Filtro de Data - De -->
        <div class="form-group">
          <label for="filtroDataDe" class="form-label font-semibold">De (Última Consulta EPO)</label>
          <input 
            id="filtroDataDe" 
            v-model="filtroDataDe" 
            type="date" 
            class="form-control"
          />
        </div>

        <!-- 4. Filtro de Data - Até -->
        <div class="form-group">
          <label for="filtroDataAte" class="form-label font-semibold">Até (Última Consulta EPO)</label>
          <input 
            id="filtroDataAte" 
            v-model="filtroDataAte" 
            type="date" 
            class="form-control"
          />
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
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Última Consulta EPO</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Solicitar APA</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200 text-sm">
            <tr v-for="paciente in pacientesFiltrados" :key="paciente.codigo">
              <td class="px-6 py-4 whitespace-nowrap text-gray-800 font-mono">{{ paciente.codigo }}</td>
              <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{{ paciente.nome }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-600">{{ paciente.procedimento || 'Não informado' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-600 font-mono">
                {{ formatarData(paciente.ultima_consulta_epo) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <Button @click="solicitarApa(paciente)" variant="success" size="sm" class="inline-flex items-center space-x-1">
                  <span>Solicitar APA</span>
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
import api from '../services/api';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';
import LoadingIndicator from '../components/LoadingIndicator.vue';

const toast = useToast();

// Lista completa de especialidades cirúrgicas ordenadas alfabeticamente
const especialidades = ref([
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
]);

// Mapeamento de procedimentos por especialidade
const procedimentosMap: Record<string, string[]> = {
  'Cardiologia': ['Revascularização do Miocárdio (Ponte de Safena)', 'Troca de Valva Aórtica', 'Troca de Valva Mitral', 'Implante de Marcapasso', 'Correção de CIA / CIV'],
  'Cirurgia Geral': ['Colecistectomia', 'Herniorrafia Inguinal', 'Apendicectomia', 'Gastrectomia', 'Colostomia'],
  'Ginecologia': ['Histerectomia', 'Miomectomia', 'Laparoscopia Diagnóstica', 'Colpoperineoplastia', 'Ooforectomia'],
  'Neurocirurgia': ['Craniectomia Descompressiva', 'Clipagem de Aneurisma', 'Derivação Ventrículo-Peritoneal', 'Microdiscectomia', 'Tumor Cerebral — Ressecção'],
  'Oftalmologia': ['Facoemulsificação (Catarata)', 'Trabeculectomia (Glaucoma)', 'Vitrectomia', 'Transplante de Córnea', 'Fotocoagulação a Laser'],
  'Ortopedia': ['Artroplastia Total de Quadril', 'Artroplastia Total de Joelho', 'Artroscopia de Joelho', 'Fixação de Fratura de Fêmur', 'Osteossíntese de Coluna'],
  'Otorrinolaringologia': ['Septoplastia', 'Amigdalectomia', 'Timpanoplastia', 'Adenoidectomia', 'Microcirurgia de Laringe'],
  'Plástica': ['Mamoplastia', 'Rinoplastia', 'Blefaroplastia', 'Reconstrução Mamária', 'Abdominoplastia'],
  'Torácica': ['Lobectomia', 'Pleuroscopia', 'Simpatectomia', 'Ressecção de Nódulo Pulmonar', 'Broncoscopia'],
  'Urologia': ['Prostatectomia Radical', 'Nefrectomia', 'Ureteroscopia', 'Litotripsia', 'Ressecção Transuretral de Próstata (RTUP)']
};

const especialidadeAtiva = ref('Cardiologia');
const filtroBusca = ref('');
const filtroProcedimento = ref('');
const filtroDataDe = ref('');
const filtroDataAte = ref('');

const pacientes = ref<any[]>([]);
const loading = ref(false);

const procedimentosDaEspecialidadeAtiva = computed(() => {
  return procedimentosMap[especialidadeAtiva.value] || [];
});

const selecionarEspecialidade = (esp: string) => {
  especialidadeAtiva.value = esp;
  filtroProcedimento.value = ''; // Reseta o filtro de procedimento ao mudar de especialidade
};

const carregarDados = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/pacientes');
    pacientes.value = res.data;
  } catch (error) {
    toast.error('Erro ao carregar dados dos pacientes.');
  } finally {
    loading.value = false;
  }
};

const formatarData = (dataStr: string) => {
  if (!dataStr) return '—';
  try {
    const [ano, mes, dia] = dataStr.split('-');
    return `${dia}/${mes}/${ano}`;
  } catch (e) {
    return dataStr;
  }
};

const solicitarApa = (paciente: any) => {
  toast.success(`APA (Avaliação Pré-Anestésica) solicitada com sucesso para o paciente ${paciente.nome}!`);
};

const pacientesFiltrados = computed(() => {
  return pacientes.value
    .filter(p => {
      // 1. Filtra por Especialidade Ativa (tratando a string para bater com o padrão do CSV)
      // O backend pode ter "Cardiologia" ou "Cardiologia / Cirurgia Cardíaca".
      const espNormalizada = p.especialidade || '';
      const matchEsp = espNormalizada.startsWith(especialidadeAtiva.value);
      
      // 2. Filtra por Busca de Paciente (Nome ou Código Prontuário)
      const matchBusca = !filtroBusca.value || 
        p.nome.toLowerCase().includes(filtroBusca.value.toLowerCase()) ||
        p.codigo.toString().includes(filtroBusca.value);

      // 3. Filtra por Procedimento
      const matchProcedimento = !filtroProcedimento.value || p.procedimento === filtroProcedimento.value;

      // 4. Filtra por Intervalo de Data (Última Consulta EPO)
      let matchData = true;
      if (p.ultima_consulta_epo) {
        if (filtroDataDe.value && p.ultima_consulta_epo < filtroDataDe.value) {
          matchData = false;
        }
        if (filtroDataAte.value && p.ultima_consulta_epo > filtroDataAte.value) {
          matchData = false;
        }
      } else if (filtroDataDe.value || filtroDataAte.value) {
        // Se o paciente não tiver data e o usuário filtrou por data, não exibe
        matchData = false;
      }

      return matchEsp && matchBusca && matchProcedimento && matchData;
    })
    // Ordenar da consulta mais antiga para a mais recente
    .sort((a, b) => {
      const dataA = a.ultima_consulta_epo || '9999-12-31';
      const dataB = b.ultima_consulta_epo || '9999-12-31';
      return dataA.localeCompare(dataB);
    });
});

onMounted(() => {
  carregarDados();
});
</script>
