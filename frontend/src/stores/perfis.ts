import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';
import { useAuthStore } from './auth';

export interface Perfil {
  id: string;
  nome: string;
  tipo: 'ADMIN' | 'GESTAO_LEC' | 'EPO_GENERALISTA' | 'ESPECIALIDADE' | 'OBSERVADOR' | 'NENHUM';
  cor: 'cinza' | 'azul' | 'laranja' | 'verde';
  especialidade?: string;
}

function sortPerfis(list: Perfil[]): Perfil[] {
  return [...list].sort((a, b) => {
    const getPeso = (p: Perfil) => {
      if (p.tipo === 'ADMIN') return 1;
      if (p.tipo === 'GESTAO_LEC') return 2;
      if (p.tipo === 'EPO_GENERALISTA' || p.id === 'EPO_GENERALISTA') return 3;
      if (p.tipo === 'ESPECIALIDADE') return 4;
      if (p.tipo === 'NENHUM' || p.tipo === 'OBSERVADOR') return 5;
      return 6;
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
      || perfis.value.find(p => p.tipo === 'NENHUM' || p.tipo === 'OBSERVADOR')
      || { id: 'NENHUM', nome: 'NENHUM', tipo: 'NENHUM', cor: 'cinza', especialidade: undefined };
  });

  const perfisDoUsuario = computed<Perfil[]>(() => {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return [];
    if (authStore.isAdmin) return perfis.value;

    const available = (authStore.user as any)?.available_profiles;
    if (Array.isArray(available) && available.length > 0) {
      const ids = available.map((ap: any) => ap.perfil_id);
      const userPerfs = perfis.value.filter(p => ids.includes(p.id));
      return userPerfs.length > 0 ? userPerfs : perfis.value.filter(p => p.tipo === 'NENHUM' || p.tipo === 'OBSERVADOR');
    }
    
    // Fallback: busca pelo perfil do usuário atual
    const userPerfilId = (authStore.user as any)?.perfil_id;
    if (userPerfilId) {
      return perfis.value.filter(p => p.id === userPerfilId);
    }

    return perfis.value.filter(p => p.tipo === 'NENHUM' || p.tipo === 'OBSERVADOR');
  });

  const podeAlternarPerfil = computed<boolean>(() => {
    const authStore = useAuthStore();
    return authStore.isAdmin || perfisDoUsuario.value.length > 1;
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
      
      const nenhumProfile = data.find((p: Perfil) => p.tipo === 'NENHUM' || p.id === 'NENHUM' || p.tipo === 'OBSERVADOR' || p.id === 'OBSERVADOR') || { id: 'NENHUM' };
      const defaultNenhumId = nenhumProfile.id;

      if (authStore.isAuthenticated) {
        if (authStore.isObservador || (authStore.user as any)?.perfil_tipo === 'NENHUM' || (authStore.user as any)?.perfil_tipo === 'OBSERVADOR') {
          setPerfilAtivoInternal(defaultNenhumId);
          return;
        }

        const userPerfilId = (authStore.user as any)?.perfil_id;
        if (userPerfilId && data.some((p: Perfil) => p.id === userPerfilId)) {
          if (perfilAtivoId.value && perfisDoUsuario.value.some(p => p.id === perfilAtivoId.value)) {
            // Mantém perfil selecionado
          } else {
            setPerfilAtivoInternal(userPerfilId);
          }
          return;
        }

        if (!authStore.isAdmin && authStore.user?.username) {
          try {
            const { data: usuariosData } = await api.get('/api/usuarios');
            const myUsers = usuariosData.filter((u: any) => u.username?.toLowerCase() === authStore.user?.username?.toLowerCase());
            if (myUsers.length > 0) {
              const matchedPerfs = data.filter((p: Perfil) => myUsers.some((u: any) => u.perfil_id === p.id));
              if (matchedPerfs.length > 0) {
                if (perfilAtivoId.value && matchedPerfs.some((p: Perfil) => p.id === perfilAtivoId.value)) {
                  // mantém seleção válida
                } else {
                  setPerfilAtivoInternal(matchedPerfs[0].id);
                }
                return;
              }
            }
            setPerfilAtivoInternal(defaultNenhumId);
            return;
          } catch (e) {
            console.error('Erro ao determinar perfil do usuário logado:', e);
            setPerfilAtivoInternal(defaultNenhumId);
            return;
          }
        }
      }

      // Se for ADMIN autenticado ou não autenticado ainda
      if (authStore.isAdmin) {
        if (!perfilAtivoId.value || !data.some((p: Perfil) => p.id === perfilAtivoId.value)) {
          setPerfilAtivoInternal(data[0]?.id || defaultNenhumId);
        }
      } else {
        // Padrão seguro para qualquer outro caso: NENHUM
        setPerfilAtivoInternal(defaultNenhumId);
      }
    } catch (error) {
      console.error('Erro ao buscar perfis:', error);
    } finally {
      loading.value = false;
    }
  }

  async function setPerfilAtivo(id: string) {
    const authStore = useAuthStore();
    const permitido = authStore.isAdmin || perfisDoUsuario.value.some(p => p.id === id) || id === 'NENHUM' || id === 'OBSERVADOR';
    if (!permitido) {
      console.warn('Usuário não possui permissão para alternar para este perfil.');
      return;
    }

    try {
      if (authStore.isAuthenticated) {
        const { data } = await api.post('/api/perfis/ativar', { perfil_id: id });
        if (data.access_token) {
          authStore.setToken(data.access_token);
          if (data.user) {
            authStore.setUser(data.user);
          }
        }
      }
    } catch (e) {
      console.error('Erro ao ativar perfil no backend:', e);
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
    perfisDoUsuario,
    podeAlternarPerfil,
    loading,
    fetchPerfis,
    setPerfilAtivo,
    adicionarPerfil
  };
});
