<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { Job } from '@/components/ui/JobCard.vue'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()

const job = ref<(Job & { description?: string; requirements?: string }) | null>(null)
const applying = ref(false)
const coverLetter = ref('')
const showForm = ref(false)
const submitted = ref(false)

onMounted(() => {
  job.value = {
    id: route.params.id as string,
    title: '产品经理（实习）',
    company_name: '字节跳动',
    location: '北京',
    job_type: 'intern',
    salary_min: 4000,
    salary_max: 6000,
    tags: ['产品规划', 'B端', '数据驱动'],
    created_at: new Date(Date.now() - 86400000).toISOString(),
    description: '负责字节跳动某业务线的产品需求调研、文档编写、项目跟进，与开发、设计同学协同工作，深度参与产品从 0 到 1 的全流程。',
    requirements: '本科及以上在读/应届，有较强的逻辑思维和沟通能力，熟悉 Axure / Figma 工具，有实际项目经验优先。',
  }
})

async function apply() {
  if (!auth.isLoggedIn) { router.push({ name: 'login', query: { redirect: route.fullPath } }); return }
  applying.value = true
  await new Promise(r => setTimeout(r, 800))
  applying.value = false
  submitted.value = true
  showForm.value = false
}
</script>

<template>
  <div class="detail-page">
    <div class="container detail-inner" v-if="job">
      <!-- Main -->
      <article class="detail-main fade-up">
        <header class="detail-header">
          <div class="detail-company-logo">
            <span>{{ job.company_name.slice(0, 2) }}</span>
          </div>
          <div>
            <h1 class="detail-title">{{ job.title }}</h1>
            <div class="detail-meta">
              <span>{{ job.company_name }}</span>
              <span class="dot">·</span>
              <span>{{ job.location }}</span>
              <span class="dot">·</span>
              <span class="detail-salary">¥{{ job.salary_min!/1000 }}k–{{ job.salary_max!/1000 }}k</span>
            </div>
            <div class="detail-tags">
              <span class="tag tag--green" v-for="t in job.tags" :key="t">{{ t }}</span>
            </div>
          </div>
        </header>

        <hr class="divider" />

        <section class="detail-section">
          <h2 class="detail-section__title">职位描述</h2>
          <p class="detail-section__body">{{ job.description }}</p>
        </section>

        <section class="detail-section">
          <h2 class="detail-section__title">任职要求</h2>
          <p class="detail-section__body">{{ job.requirements }}</p>
        </section>
      </article>

      <!-- Sidebar -->
      <aside class="detail-aside">
        <div class="detail-apply-card">
          <div class="detail-apply-salary">¥{{ job.salary_min!/1000 }}k–{{ job.salary_max!/1000 }}k</div>
          <div class="detail-apply-type tag tag--muted" style="margin-bottom: var(--space-5)">
            {{ { full: '全职', part: '兼职', intern: '实习' }[job.job_type] }}
          </div>

          <template v-if="!submitted">
            <button
              v-if="!showForm"
              class="btn btn--primary"
              style="width: 100%"
              @click="showForm = true"
            >立即申请</button>

            <template v-else>
              <label class="field__label" style="font-size: var(--text-sm); color: var(--gs-text-2); margin-bottom: var(--space-2); display: block">求职信（可选）</label>
              <textarea
                v-model="coverLetter"
                class="input"
                style="height: 120px; resize: vertical; padding-block: var(--space-3)"
                placeholder="简单介绍一下你自己..."
              ></textarea>
              <button
                class="btn btn--primary"
                style="width: 100%; margin-top: var(--space-3)"
                :disabled="applying"
                @click="apply"
              >{{ applying ? '提交中…' : '确认申请' }}</button>
              <button class="btn btn--ghost" style="width: 100%; margin-top: var(--space-2)" @click="showForm = false">取消</button>
            </template>
          </template>

          <div v-else class="apply-success">
            <span>✅</span>
            <p>申请已提交，等待对方查看</p>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.detail-page { padding-block: var(--space-10); }

.detail-inner {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: var(--space-8);
  align-items: start;
}

.detail-header {
  display: flex;
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.detail-company-logo {
  width: 56px; height: 56px; flex-shrink: 0;
  background: var(--gs-primary-tint);
  border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display);
  font-weight: 700; font-size: var(--text-lg);
  color: var(--gs-primary);
  border: 1px solid var(--gs-border);
}

.detail-title {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--gs-text);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-2);
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-base);
  color: var(--gs-text-2);
  margin-bottom: var(--space-3);
}
.dot { color: var(--gs-border-strong); }
.detail-salary { color: var(--gs-primary); font-weight: 600; }
.detail-tags   { display: flex; flex-wrap: wrap; gap: var(--space-2); }

.detail-section { margin-top: var(--space-8); }
.detail-section__title {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--gs-text);
  margin-bottom: var(--space-4);
}
.detail-section__body {
  font-size: var(--text-base);
  color: var(--gs-text-2);
  line-height: 1.75;
  max-width: 65ch;
}

.detail-aside { position: sticky; top: 80px; }

.detail-apply-card {
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.detail-apply-salary {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--gs-primary);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-2);
}

.apply-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding-block: var(--space-4);
  text-align: center;
  font-size: var(--text-sm);
  color: var(--gs-success);
}

@media (max-width: 768px) {
  .detail-inner {
    grid-template-columns: 1fr;
  }
  .detail-aside {
    position: static;
    order: -1;
  }
}
</style>
