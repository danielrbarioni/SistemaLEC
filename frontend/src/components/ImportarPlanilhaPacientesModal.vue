<template>
  <Modal :show="show" @close="handleClose">
    <template #header>
      <div class="flex items-center space-x-2 text-slate-800">
        <DocumentArrowUpIcon class="h-6 w-6 text-emerald-600" />
        <span>Importar Planilha de Pacientes (Gestão LEC)</span>
      </div>
    </template>

    <div class="space-y-5">
      <!-- Instruções das Colunas -->
      <div class="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs text-slate-600 space-y-2">
        <div class="font-bold text-slate-800 flex items-center space-x-1.5">
          <InformationCircleIcon class="h-4 w-4 text-emerald-600 shrink-0" />
          <span>Estrutura de Colunas Esperada (Excel .xlsx / .xls)</span>
        </div>
        <p class="text-slate-500">
          A planilha deve conter o cabeçalho na primeira linha e as colunas organizadas exatamente de A até L:
        </p>
        <div class="grid grid-cols-2 gap-x-4 gap-y-1 font-mono text-[11px] bg-white p-2.5 rounded-lg border border-slate-200">
          <div><strong class="text-slate-700">A:</strong> id_fila</div>
          <div><strong class="text-slate-700">G:</strong> id_motivo_status</div>
          <div><strong class="text-slate-700">B:</strong> Prontuário</div>
          <div><strong class="text-slate-700">H:</strong> <i>(ignorado)</i></div>
          <div><strong class="text-slate-700">C:</strong> id_procedimento</div>
          <div><strong class="text-slate-700">I:</strong> id_especialidade</div>
          <div><strong class="text-slate-700">D:</strong> medico_responsavel</div>
          <div><strong class="text-slate-700">J:</strong> swalis</div>
          <div><strong class="text-slate-700">E:</strong> <i>(ignorado)</i></div>
          <div><strong class="text-slate-700">K:</strong> sin_judicializado</div>
          <div><strong class="text-slate-700">F:</strong> <i>(ignorado)</i></div>
          <div><strong class="text-slate-700">L:</strong> dth_indicação</div>
        </div>
      </div>

      <!-- Seletor de Arquivo -->
      <div v-if="!resultado" class="space-y-4">
        <!-- Seletor de Especialidade Alvo -->
        <div class="space-y-1.5">
          <label class="block text-xs font-semibold text-slate-700">
            Especialidade Alvo da Planilha <span class="text-rose-500">*</span>
          </label>
          <select 
            v-model="especialidadeSelecionada"
            class="w-full text-xs bg-white border border-slate-300 rounded-lg px-3 py-2.5 text-slate-800 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 font-medium shadow-sm"
            :disabled="enviando"
          >
            <option value="" disabled>-- Selecione a especialidade da planilha --</option>
            <option 
              v-for="esp in especialidadesDisponiveis" 
              :key="esp.id" 
              :value="esp.especialidade || esp.nome"
            >
              {{ esp.especialidade || esp.nome }}
            </option>
          </select>
          <p class="text-[11px] text-slate-500 italic">
            * Todas as solicitações da planilha serão atribuídas a esta especialidade. Se o perfil da especialidade não existir, crie-o antes na tela de Perfis.
          </p>
        </div>

        <label 
          class="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-colors relative"
          :class="isDragging ? 'border-emerald-600 bg-emerald-100/60 scale-[0.99]' : (arquivoSelecionado ? 'border-emerald-500 bg-emerald-50/40' : 'border-slate-300 bg-slate-50 hover:bg-slate-100')"
          @dragenter.prevent="handleDragEnter"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleDrop"
        >
          <div class="flex flex-col items-center justify-center pt-4 pb-5 text-center px-4 pointer-events-none">
            <DocumentTextIcon v-if="arquivoSelecionado" class="w-9 h-9 text-emerald-600 mb-1.5" />
            <CloudArrowUpIcon v-else class="w-9 h-9 text-slate-400 mb-1.5" />
            
            <p v-if="arquivoSelecionado" class="text-sm font-semibold text-emerald-800 break-all">
              {{ arquivoSelecionado.name }}
            </p>
            <p v-else class="text-xs text-slate-600">
              <span class="font-semibold text-emerald-600">Clique para escolher</span> ou arraste a planilha aqui
            </p>
            <p class="text-[11px] text-slate-400 mt-0.5">Arquivos suportados: .xlsx, .xls</p>
          </div>
          <input 
            type="file" 
            accept=".xlsx, .xls" 
            class="hidden" 
            @change="handleFileSelect"
            :disabled="enviando"
          />
        </label>

        <!-- Mensagem de erro de validação local / API -->
        <div v-if="erroMensagem" class="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 font-medium flex items-start space-x-2">
          <ExclamationTriangleIcon class="h-4 w-4 text-rose-500 shrink-0 mt-0.5" />
          <span>{{ erroMensagem }}</span>
        </div>
      </div>

      <!-- Relatório de Resultado -->
      <div v-else class="space-y-4">
        <div class="p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-2">
          <div class="flex items-center space-x-2 text-emerald-800 font-bold text-sm">
            <CheckCircleIcon class="h-5 w-5 text-emerald-600" />
            <span>Importação concluída com sucesso!</span>
          </div>
          
          <div class="grid grid-cols-3 gap-2 text-center pt-2">
            <div class="bg-white p-2.5 rounded-lg border border-emerald-100 shadow-sm">
              <span class="text-xs text-slate-500 block">Total Linhas</span>
              <span class="text-lg font-bold text-slate-800">{{ resultado.total_linhas }}</span>
            </div>
            <div class="bg-white p-2.5 rounded-lg border border-emerald-100 shadow-sm">
              <span class="text-xs text-slate-500 block">Criadas</span>
              <span class="text-lg font-bold text-emerald-600">{{ resultado.solicitacoes_criadas }}</span>
            </div>
            <div class="bg-white p-2.5 rounded-lg border border-emerald-100 shadow-sm">
              <span class="text-xs text-slate-500 block">Atualizadas</span>
              <span class="text-lg font-bold text-blue-600">{{ resultado.solicitacoes_atualizadas }}</span>
            </div>
          </div>
        </div>

        <!-- Novos médicos cadastrados sem nome completo -->
        <div v-if="resultado.novos_medicos && resultado.novos_medicos.length > 0" class="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs space-y-1.5">
          <div class="font-bold text-amber-800 flex items-center space-x-1.5">
            <UserPlusIcon class="h-4 w-4 text-amber-600 shrink-0" />
            <span>Novos médicos autocadastrados (pendentes de nome completo):</span>
          </div>
          <ul class="list-disc list-inside text-amber-700 font-mono text-[11px] space-y-0.5 max-h-24 overflow-y-auto">
            <li v-for="(med, i) in resultado.novos_medicos" :key="i">
              {{ med.username }} ({{ med.especialidade }})
            </li>
          </ul>
        </div>

        <!-- Erros ou Avisos por Linha -->
        <div v-if="resultado.erros && resultado.erros.length > 0" class="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs space-y-1.5">
          <div class="font-bold text-rose-800 flex items-center space-x-1.5">
            <ExclamationCircleIcon class="h-4 w-4 text-rose-600 shrink-0" />
            <span>Avisos / Erros de Processamento:</span>
          </div>
          <ul class="list-disc list-inside text-rose-700 font-mono text-[11px] space-y-0.5 max-h-28 overflow-y-auto">
            <li v-for="(err, i) in resultado.erros" :key="i">
              {{ err }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <template #footer>
      <button
        type="button"
        @click="handleClose"
        class="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition"
        :disabled="enviando"
      >
        {{ resultado ? 'Fechar' : 'Cancelar' }}
      </button>

      <button
        v-if="!resultado"
        type="button"
        @click="processarEnvio"
        :disabled="!arquivoSelecionado || !especialidadeSelecionada || enviando"
        class="flex items-center space-x-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-semibold rounded-lg shadow-sm transition"
      >
        <span v-if="enviando" class="inline-block animate-spin h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full mr-1"></span>
        <span>{{ enviando ? 'Processando Planilha...' : 'Confirmar Importação' }}</span>
      </button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import Modal from './Modal.vue';
import { 
  DocumentArrowUpIcon, 
  InformationCircleIcon, 
  CloudArrowUpIcon, 
  DocumentTextIcon, 
  ExclamationTriangleIcon, 
  CheckCircleIcon,
  UserPlusIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline';
import { importarPlanilhaPacientes, type ImportacaoResultado } from '../services/pacienteService';
import { usePerfisStore } from '../stores/perfis';

defineProps({
  show: { type: Boolean, default: false }
});

const emit = defineEmits(['close', 'sucesso']);

const perfisStore = usePerfisStore();
const arquivoSelecionado = ref<File | null>(null);
const especialidadeSelecionada = ref('');
const enviando = ref(false);
const erroMensagem = ref('');
const resultado = ref<ImportacaoResultado | null>(null);
const isDragging = ref(false);
let dragCounter = 0;

const especialidadesDisponiveis = computed(() => {
  return perfisStore.perfis.filter(p => p.tipo === 'ESPECIALIDADE' || (p.especialidade && p.especialidade.trim() !== ''));
});

function preventWindowDrop(e: DragEvent) {
  e.preventDefault();
}

onMounted(() => {
  window.addEventListener('dragover', preventWindowDrop);
  window.addEventListener('drop', preventWindowDrop);
  perfisStore.fetchPerfis();
});

onUnmounted(() => {
  window.removeEventListener('dragover', preventWindowDrop);
  window.removeEventListener('drop', preventWindowDrop);
});

function handleDragEnter(event: DragEvent) {
  event.preventDefault();
  dragCounter++;
  isDragging.value = true;
}

function handleDragOver(event: DragEvent) {
  event.preventDefault();
  isDragging.value = true;
}

function handleDragLeave(event: DragEvent) {
  event.preventDefault();
  dragCounter--;
  if (dragCounter <= 0) {
    dragCounter = 0;
    isDragging.value = false;
  }
}

function handleDrop(event: DragEvent) {
  event.preventDefault();
  dragCounter = 0;
  isDragging.value = false;
  erroMensagem.value = '';
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    const file = event.dataTransfer.files[0];
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      erroMensagem.value = 'Selecione apenas arquivos Excel com extensão .xlsx ou .xls';
      arquivoSelecionado.value = null;
      return;
    }
    arquivoSelecionado.value = file;
  }
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement;
  erroMensagem.value = '';
  if (target.files && target.files.length > 0) {
    const file = target.files[0];
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      erroMensagem.value = 'Selecione apenas arquivos Excel com extensão .xlsx ou .xls';
      arquivoSelecionado.value = null;
      return;
    }
    arquivoSelecionado.value = file;
  }
}

async function processarEnvio() {
  if (!arquivoSelecionado.value) return;

  if (!especialidadeSelecionada.value) {
    erroMensagem.value = 'Selecione a especialidade alvo da planilha antes de prosseguir.';
    return;
  }

  enviando.value = true;
  erroMensagem.value = '';

  try {
    const res = await importarPlanilhaPacientes(arquivoSelecionado.value, especialidadeSelecionada.value);
    resultado.value = res;
    emit('sucesso', res);
  } catch (err: any) {
    console.error('Erro ao importar planilha:', err);
    if (err?.response?.status === 405) {
      erroMensagem.value = 'Método HTTP não permitido (405). Verifique a rota do servidor.';
    } else {
      erroMensagem.value = err?.response?.data?.detail || err?.message || 'Erro ao processar a planilha. Verifique a estrutura e tente novamente.';
    }
  } finally {
    enviando.value = false;
  }
}

function handleClose() {
  if (enviando.value) return;
  arquivoSelecionado.value = null;
  especialidadeSelecionada.value = '';
  erroMensagem.value = '';
  resultado.value = null;
  dragCounter = 0;
  isDragging.value = false;
  emit('close');
}
</script>
