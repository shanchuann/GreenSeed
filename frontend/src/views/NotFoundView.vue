<template>
  <div class="notfound">
    <div class="notfound__inner">
      <div class="notfound__code" aria-hidden="true">404</div>
      <h1 class="notfound__title">找不到这个页面</h1>
      <p class="notfound__desc">你访问的地址不存在，可能已被移除或输入有误。</p>
      <div class="notfound__actions">
        <RouterLink to="/" class="btn btn--primary">回到首页</RouterLink>
        <RouterLink to="/jobs" class="btn btn--outline">浏览职位</RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.notfound {
  min-height: calc(100dvh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
}
.notfound__inner {
  text-align: center;
  max-width: 420px;
}
.notfound__code {
  font-family: var(--font-display);
  font-size: clamp(6rem, 18vw, 10rem);
  font-weight: 800;
  line-height: 1;
  color: var(--gs-primary);
  opacity: 0.18;
  letter-spacing: -0.06em;
  margin-bottom: var(--space-4);
  user-select: none;
}
.notfound__title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--gs-text);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-3);
}
.notfound__desc {
  font-size: var(--text-base);
  color: var(--gs-text-3);
  line-height: 1.6;
  margin-bottom: var(--space-8);
}
.notfound__actions {
  display: flex;
  gap: var(--space-3);
  justify-content: center;
  flex-wrap: wrap;
}
</style>
