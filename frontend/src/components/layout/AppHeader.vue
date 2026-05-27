<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth   = useAuthStore()

const menuOpen = ref(false)

const theme = ref(document.documentElement.getAttribute('data-theme') ?? 'light')

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  document.documentElement.setAttribute('data-theme', theme.value)
  localStorage.setItem('gs-theme', theme.value)
}

function logout() {
  auth.logout()
  router.push({ name: 'home' })
}

const userInitial = computed(() =>
  auth.user?.name ? auth.user.name[0].toUpperCase() : '?'
)
</script>

<template>
  <header class="header">
    <div class="container header__inner">
      <!-- Logo -->
      <RouterLink to="/" class="logo" aria-label="青禾招聘 首页">
        <span class="logo__text">青禾<span class="logo__accent">招聘</span></span>
      </RouterLink>

      <!-- Desktop nav -->
      <nav class="nav" aria-label="主导航">
        <RouterLink to="/jobs" class="nav__link">找工作</RouterLink>
        <RouterLink v-if="auth.isRecruiter || auth.isAdmin" to="/recruiter" class="nav__link">招聘管理</RouterLink>
        <RouterLink v-if="auth.isAdmin" to="/admin" class="nav__link">控制台</RouterLink>
      </nav>

      <!-- Right actions -->
      <div class="header__actions">
        <!-- Theme toggle -->
        <button
          class="theme-btn"
          :aria-label="theme === 'dark' ? '切换浅色模式' : '切换深色模式'"
          @click="toggleTheme"
        >
          <svg v-if="theme === 'dark'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
          </svg>
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
          </svg>
        </button>

        <template v-if="!auth.isLoggedIn">
          <RouterLink to="/login"    class="btn btn--ghost btn--sm">登录</RouterLink>
          <RouterLink to="/register" class="btn btn--primary btn--sm">免费注册</RouterLink>
        </template>

        <template v-else>
          <RouterLink v-if="auth.isRecruiter" to="/recruiter/post" class="btn btn--outline btn--sm">
            发布职位
          </RouterLink>
          <div class="avatar-menu">
            <button class="avatar" @click="menuOpen = !menuOpen" :aria-expanded="menuOpen">
              <img v-if="auth.user?.avatar_url" :src="auth.user.avatar_url" :alt="auth.user.name" />
              <span v-else>{{ userInitial }}</span>
            </button>
            <Transition name="drop">
              <div v-if="menuOpen" class="dropdown" @click="menuOpen = false">
                <div class="dropdown__header">
                  <span class="dropdown__name">{{ auth.user?.name }}</span>
                  <span class="dropdown__email">{{ auth.user?.email }}</span>
                </div>
                <RouterLink to="/profile"      class="dropdown__item">个人资料</RouterLink>
                <RouterLink to="/resume"       class="dropdown__item" v-if="auth.isSeeker">在线简历</RouterLink>
                <RouterLink to="/applications" class="dropdown__item" v-if="auth.isSeeker">我的申请</RouterLink>
                <button class="dropdown__item dropdown__item--danger" @click="logout">退出登录</button>
              </div>
            </Transition>
          </div>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--gs-overlay);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--gs-border);
  transition: background var(--duration-slow) var(--ease-out);
}

.header__inner {
  display: flex;
  align-items: center;
  gap: var(--space-6);
  height: 60px;
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  font-family: var(--font-display);
  text-decoration: none;
  flex-shrink: 0;
}
.logo__text {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--gs-ink);
  letter-spacing: -0.03em;
  line-height: 1;
  transition: color var(--duration-fast);
}
.logo__accent {
  color: var(--gs-primary);
  font-weight: 800;
}
.logo:hover .logo__text { color: var(--gs-primary); }
.logo:hover .logo__accent { color: var(--gs-primary); }

/* Nav */
.nav {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex: 1;
}

.nav__link {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--gs-text-2);
  border-radius: var(--radius-md);
  transition: color var(--duration-fast), background var(--duration-fast);
}
.nav__link:hover,
.nav__link.router-link-active {
  color: var(--gs-text);
  background: var(--gs-surface);
}

/* Actions */
.header__actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-left: auto;
}

.theme-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: none;
  border: none;
  color: var(--gs-text-2);
  border-radius: var(--radius-md);
  transition: color var(--duration-fast), background var(--duration-fast);
}
.theme-btn:hover {
  color: var(--gs-text);
  background: var(--gs-surface);
}

/* Avatar + dropdown */
.avatar-menu { position: relative; }

.avatar {
  width: 34px;
  height: 34px;
  border-radius: var(--radius-full);
  background: var(--gs-primary-tint);
  color: var(--gs-primary);
  font-size: var(--text-sm);
  font-weight: 700;
  border: 2px solid var(--gs-border);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  cursor: pointer;
  transition: border-color var(--duration-fast);
}
.avatar:hover { border-color: var(--gs-primary); }
.avatar img  { width: 100%; height: 100%; object-fit: cover; }

.dropdown {
  position: absolute;
  top: calc(100% + var(--space-2));
  right: 0;
  width: 200px;
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  z-index: 200;
}

.dropdown__header {
  padding: var(--space-4);
  border-bottom: 1px solid var(--gs-border);
}
.dropdown__name  { display: block; font-size: var(--text-sm); font-weight: 600; color: var(--gs-text); }
.dropdown__email { display: block; font-size: var(--text-xs); color: var(--gs-text-3); margin-top: 2px; }

.dropdown__item {
  display: block;
  width: 100%;
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  color: var(--gs-text-2);
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background var(--duration-fast), color var(--duration-fast);
}
.dropdown__item:hover        { background: var(--gs-surface-2); color: var(--gs-text); }
.dropdown__item--danger:hover { color: var(--gs-error); }

/* Dropdown animation */
.drop-enter-active, .drop-leave-active {
  transition: opacity var(--duration-fast) var(--ease-out),
              transform var(--duration-fast) var(--ease-out);
}
.drop-enter-from, .drop-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.97);
}
</style>
