import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';
import { useAuthStore } from './auth';

export interface Perfil {
  id: string;
  nome: string;
  tipo: 'ADMIN' | 'GESTAO_LEC' | 'ESPECIALIDADE';
  cor: 'cinza' | 'azul' | 'verde';
  especialidade?: string;
}

export const usePerfisStore = defineStore('perfis', () => {
  const perfis = ref<Perfil[]>([]);
  const loading = ref(false);

  const perfilAtivoId = ref<string>(localStorage.getItem('perfilAtivoId') || '');

  const perfilAtivo = computed(() => {
    return perfis.value.find(p => p.id === perfilAtivoId.value) || perfis.value[0] || { id: '', nome: 'SEM PERFIL', tipo: 'ESPECIALIDADE', cor: 'cinza' };
  });

  function setPerfilAtivoInternal(id: string) {
    perfilAtivoId.value = id;
    localStorage.setItem('perfilAtivoId', id);
  }

  async function fetchPerfis() {
    loading.value = true;
    try {
      const { data } = await api.get('/api/perfis');
      perfis.value = data;

      const authStore = useAuthStore();
      
      // Se não for ADMIN e estiver autenticado, tenta buscar o perfil vinculado ao usuário cadastrado
      if (authStore.isAuthenticated && !authStore.isAdmin && authStore.user?.username) {
        try {
          const { data: usuariosData } = await api.get('/api/usuarios');
          const meUser = usuariosData.find((u: any) => u.username?.toLowerCase() === authStore.user?.username?.toLowerCase());
          if (meUser && meUser.perfil_id && data.some((p: Perfil) => p.id === meUser.perfil_id)) {
            setPerfilAtivoInternal(meUser.perfil_id);
            return;
          }
        } catch (e) {
          console.error('Erro ao determinar perfil do usuário logado:', e);
        }
      }

      // Define o perfil ativo padrão se não houver um salvo
      if (!perfilAtivoId.value && data.length > 0) {
        setPerfilAtivoInternal(data[0].id);
      } else if (perfilAtivoId.value && !data.some((p: Perfil) => p.id === perfilAtivoId.value) && data.length > 0) {
        setPerfilAtivoInternal(data[0].id);
      }
    } catch (error) {
      console.error('Erro ao buscar perfis:', error);
    } finally {
      loading.value = false;
    }
  }

  function setPerfilAtivo(id: string) {
    const authStore = useAuthStore();
    // Apenas ADMIN pode alternar manualmente entre perfis
    if (!authStore.isAdmin && perfilAtivoId.value) {
      console.warn('Apenas usuários ADMIN podem alternar entre perfis.');
      return;
    }
    setPerfilAtivoInternal(id);
  }

  async function adicionarPerfil(nome: string, especialidade?: string) {
    try {
      const { data } = await api.post('/api/perfis', {
        nome,
        especialidade
      });
      perfis.value.push(data);
      return data;
    } catch (error) {
      console.error('Erro ao adicionar perfil:', error);
      throw error;
    }
  }

  return {
    perfis,
    perfilAtivoId,
    perfilAtivo,
    loading,
    fetchPerfis,
    setPerfilAtivo,
    adicionarPerfil
  };
});
