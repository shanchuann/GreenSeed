<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { GraduationCap, Building2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { parseApiError } from '@/utils/error'

const router = useRouter()
const auth   = useAuthStore()

const form = reactive({
  name:     '',
  email:    '',
  password: '',
  role:     '' as 'seeker' | 'recruiter' | '',
})
const error     = ref('')
const loading   = ref(false)
const needEmail = ref(false)

async function submit() {
  if (!form.role) { error.value = '请选择注册身份'; return }
  error.value   = ''
  loading.value = true
  try {
    await auth.register({
      name:     form.name,
      email:    form.email,
      password: form.password,
      role:     form.role,
    })
    if (auth.token) {
      router.push('/')
    } else {
      // email confirmation required
      needEmail.value = true
    }
  } catch (e: any) {
    error.value = parseApiError(e, '注册失败，请检查信息后重试')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <!-- Email confirmation notice -->
    <div v-if="needEmail" class="auth-card fade-up" style="text-align:center">
      <div class="auth-card__header">
        <RouterLink to="/" class="auth-logo">
          <span class="auth-logo__text">青禾<em class="auth-logo__accent">招聘</em></span>
        </RouterLink>
        <h1 class="auth-card__title">验证邮箱</h1>
        <p class="auth-card__subtitle" style="margin-top: var(--space-3)">
          我们已向 <strong>{{ form.email }}</strong> 发送了验证邮件，<br>请点击邮件中的链接完成注册。
        </p>
      </div>
      <RouterLink to="/login" class="btn btn--primary" style="margin-top: var(--space-6); width: 100%">前往登录</RouterLink>
    </div>

    <div v-else class="auth-card fade-up">
      <div class="auth-card__header">
        <RouterLink to="/" class="auth-logo">
          <span class="auth-logo__text">青禾<em class="auth-logo__accent">招聘</em></span>
        </RouterLink>
        <h1 class="auth-card__title">创建账号</h1>
        <p class="auth-card__subtitle">加入青禾，开启你的职场新篇章</p>
      </div>

      <!-- Role selection -->
      <div class="role-picker" role="group" aria-label="选择身份">
        <button
          type="button"
          class="role-card"
          :class="{ 'role-card--active': form.role === 'seeker' }"
          @click="form.role = 'seeker'"
        >
          <GraduationCap :size="24" :stroke-width="1.5" class="role-card__icon" aria-hidden="true" />
          <span class="role-card__name">我是求职者</span>
          <span class="role-card__desc">浏览职位，投递简历</span>
        </button>
        <button
          type="button"
          class="role-card"
          :class="{ 'role-card--active': form.role === 'recruiter' }"
          @click="form.role = 'recruiter'"
        >
          <Building2 :size="24" :stroke-width="1.5" class="role-card__icon" aria-hidden="true" />
          <span class="role-card__name">我是招聘方</span>
          <span class="role-card__desc">发布职位，寻找人才</span>
        </button>
      </div>

      <form @submit.prevent="submit" class="auth-form" novalidate>
        <div class="field">
          <label class="field__label" for="name">姓名</label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            class="input"
            placeholder="你的姓名"
            autocomplete="name"
            required
          />
        </div>

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
          <label class="field__label" for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="input"
            placeholder="至少 8 位"
            autocomplete="new-password"
            minlength="8"
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
          {{ loading ? '注册中…' : '注册' }}
        </button>
      </form>

      <p class="auth-card__footer">
        已有账号？
        <RouterLink to="/login" class="auth-link">立即登录</RouterLink>
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
  max-width: 440px;
  padding: var(--space-10);
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
}

.auth-card__header { text-align: center; margin-bottom: var(--space-6); }

.auth-logo {
  display: inline-flex;
  align-items: baseline;
  text-decoration: none;
  margin-bottom: var(--space-5);
}
.auth-logo__text {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--gs-ink);
  letter-spacing: -0.04em;
  font-style: normal;
}
.auth-logo__accent {
  color: var(--gs-primary);
  font-style: normal;
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

/* Role picker */
.role-picker {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.role-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-4) var(--space-3);
  background: var(--gs-bg);
  border: 2px solid var(--gs-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  text-align: center;
  transition: border-color var(--duration-fast), background var(--duration-fast);
}
.role-card:hover { border-color: var(--gs-border-strong); }
.role-card--active {
  border-color: var(--gs-primary);
  background: var(--gs-primary-tint);
}

.role-card__icon { color: var(--gs-text-2); }
.role-card__name { font-size: var(--text-sm); font-weight: 600; color: var(--gs-text); }
.role-card__desc { font-size: var(--text-xs); color: var(--gs-text-3); }
.role-card--active .role-card__name { color: var(--gs-primary); }
.role-card--active .role-card__icon { color: var(--gs-primary); }

/* Form */
.auth-form { display: flex; flex-direction: column; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field__label { font-size: var(--text-sm); font-weight: 500; color: var(--gs-text-2); }

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

.auth-submit { width: 100%; margin-top: var(--space-2); }
.auth-submit:disabled { opacity: 0.65; cursor: not-allowed; }

.auth-card__footer {
  text-align: center;
  font-size: var(--text-sm);
  color: var(--gs-text-3);
  margin-top: var(--space-6);
}
.auth-link { color: var(--gs-primary); font-weight: 500; }
.auth-link:hover { text-decoration: underline; }

.spin { animation: rotate 0.8s linear infinite; }
@keyframes rotate { to { transform: rotate(360deg); } }
</style>
