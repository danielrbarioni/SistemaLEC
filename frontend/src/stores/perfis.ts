import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface Perfil {
  id: string;
  nome: string;
  tipo: 'ADMIN' | 'GESTAO_LEC' | 'ESPECIALIDADE';
  cor: 'cinza' | 'azul' | 'verde';
  especialidade?: string;
}

export const usePerfisStore = defineStore('perfis', () => {
  const perfis = ref<Perfil[]>([
    { id: '1', nome: 'ADMIN', tipo: 'ADMIN', cor: 'cinza' },
    { id: '2', nome: 'GESTÃO LEC', tipo: 'GESTAO_LEC', cor: 'azul' },
    { id: '3', nome: 'PLÁSTICA', tipo: 'ESPECIALIDADE', cor: 'verde', especialidade: 'Plástica' }
  ]);

  const perfilAtivoId = ref<string>(localStorage.getItem('perfilAtivoId') || '1');

  const perfilAtivo = computed(() => {
    return perfis.value.find(p => p.id === perfilAtivoId.value) || perfis.value[0];
  });

  function setPerfilAtivo(id: string) {
    perfilAtivoId.value = id;
    localStorage.setItem('perfilAtivoId', id);
  }

  function adicionarPerfil(nome: string, tipo: 'ADMIN' | 'GESTAO_LEC' | 'ESPECIALIDADE', cor: 'cinza' | 'azul' | 'verde', especialidade?: string) {
    const novo: Perfil = {
      id: Date.now().toString(),
      nome: nome.toUpperCase(),
      tipo,
      cor,
      especialidade
    };
    perfis.value.push(novo);
  }

  return {
    perfis,
    perfilAtivoId,
    perfilAtivo,
    setPerfilAtivo,
    adicionarPerfil
  };
});
