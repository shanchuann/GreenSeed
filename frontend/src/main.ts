import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import { useAuthStore } from '@/stores/auth'

async function bootstrap() {
  const app = createApp(App)
  app.use(createPinia())

  // 在挂载、路由初始化之前完成 token 验证，路由守卫可以保持同步
  await useAuthStore().restore()

  app.use(router)
  app.mount('#app')
}

bootstrap()
