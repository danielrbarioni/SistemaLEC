<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Perfis de Utilização</h1>
      <span class="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full border border-gray-200">
        Configurações do Sistema
      </span>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Lista de Perfis -->
      <div class="lg:col-span-2 space-y-4">
        <Card>
          <template #header>
            <h2 class="text-lg font-bold text-gray-800">Perfis Disponíveis</h2>
          </template>

          <div class="divide-y divide-gray-200">
            <div 
              v-for="perf in perfisStore.perfis" 
              :key="perf.id" 
              class="py-4 flex items-center justify-between first:pt-0 last:pb-0"
            >
              <div class="flex items-center space-x-3">
                <!-- Indicador de Cor -->
                <span :class="[getCorClass(perf.cor), 'inline-block w-3.5 h-3.5 rounded-full ring-4 ring-opacity-20 shrink-0']"></span>
                <div>
                  <div class="flex items-center space-x-2">
                    <span class="font-bold text-gray-800">{{ perf.nome }}</span>
                    <span v-if="perfisStore.perfilAtivoId === perf.id" class="px-2 py-0.5 text-[10px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200 rounded-full">
                      Ativo
                    </span>
                  </div>
                  <div class="text-xs text-gray-500 mt-0.5">
                    Tipo: <span class="font-medium text-gray-700">{{ getTipoLabel(perf.tipo) }}</span>
                    <span v-if="perf.especialidade"> | Especialidade: <span class="font-medium text-gray-700">{{ perf.especialidade }}</span></span>
                  </div>
                </div>
              </div>

              <div>
                <Button 
                  v-if="perfisStore.perfilAtivoId !== perf.id"
                  @click="perfisStore.setPerfilAtivo(perf.id)"
                  variant="primary" 
                  size="sm"
                >
                  Ativar Perfil
                </Button>
                <span v-else class="text-xs font-semibold text-emerald-600 flex items-center space-x-1">
                  <span>✓ Ativo atualmente</span>
                </span>
              </div>
            </div>
          </div>
        </Card>

        <!-- Detalhes do Perfil Ativo -->
        <Card class="bg-gradient-to-r from-gray-50 to-slate-50 border border-gray-200">
          <h3 class="font-bold text-gray-800 text-sm mb-2">Comportamento do Perfil Ativo:</h3>
          <div class="text-xs text-gray-600 space-y-2">
            <p v-if="perfisStore.perfilAtivo.tipo === 'ADMIN'">
              <strong>ADMIN (Desenvolvedor/Manutenção):</strong> Possui acesso total ao formulário do Sistema LEC, visualiza solicitações de todas as especialidades e pode aprovar/rejeitar registros.
            </p>
            <p v-else-if="perfisStore.perfilAtivo.tipo === 'GESTAO_LEC'">
              <strong>GESTÃO LEC (Equipe de Gestão):</strong> Responsável por receber e acompanhar as solicitações de todas as especialidades. O formulário de nova solicitação fica oculto. Pode aprovar ("Dar Baixa") ou rejeitar registros.
            </p>
            <p v-else>
              <strong>ESPECIALIDADE ({{ perfisStore.perfilAtivo.especialidade }}):</strong> Responsável por criar solicitações (inclusão, edição, exclusão, standby) apenas para a especialidade <strong>{{ perfisStore.perfilAtivo.especialidade }}</strong>. Visualiza no acompanhamento apenas as solicitações desta especialidade. Não pode aprovar/rejeitar registros.
            </p>
          </div>
        </Card>
      </div>

      <!-- Formulário de Criação -->
      <div class="lg:col-span-1">
        <Card>
          <template #header>
            <h2 class="text-lg font-bold text-gray-800">Criar Novo Perfil</h2>
          </template>

          <form @submit.prevent="criarPerfil" class="space-y-4">
            <div class="form-group">
              <label for="nome" class="form-label font-semibold">Nome do Perfil <span class="text-red-500">*</span></label>
              <input 
                id="nome" 
                v-model="form.nome" 
                type="text" 
                placeholder="Ex: ESPECIALIDADE UROLOGIA" 
                class="form-control"
                required
              />
            </div>

            <div class="form-group">
              <label for="tipo" class="form-label font-semibold">Tipo <span class="text-red-500">*</span></label>
              <select id="tipo" v-model="form.tipo" class="form-control" required @change="onTipoChange">
                <option value="ADMIN">ADMIN (Desenvolvedor/TI)</option>
                <option value="GESTAO_LEC">GESTÃO LEC</option>
                <option value="ESPECIALIDADE">ESPECIALIDADE</option>
              </select>
            </div>

            <div v-if="form.tipo === 'ESPECIALIDADE'" class="form-group">
              <label for="especialidade" class="form-label font-semibold">Especialidade Correspondente <span class="text-red-500">*</span></label>
              <select id="especialidade" v-model="form.especialidade" class="form-control" required>
                <option value="" disabled>Selecione...</option>
                <option v-for="esp in especialidadesDisponiveis" :key="esp" :value="esp">
                  {{ esp }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="cor" class="form-label font-semibold">Cor de Identificação <span class="text-red-500">*</span></label>
              <select id="cor" v-model="form.cor" class="form-control" required>
                <option value="cinza">Cinza (Padrão Admin)</option>
                <option value="azul">Azul (Padrão Gestão)</option>
                <option value="verde">Verde (Padrão Especialidade)</option>
              </select>
            </div>

            <Button type="submit" variant="primary" class="w-full justify-center">
              Criar Perfil
            </Button>
          </form>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useToast } from 'vue-toastification';
import { usePerfisStore } from '../stores/perfis';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';

const toast = useToast();
const perfisStore = usePerfisStore();

const especialidadesDisponiveis = [
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

const form = ref({
  nome: '',
  tipo: 'ESPECIALIDADE' as 'ADMIN' | 'GESTAO_LEC' | 'ESPECIALIDADE',
  cor: 'verde' as 'cinza' | 'azul' | 'verde',
  especialidade: ''
});

const onTipoChange = () => {
  if (form.value.tipo === 'ADMIN') {
    form.value.cor = 'cinza';
    form.value.especialidade = '';
  } else if (form.value.tipo === 'GESTAO_LEC') {
    form.value.cor = 'azul';
    form.value.especialidade = '';
  } else {
    form.value.cor = 'verde';
  }
};

const criarPerfil = () => {
  if (form.value.tipo === 'ESPECIALIDADE' && !form.value.especialidade) {
    toast.error('Selecione uma especialidade correspondente.');
    return;
  }

  perfisStore.adicionarPerfil(
    form.value.nome,
    form.value.tipo,
    form.value.cor,
    form.value.tipo === 'ESPECIALIDADE' ? form.value.especialidade : undefined
  );

  toast.success('Perfil criado com sucesso!');
  
  // Limpa o form
  form.value.nome = '';
  form.value.especialidade = '';
};

const getCorClass = (cor: string) => {
  switch (cor) {
    case 'cinza': return 'bg-gray-400 ring-gray-400';
    case 'azul': return 'bg-blue-500 ring-blue-500';
    case 'verde': return 'bg-green-500 ring-green-500';
    default: return 'bg-gray-400 ring-gray-400';
  }
};

const getTipoLabel = (tipo: string) => {
  switch (tipo) {
    case 'ADMIN': return 'Administrador';
    case 'GESTAO_LEC': return 'Gestão da LEC';
    case 'ESPECIALIDADE': return 'Especialidade Cirúrgica';
    default: return tipo;
  }
};
</script>
