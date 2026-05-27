<script setup lang="ts">
import { ref, reactive } from 'vue'
import api from '@/api'

const form    = reactive({ email: '' })
const loading = ref(false)
const sent    = ref(false)
const error   = ref('')

async function submit() {
  error.value   = ''
  loading.value = true
  try {
    await api.post('/auth/forgot-password', { email: form.email })
    sent.value = true
  } catch {
    error.value = '请求失败，请稍后重试'
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
        <h1 class="auth-card__title">重置密码</h1>
        <p class="auth-card__subtitle">输入注册邮箱，我们将发送重置链接</p>
      </div>

      <div v-if="sent" class="sent-notice">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--gs-primary);margin-bottom:var(--space-3)">
          <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.82 12a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.73 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.1a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>
        </svg>
        <p>重置邮件已发送至 <strong>{{ form.email }}</strong>，请查收并点击邮件中的链接。</p>
        <RouterLink to="/login" class="btn btn--primary" style="margin-top:var(--space-6);width:100%">返回登录</RouterLink>
      </div>

      <form v-else @submit.prevent="submit" class="auth-form" novalidate>
        <div class="field">
          <label class="field__label" for="email">注册邮箱</label>
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
        <p v-if="error" class="auth-error" role="alert">{{ error }}</p>
        <button type="submit" class="btn btn--primary auth-submit" :disabled="loading">
          {{ loading ? '发送中…' : '发送重置邮件' }}
        </button>
      </form>

      <p class="auth-card__footer">
        <RouterLink to="/login" class="auth-link">← 返回登录</RouterLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: calc(100dvh - 60px);
  display: flex; align-items: center; justify-content: center;
  padding: var(--space-8) var(--space-4);
  background: var(--gs-bg);
}
.auth-card {
  width: 100%; max-width: 420px;
  padding: var(--space-10);
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
}
.auth-card__header { text-align: center; margin-bottom: var(--space-6); }
.auth-logo { display: inline-flex; align-items: baseline; text-decoration: none; margin-bottom: var(--space-5); }
.auth-logo__text { font-family: var(--font-display); font-size: 1.5rem; font-weight: 800; color: var(--gs-ink); letter-spacing: -0.04em; font-style: normal; }
.auth-logo__accent { color: var(--gs-primary); font-style: normal; }
.auth-card__title { font-family: var(--font-display); font-size: var(--text-2xl); font-weight: 700; color: var(--gs-text); letter-spacing: -0.02em; margin-bottom: var(--space-2); }
.auth-card__subtitle { font-size: var(--text-sm); color: var(--gs-text-3); }
.auth-form { display: flex; flex-direction: column; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field__label { font-size: var(--text-sm); font-weight: 500; color: var(--gs-text-2); }
.auth-error { font-size: var(--text-sm); color: var(--gs-error); padding: var(--space-3) var(--space-4); background: oklch(from var(--gs-error) l c h / 0.08); border-radius: var(--radius-md); }
.auth-submit { width: 100%; margin-top: var(--space-2); }
.auth-card__footer { text-align: center; font-size: var(--text-sm); color: var(--gs-text-3); margin-top: var(--space-6); }
.auth-link { color: var(--gs-primary); font-weight: 500; }
.sent-notice { text-align: center; color: var(--gs-text-2); font-size: var(--text-sm); line-height: 1.7; display: flex; flex-direction: column; align-items: center; }
</style>
