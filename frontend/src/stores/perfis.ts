import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';
import { useAuthStore } from './auth';

export interface Perfil {
  id: string;
  nome: string;
  tipo: 'ADMIN' | 'GESTAO_LEC' | 'ESPECIALIDADE' | 'OBSERVADOR';
  cor: 'cinza' | 'azul' | 'verde';
  especialidade?: string;
}

function sortPerfis(list: Perfil[]): Perfil[] {
  return [...list].sort((a, b) => {
    const getPeso = (p: Perfil) => {
      if (p.tipo === 'ADMIN') return 1;
      if (p.tipo === 'GESTAO_LEC') return 2;
      if (p.tipo === 'ESPECIALIDADE') return 3;
      if (p.tipo === 'OBSERVADOR') return 4;
      return 5;
    };
    const pesoA = getPeso(a);
    const pesoB = getPeso(b);
    if (pesoA !== pesoB) return pesoA - pesoB;

    const nomeA = (a.especialidade || a.nome || '').trim();
    const nomeB = (b.especialidade || b.nome || '').trim();
    return nomeA.localeCompare(nomeB, 'pt-BR');
  });
}

export const usePerfisStore = defineStore('perfis', () => {
  const perfis = ref<Perfil[]>([]);
  const loading = ref(false);

  const perfilAtivoId = ref<string>(localStorage.getItem('perfilAtivoId') || '');

  const perfilAtivo = computed<Perfil>(() => {
    return perfis.value.find(p => p.id === perfilAtivoId.value) 
      || perfis.value.find(p => p.tipo === 'OBSERVADOR')
      || { id: 'OBSERVADOR', nome: 'OBSERVADOR', tipo: 'OBSERVADOR', cor: 'cinza', especialidade: undefined };
  });

  function setPerfilAtivoInternal(id: string) {
    perfilAtivoId.value = id;
    localStorage.setItem('perfilAtivoId', id);
  }

  async function fetchPerfis() {
    loading.value = true;
    try {
      const { data } = await api.get('/api/perfis');
      perfis.value = sortPerfis(data);

      const authStore = useAuthStore();
      
      const observadorProfile = data.find((p: Perfil) => p.tipo === 'OBSERVADOR' || p.id === 'OBSERVADOR') || { id: 'OBSERVADOR' };
      const defaultObservadorId = observadorProfile.id;

      if (authStore.isAuthenticated) {
        if (authStore.isObservador || (authStore.user as any)?.perfil_tipo === 'OBSERVADOR') {
          setPerfilAtivoInternal(defaultObservadorId);
          return;
        }

        if (!authStore.isAdmin && authStore.user?.username) {
          try {
            const { data: usuariosData } = await api.get('/api/usuarios');
            const meUser = usuariosData.find((u: any) => u.username?.toLowerCase() === authStore.user?.username?.toLowerCase());
            if (meUser && meUser.perfil_id && data.some((p: Perfil) => p.id === meUser.perfil_id)) {
              setPerfilAtivoInternal(meUser.perfil_id);
              return;
            } else {
              // Usuário não cadastrado na tabela de usuários ou sem perfil específico -> OBSERVADOR
              setPerfilAtivoInternal(defaultObservadorId);
              return;
            }
          } catch (e) {
            console.error('Erro ao determinar perfil do usuário logado:', e);
            setPerfilAtivoInternal(defaultObservadorId);
            return;
          }
        }
      }

      // Se for ADMIN autenticado ou não autenticado ainda
      if (authStore.isAdmin) {
        if (!perfilAtivoId.value || !data.some((p: Perfil) => p.id === perfilAtivoId.value)) {
          setPerfilAtivoInternal(data[0]?.id || defaultObservadorId);
        }
      } else {
        // Padrão seguro para qualquer outro caso: OBSERVADOR
        setPerfilAtivoInternal(defaultObservadorId);
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
