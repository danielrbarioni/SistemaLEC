import { createRouter, createWebHistory, NavigationGuardNext } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Admin from '../views/Admin.vue';

import Exemplos from '../views/Exemplos.vue';
import Pacientes from '../views/Pacientes.vue';
import InteracoesLec from '../views/InteracoesLec.vue';
import NavegacaoLec from '../views/NavegacaoLec.vue';
import Perfis from '../views/Perfis.vue';
import Historico from '../views/Historico.vue';


const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { layout: 'LoginLayout' },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { requiresAuth: true },
  },

  {
    path: '/exemplos',
    name: 'Exemplos',
    component: Exemplos,
  },
  {
    path: '/pacientes',
    name: 'Pacientes',
    component: Pacientes,
    meta: { requiresAuth: true },
  },
  {
    path: '/interacoes',
    name: 'Interações LEC',
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
  // Pinia store must be used inside a function to ensure it's initialized
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' });
  } else {
    next();
  }
});

export default router;
