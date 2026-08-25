import { createRouter, createWebHistory, NavigationGuardNext } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { usePerfisStore } from '../stores/perfis';
import { useToast } from 'vue-toastification';
import Login from '../views/Login.vue';

import Pacientes from '../views/Pacientes.vue';
import InteracoesLec from '../views/InteracoesLec.vue';
import NavegacaoLec from '../views/NavegacaoLec.vue';
import Perfis from '../views/Perfis.vue';
import Historico from '../views/Historico.vue';


const routes = [
  {
    path: '/',
    redirect: '/interacoes',
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { layout: 'LoginLayout' },
  },
  {
    path: '/pacientes',
    name: 'Pacientes',
    component: Pacientes,
    meta: { requiresAuth: true },
  },
  {
    path: '/interacoes',
    name: 'Solicitações LEC',
    component: InteracoesLec,
    meta: { requiresAuth: true },
  },
  {
    path: '/navegacao',
    name: 'Navegação',
    component: NavegacaoLec,
    meta: { requiresAuth: true },
  },
  {
    path: '/historico',
    name: 'Histórico',
    component: Historico,
    meta: { requiresAuth: true },
  },
  {
    path: '/perfis',
    name: 'Perfis',
    component: Perfis,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  linkActiveClass: 'bg-paper-active-link',
  linkExactActiveClass: 'bg-paper-active-link',
});

router.beforeEach((to, _from, next: NavigationGuardNext) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' });
  } else {
    const perfisStore = usePerfisStore();
    const perfilTipo = perfisStore.perfilAtivo?.tipo;

    if (perfilTipo === 'NENHUM' || perfilTipo === 'OBSERVADOR') {
      if (to.path !== '/perfis' && to.name !== 'Login' && to.name !== 'Perfis') {
        try {
          const toast = useToast();
          toast.error('Solicite criação de usuário e associação a um perfil, no menu Perfis');
        } catch {
          // Fallback silencioso ou alert se toast falhar
        }
        next({ name: 'Perfis' });
        return;
      }
    }

    if (to.path === '/navegacao') {
      if (perfilTipo !== 'ADMIN') {
        next({ path: '/interacoes' });
        return;
      }
    }

    next();
  }
});

export default router;
