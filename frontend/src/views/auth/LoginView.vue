<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()

const form = reactive({ email: '', password: '' })
const error   = ref('')
const loading = ref(false)

async function submit() {
  error.value   = ''
  loading.value = true
  try {
    await auth.login(form.email, form.password)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? '邮箱或密码错误，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card fade-up">
      <div class="auth-card__header">
        <RouterLink to="/" class="auth-logo">
          <span class="auth-logo__main">青禾</span>
          <span class="auth-logo__sub">招聘</span>
        </RouterLink>
        <h1 class="auth-card__title">欢迎回来</h1>
        <p class="auth-card__subtitle">登录你的账号，继续探索职位</p>
      </div>

      <form @submit.prevent="submit" class="auth-form" novalidate>
        <div class="field">
          <label class="field__label" for="email">邮箱</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="input"
            placeholder="your@email.com"
            autocomplete="email"
            required
          />
        </div>

        <div class="field">
          <div class="field__row">
            <label class="field__label" for="password">密码</label>
            <a href="#" class="field__link">忘记密码？</a>
          </div>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="input"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
        </div>

        <Transition name="error">
          <p v-if="error" class="auth-error" role="alert">{{ error }}</p>
        </Transition>

        <button type="submit" class="btn btn--primary auth-submit" :disabled="loading">
          <svg v-if="loading" class="spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4"/>
          </svg>
          {{ loading ? '登录中…' : '登录' }}
        </button>
      </form>

      <p class="auth-card__footer">
        还没有账号？
        <RouterLink to="/register" class="auth-link">免费注册</RouterLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: calc(100dvh - 60px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8) var(--space-4);
  background: var(--gs-bg);
}

.auth-card {
  width: 100%;
  max-width: 400px;
  padding: var(--space-10);
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
}

.auth-card__header { text-align: center; margin-bottom: var(--space-8); }

.auth-logo {
  display: inline-flex;
  align-items: baseline;
  gap: 3px;
  text-decoration: none;
  margin-bottom: var(--space-5);
}
.auth-logo__main {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--gs-ink);
  letter-spacing: -0.04em;
}
.auth-logo__sub {
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 400;
  color: var(--gs-primary);
  letter-spacing: 0.06em;
}

.auth-card__title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--gs-text);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-2);
}
.auth-card__subtitle {
  font-size: var(--text-sm);
  color: var(--gs-text-3);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field__row { display: flex; justify-content: space-between; align-items: center; }
.field__label { font-size: var(--text-sm); font-weight: 500; color: var(--gs-text-2); }
.field__link  { font-size: var(--text-sm); color: var(--gs-primary); transition: opacity var(--duration-fast); }
.field__link:hover { opacity: 0.75; }

.auth-error {
  font-size: var(--text-sm);
  color: var(--gs-error);
  padding: var(--space-3) var(--space-4);
  background: oklch(from var(--gs-error) l c h / 0.08);
  border-radius: var(--radius-md);
}
.error-enter-active, .error-leave-active {
  transition: opacity var(--duration-fast), transform var(--duration-fast);
}
.error-enter-from, .error-leave-to { opacity: 0; transform: translateY(-4px); }

.auth-submit {
  width: 100%;
  margin-top: var(--space-2);
}
.auth-submit:disabled { opacity: 0.65; cursor: not-allowed; }

.auth-card__footer {
  text-align: center;
  font-size: var(--text-sm);
  color: var(--gs-text-3);
  margin-top: var(--space-6);
}
.auth-link { color: var(--gs-primary); font-weight: 500; }
.auth-link:hover { text-decoration: underline; }

/* Spinner */
.spin { animation: rotate 0.8s linear infinite; }
@keyframes rotate { to { transform: rotate(360deg); } }
</style>
