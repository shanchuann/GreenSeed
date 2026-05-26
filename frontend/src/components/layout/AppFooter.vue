<template>
  <footer class="footer">
    <div class="container footer__inner">
      <div class="footer__brand">
        <span class="footer__logo">青禾招聘</span>
        <p class="footer__slogan">以青春为籽，启职场新章</p>
      </div>
      <div class="footer__links">
        <RouterLink to="/jobs">浏览职位</RouterLink>
        <RouterLink to="/register">注册加入</RouterLink>
      </div>
      <p class="footer__copy">© {{ year }} GreenSeed · 山川不念旧</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
const year = new Date().getFullYear()
</script>

<style scoped>
.footer {
  border-top: 1px solid var(--gs-border);
  background: var(--gs-surface);
  padding-block: var(--space-8);
  margin-top: auto;
}

.footer__inner {
  display: flex;
  align-items: center;
  gap: var(--space-8);
  flex-wrap: wrap;
}

.footer__brand { flex: 1; min-width: 160px; }

.footer__logo {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--gs-ink);
  letter-spacing: -0.02em;
}

.footer__slogan {
  font-size: var(--text-sm);
  color: var(--gs-text-3);
  margin-top: var(--space-1);
}

.footer__links {
  display: flex;
  gap: var(--space-6);
}

.footer__links a {
  font-size: var(--text-sm);
  color: var(--gs-text-2);
  transition: color var(--duration-fast);
}
.footer__links a:hover { color: var(--gs-primary); }

.footer__copy {
  width: 100%;
  font-size: var(--text-xs);
  color: var(--gs-text-3);
  margin-top: var(--space-4);
}

@media (min-width: 640px) {
  .footer__copy { width: auto; margin-top: 0; margin-left: auto; }
}
</style>
