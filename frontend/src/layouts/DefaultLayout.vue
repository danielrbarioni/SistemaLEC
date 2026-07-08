<template>
  <div class="relative h-screen overflow-hidden md:flex">
    <!-- Mobile Menu -->
    <div class="bg-paper-sidebar text-gray-100 flex justify-between md:hidden shrink-0">
      <router-link to="/" class="block p-4 text-white font-bold">Gestão LEC HC-UFPE</router-link>
      <button @click="sidebarOpen = !sidebarOpen" class="p-4 focus:outline-none focus:bg-paper-active-link">
        <Bars3Icon class="h-6 w-6" />
      </button>
    </div>

    <!-- Sidebar -->
    <aside :class="{ '-translate-x-full': !sidebarOpen }" class="bg-paper-sidebar text-gray-100 w-64 space-y-6 py-7 px-2 absolute inset-y-0 left-0 transform md:relative md:translate-x-0 transition duration-200 ease-in-out z-20 h-full shrink-0">
      <div @click="() => router.push('/')" class="cursor-pointer text-white flex items-center space-x-2 px-4">
        <ClipboardDocumentListIcon class="h-8 w-8"/>
        <span class="text-2xl font-extrabold">Gestão LEC HC-UFPE</span>
      </div>
      <div class="px-4 my-6">
        <div class="border-t border-white border-opacity-20"></div>
      </div>

      <nav>
        <router-link to="/" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 text-red-400 hover:bg-red-500/10 hover:text-red-300">
          <HomeIcon class="h-6 w-6 text-red-400"/>
          <span>Home</span>
        </router-link>



            <router-link to="/exemplos" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 text-red-400 hover:bg-red-500/10 hover:text-red-300">
              <BeakerIcon class="h-6 w-6 text-red-400" />
              <span>Exemplos</span>
            </router-link>
            <router-link v-if="authStore.isAuthenticated" to="/pacientes" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
              <UsersIcon class="h-6 w-6" />
              <span>Pacientes</span>
            </router-link>
            <router-link v-if="authStore.isAuthenticated" to="/interacoes" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
              <ComputerDesktopIcon class="h-6 w-6" />
              <span>Sistema LEC</span>
            </router-link>
            <router-link v-if="authStore.isAuthenticated" to="/navegacao" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white w-full">
              <MapIcon class="h-6 w-6" />
              <span>Navegação</span>
              <ClockIcon class="h-4 w-4 text-amber-400 animate-pulse ml-auto" title="Aguardando liberação / Em desenvolvimento" />
            </router-link>

        
        <router-link v-if="authStore.isAdmin" to="/admin" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 text-red-400 hover:bg-red-500/10 hover:text-red-300">
          <ShieldCheckIcon class="h-6 w-6 text-red-400"/>
          <span>Admin</span>
        </router-link>

        <router-link v-if="authStore.isAuthenticated" to="/historico" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <ClockIcon class="h-6 w-6" />
          <span>Histórico</span>
        </router-link>

        <router-link v-if="authStore.isAuthenticated" to="/perfis" class="flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 hover:bg-paper-active-link hover:text-white">
          <UserGroupIcon class="h-6 w-6" />
          <span>Perfis</span>
        </router-link>


      </nav>
    </aside>

    <!-- Content -->
    <div class="flex-1 flex flex-col bg-paper-bg overflow-y-auto h-full">
      <header class="flex justify-between items-center p-6 bg-white/80 backdrop-blur-md border-b border-gray-300 sticky top-0 z-10">
        <div>
          <h1 class="text-2xl font-semibold text-paper-text">{{ $route.name }}</h1>
        </div>
        <div class="flex items-center space-x-4">
          <!-- Profile Switcher for Dev/Testing -->
          <div v-if="authStore.isAuthenticated" class="flex items-center space-x-2 bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1.5 shadow-sm">
            <span class="text-[10px] uppercase font-bold text-gray-400">Perfil:</span>
            <select 
              v-model="perfisStore.perfilAtivoId"
              @change="perfisStore.setPerfilAtivo(perfisStore.perfilAtivoId)"
              class="text-xs font-semibold bg-transparent border-none focus:ring-0 text-gray-700 cursor-pointer"
            >
              <option v-for="perf in perfisStore.perfis" :key="perf.id" :value="perf.id">
                {{ perf.nome }}
              </option>
            </select>
          </div>

          <router-link v-if="!authStore.isAuthenticated" to="/login">
            <Button variant="primary">
              <template #icon>
                <ArrowRightOnRectangleIcon class="h-5 w-5" />
              </template>
              Login
            </Button>
          </router-link>
          <ProfileDropdown v-else />
        </div>
      </header>
      <main class="flex-1">
        <div class="container py-4 md:py-6">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  HomeIcon,
  BeakerIcon,
  UsersIcon,
  ShieldCheckIcon,
  ClipboardDocumentListIcon,
  Bars3Icon,
  ArrowRightOnRectangleIcon,
  ComputerDesktopIcon,
  MapIcon,
  ClockIcon,
  UserGroupIcon,

} from '@heroicons/vue/24/outline';
import ProfileDropdown from '../components/ProfileDropdown.vue';
import Button from '../components/Button.vue';
import { useAuthStore } from '../stores/auth';
import { usePerfisStore } from '../stores/perfis';

const sidebarOpen = ref(false);
const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const perfisStore = usePerfisStore();


// Close sidebar on route change
watch(() => route.path, () => {
  sidebarOpen.value = false;
});
</script>