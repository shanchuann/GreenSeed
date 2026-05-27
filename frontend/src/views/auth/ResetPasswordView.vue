<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router  = useRouter()
const form    = reactive({ password: '', confirm: '' })
const token   = ref('')
const loading = ref(false)
const error   = ref('')
const success  = ref(false)

onMounted(() => {
  // Supabase puts the recovery token in the URL hash as access_token
  const hash = window.location.hash.slice(1)
  const params = new URLSearchParams(hash)
  const t = params.get('access_token')
  const type = params.get('type')
  if (!t || type !== 'recovery') {
    error.value = '链接无效或已过期，请重新申请'
    return
  }
  token.value = t
  // Clean the hash so tokens don't linger in history
  history.replaceState(null, '', window.location.pathname)
})

async function submit() {
  if (form.password !== form.confirm) {
    error.value = '两次输入的密码不一致'
    return
  }
  if (form.password.length < 8) {
    error.value = '密码至少 8 位'
    return
  }
  error.value   = ''
  loading.value = true
  try {
    await axios.post('/api/auth/reset-password', { password: form.password }, {
      headers: { Authorization: `Bearer ${token.value}` },
    })
    success.value = true
    setTimeout(() => router.push('/login'), 2000)
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? '重置失败，请重新申请'
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
          <span class="auth-logo__text">青禾<em class="auth-logo__accent">招聘</em></span>
        </RouterLink>
        <h1 class="auth-card__title">设置新密码</h1>
      </div>

      <div v-if="success" class="success-notice">
        <p>密码已重置，正在跳转到登录页…</p>
      </div>

      <div v-else-if="error && !token" class="auth-error" role="alert" style="margin-bottom:var(--space-4)">
        {{ error }}
        <br />
        <RouterLink to="/forgot-password" class="auth-link" style="margin-top:var(--space-3);display:inline-block">重新申请重置</RouterLink>
      </div>

      <form v-else @submit.prevent="submit" class="auth-form" novalidate>
        <div class="field">
          <label class="field__label" for="pwd">新密码</label>
          <input id="pwd" v-model="form.password" type="password" class="input" placeholder="至少 8 位" minlength="8" required />
        </div>
        <div class="field">
          <label class="field__label" for="cpwd">确认密码</label>
          <input id="cpwd" v-model="form.confirm" type="password" class="input" placeholder="再输一次" required />
        </div>
        <p v-if="error" class="auth-error" role="alert">{{ error }}</p>
        <button type="submit" class="btn btn--primary auth-submit" :disabled="loading || !token">
          {{ loading ? '重置中…' : '确认修改' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.auth-page { min-height: calc(100dvh - 60px); display: flex; align-items: center; justify-content: center; padding: var(--space-8) var(--space-4); background: var(--gs-bg); }
.auth-card { width: 100%; max-width: 420px; padding: var(--space-10); background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-xl); box-shadow: var(--shadow-md); }
.auth-card__header { text-align: center; margin-bottom: var(--space-6); }
.auth-logo { display: inline-flex; align-items: baseline; text-decoration: none; margin-bottom: var(--space-5); }
.auth-logo__text { font-family: var(--font-display); font-size: 1.5rem; font-weight: 800; color: var(--gs-ink); letter-spacing: -0.04em; font-style: normal; }
.auth-logo__accent { color: var(--gs-primary); font-style: normal; }
.auth-card__title { font-family: var(--font-display); font-size: var(--text-2xl); font-weight: 700; color: var(--gs-text); letter-spacing: -0.02em; }
.auth-form { display: flex; flex-direction: column; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field__label { font-size: var(--text-sm); font-weight: 500; color: var(--gs-text-2); }
.auth-error { font-size: var(--text-sm); color: var(--gs-error); padding: var(--space-3) var(--space-4); background: oklch(from var(--gs-error) l c h / 0.08); border-radius: var(--radius-md); }
.auth-link { color: var(--gs-primary); font-weight: 500; }
.auth-submit { width: 100%; margin-top: var(--space-2); }
.success-notice { text-align: center; color: var(--gs-primary); font-size: var(--text-base); padding: var(--space-6) 0; }
</style>
