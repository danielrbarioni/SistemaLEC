<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">Controle de Acessos e Usuários</h1>
      <span class="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full border border-gray-200">
        Configurações do Sistema
      </span>
    </div>

    <!-- Seletor de Perfil Ativo rápido (se necessário para debug/desenvolvimento) -->
    <div v-if="perfisStore.loading" class="text-center py-6 text-gray-500">
      <span class="inline-block animate-spin border-4 border-emerald-500 border-t-transparent w-8 h-8 rounded-full mr-2 align-middle"></span>
      Carregando dados...
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Lista de Perfis & Usuários -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Perfis Disponíveis -->
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
                <span :class="[getCorClass(perf.tipo), 'inline-block w-3.5 h-3.5 rounded-full ring-4 ring-opacity-20 shrink-0']"></span>
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
                  @click="alterarPerfilAtivo(perf.id)"
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
              <strong>ADMIN (Desenvolvedor/Manutenção):</strong> Possui acesso total ao formulário do Sistema LEC, visualiza solicitações de todas as especialidades e pode aprovar/rejeitar registros. Tem permissão para criar perfis e qualquer tipo de usuário.
            </p>
            <p v-else-if="perfisStore.perfilAtivo.tipo === 'GESTAO_LEC'">
              <strong>GESTÃO LEC (Equipe de Gestão):</strong> Responsável por receber e acompanhar as solicitações de todas as especialidades. O formulário de nova solicitação fica oculto. Pode aprovar ("Dar Baixa") ou rejeitar registros. Tem permissão para criar perfis e usuários do tipo GESTÃO LEC ou ESPECIALIDADE.
            </p>
            <p v-else>
              <strong>ESPECIALIDADE ({{ perfisStore.perfilAtivo.especialidade }}):</strong> Responsável por criar solicitações (inclusão, edição, exclusão, standby) apenas para a especialidade <strong>{{ perfisStore.perfilAtivo.especialidade }}</strong>. Visualiza no acompanhamento apenas as solicitações desta especialidade. Não pode aprovar/rejeitar registros. Tem permissão para criar usuários unicamente vinculados à sua própria especialidade.
            </p>
          </div>
        </Card>

        <!-- Usuários Cadastrados Localmente -->
        <Card>
          <template #header>
            <h2 class="text-lg font-bold text-gray-800">Usuários Locais Cadastrados</h2>
          </template>

          <div v-if="usuarios.length === 0" class="text-center py-6 text-gray-500 text-sm">
            Nenhum usuário cadastrado localmente no SQLite.
          </div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Nome / Username</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Perfil ID</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Especialidade</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="user in usuarios" :key="user.id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-bold text-gray-800">{{ user.nome }}</div>
                    <div class="text-xs text-gray-500">@{{ user.username }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs font-semibold rounded bg-gray-100 text-gray-800 border border-gray-200">
                      {{ user.perfil_id }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {{ user.especialidade || '—' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      <!-- Formulários de Criação (Lateral) -->
      <div class="lg:col-span-1 space-y-6">
        <!-- Formulário: Criar Usuário -->
        <Card>
          <template #header>
            <h2 class="text-lg font-bold text-gray-800">Criar Usuário</h2>
          </template>

          <form @submit.prevent="criarUsuario" class="space-y-4">
            <div class="form-group">
              <label for="usr_username" class="form-label font-semibold">Usuário (usuário Ebserh) <span class="text-red-500">*</span></label>
              <input 
                id="usr_username" 
                v-model="usuarioForm.username" 
                type="text" 
                placeholder="Ex: joao.silva" 
                class="form-control"
                required
              />
            </div>

            <div class="form-group">
              <label for="usr_nome" class="form-label font-semibold">Nome completo <span class="text-red-500">*</span></label>
              <input 
                id="usr_nome" 
                v-model="usuarioForm.nome" 
                type="text" 
                placeholder="Ex: Dr. João Silva" 
                class="form-control"
                required
              />
            </div>

            <div class="form-group">
              <label for="usr_perfil" class="form-label font-semibold">Perfil de Acesso <span class="text-red-500">*</span></label>
              <select id="usr_perfil" v-model="usuarioForm.perfil_id" class="form-control" required>
                <option value="" disabled>Selecione...</option>
                <option v-for="perf in perfisFiltrados" :key="perf.id" :value="perf.id">
                  {{ perf.nome }} ({{ getTipoLabel(perf.tipo) }})
                </option>
              </select>
            </div>

            <Button type="submit" variant="primary" class="w-full justify-center">
              Criar Usuário
            </Button>
          </form>
        </Card>

        <!-- Formulário: Criar Novo Perfil -->
        <Card v-if="podeCriarPerfil">
          <template #header>
            <h2 class="text-lg font-bold text-gray-800">Criar Novo Perfil</h2>
          </template>

          <form @submit.prevent="criarPerfil" class="space-y-4">
            <div class="form-group">
              <label for="tipo_perfil" class="form-label font-semibold">Tipo</label>
              <input 
                id="tipo_perfil" 
                type="text" 
                value="Especialidade Cirúrgica" 
                class="form-control bg-gray-100 cursor-not-allowed"
                disabled
              />
            </div>

            <div class="form-group">
              <label for="especialidade" class="form-label font-semibold">Nome da Especialidade <span class="text-red-500">*</span></label>
              <input 
                id="especialidade" 
                v-model="perfilForm.especialidade" 
                type="text" 
                placeholder="Ex: Plástica" 
                class="form-control"
                required
              />
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
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import { usePerfisStore } from '../stores/perfis';
import api from '../services/api';
import Card from '../components/Card.vue';
import Button from '../components/Button.vue';

const toast = useToast();
const perfisStore = usePerfisStore();

const usuarios = ref<any[]>([]);

// Formulários
const perfilForm = ref({
  nome: '',
  especialidade: ''
});

const usuarioForm = ref({
  nome: '',
  username: '',
  perfil_id: ''
});

// Regras de Visualização/Permissão baseadas no perfil ativo
const podeCriarPerfil = computed(() => {
  const tipo = perfisStore.perfilAtivo.tipo;
  return tipo === 'ADMIN' || tipo === 'GESTAO_LEC';
});

// Dropdown dinâmico de perfis para criação de usuário conforme regras hierárquicas
const perfisFiltrados = computed(() => {
  const tipo = perfisStore.perfilAtivo.tipo;
  const esp = perfisStore.perfilAtivo.especialidade;

  if (tipo === 'ADMIN') {
    // ADMIN pode criar qualquer perfil
    return perfisStore.perfis;
  } else if (tipo === 'GESTAO_LEC') {
    // GESTÃO LEC pode criar GESTÃO LEC ou ESPECIALIDADES
    return perfisStore.perfis.filter(p => p.tipo === 'GESTAO_LEC' || p.tipo === 'ESPECIALIDADE');
  } else if (tipo === 'ESPECIALIDADE' && esp) {
    // ESPECIALIDADE só pode criar usuários da sua própria especialidade
    return perfisStore.perfis.filter(p => p.tipo === 'ESPECIALIDADE' && p.especialidade === esp);
  }
  return [];
});

const loadUsuarios = async () => {
  try {
    const { data } = await api.get('/api/usuarios');
    usuarios.value = data;
  } catch (error) {
    console.error('Erro ao carregar usuários:', error);
  }
};

const alterarPerfilAtivo = (id: string) => {
  perfisStore.setPerfilAtivo(id);
  toast.success('Perfil de utilização alterado!');
};

const criarPerfil = async () => {
  if (!perfilForm.value.especialidade) {
    toast.error('Informe o nome da especialidade.');
    return;
  }

  try {
    const nomePerfil = perfilForm.value.especialidade.trim().toUpperCase();
    await perfisStore.adicionarPerfil(
      nomePerfil,
      perfilForm.value.especialidade.trim()
    );

    toast.success('Perfil criado com sucesso!');
    perfilForm.value.especialidade = '';
    
    // Atualiza perfis
    await perfisStore.fetchPerfis();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao criar perfil.';
    toast.error(detail);
  }
};

const criarUsuario = async () => {
  try {
    await api.post('/api/usuarios', {
      nome: usuarioForm.value.nome,
      username: usuarioForm.value.username.trim(),
      perfil_id: usuarioForm.value.perfil_id
    });

    toast.success('Usuário vinculado com sucesso!');
    
    // Limpa form
    usuarioForm.value.nome = '';
    usuarioForm.value.username = '';
    usuarioForm.value.perfil_id = '';

    // Recarrega lista
    await loadUsuarios();
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao vincular usuário.';
    toast.error(detail);
  }
};

const getCorClass = (tipo: string) => {
  switch (tipo) {
    case 'ADMIN': return 'bg-gray-400 ring-gray-400';
    case 'GESTAO_LEC': return 'bg-blue-500 ring-blue-500';
    case 'ESPECIALIDADE': return 'bg-green-500 ring-green-500';
    default: return 'bg-gray-400 ring-gray-400';
  }
};

const getTipoLabel = (tipo: string) => {
  switch (tipo) {
    case 'ADMIN': return 'ADMIN';
    case 'GESTAO_LEC': return 'Gestão da LEC';
    case 'ESPECIALIDADE': return 'Especialidade Cirúrgica';
    default: return tipo;
  }
};

onMounted(async () => {
  await perfisStore.fetchPerfis();
  await loadUsuarios();
});
</script>
