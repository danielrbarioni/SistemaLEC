import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';

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

  async function fetchPerfis() {
    loading.value = true;
    try {
      const { data } = await api.get('/api/perfis');
      perfis.value = data;
      // Define o perfil ativo padrão se não houver um salvo
      if (!perfilAtivoId.value && data.length > 0) {
        setPerfilAtivo(data[0].id);
      } else if (perfilAtivoId.value && !data.some((p: Perfil) => p.id === perfilAtivoId.value) && data.length > 0) {
        setPerfilAtivo(data[0].id);
      }
    } catch (error) {
      console.error('Erro ao buscar perfis:', error);
    } finally {
      loading.value = false;
    }
  }

  function setPerfilAtivo(id: string) {
    perfilAtivoId.value = id;
    localStorage.setItem('perfilAtivoId', id);
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
