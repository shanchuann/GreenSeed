<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const restored = ref(false)

onMounted(async () => {
  const saved = localStorage.getItem('gs-theme')
  if (saved) document.documentElement.setAttribute('data-theme', saved)
  await auth.restore()
  restored.value = true
})
</script>

<template>
  <div class="app-shell">
    <AppHeader />
    <main class="app-main">
      <RouterView v-if="restored" v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
      <div v-else class="app-loading" aria-label="加载中">
        <span class="app-loading__dot"></span>
        <span class="app-loading__dot"></span>
        <span class="app-loading__dot"></span>
      </div>
    </main>
    <AppFooter />
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

.app-main {
  flex: 1;
}

.app-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding-block: 120px;
}

.app-loading__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--gs-primary);
  opacity: 0.3;
  animation: dot-pulse 1.2s ease-in-out infinite;
}
.app-loading__dot:nth-child(2) { animation-delay: 0.2s; }
.app-loading__dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes dot-pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40%           { opacity: 1;   transform: scale(1.1); }
}
</style>

<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 180ms var(--ease-out), transform 180ms var(--ease-out);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
