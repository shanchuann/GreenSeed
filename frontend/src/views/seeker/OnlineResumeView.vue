<script setup lang="ts">
import ResumeEditor from '@/components/resume/ResumeEditor.vue'
</script>

<template>
  <div class="page-wrap">
    <div class="container">
      <h1 class="page-title fade-up">在线简历</h1>
      <ResumeEditor />
    </div>
  </div>
</template>

<style scoped>
.page-wrap { padding-block: var(--space-10); }
.page-title {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: 800;
  color: var(--gs-text);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-8);
}
</style>
