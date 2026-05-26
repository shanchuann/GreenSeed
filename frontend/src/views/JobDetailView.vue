<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CheckCircle } from 'lucide-vue-next'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import type { Job } from '@/components/ui/JobCard.vue'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()

const job         = ref<Job | null>(null)
const loading     = ref(true)
const notFound    = ref(false)
const applying    = ref(false)
const coverLetter = ref('')
const showForm    = ref(false)
const submitted   = ref(false)
const applyError  = ref('')

const companyName = computed(() =>
  job.value?.company?.name ?? job.value?.company_name ?? '未知公司'
)
const companyInitials = computed(() => companyName.value.slice(0, 2))

const salary = computed(() => {
  if (!job.value) return ''
  const { salary_min: min, salary_max: max } = job.value
  if (!min && !max) return '薪资面议'
  if (min && max)   return `¥${min / 1000}k–${max / 1000}k`
  if (min)          return `¥${min / 1000}k 起`
  return `¥${max! / 1000}k 以内`
})

const typeLabel: Record<string, string> = {
  full: '全职', part: '兼职', intern: '实习',
}

onMounted(async () => {
  try {
    const res = await api.get(`/jobs/${route.params.id}`)
    job.value = res.data
  } catch (e: any) {
    if (e?.response?.status === 404) notFound.value = true
  } finally {
    loading.value = false
  }
})

async function apply() {
  if (!auth.isLoggedIn) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  applying.value  = true
  applyError.value = ''
  try {
    await api.post('/applications', {
      job_id:       route.params.id,
      cover_letter: coverLetter.value,
    })
    submitted.value = true
    showForm.value  = false
  } catch (e: any) {
    applyError.value = e?.response?.data?.detail ?? '申请失败，请稍后重试'
  } finally {
    applying.value = false
  }
}
</script>

<template>
  <div class="detail-page">
    <!-- Loading -->
    <div v-if="loading" class="container detail-inner">
      <div class="skeleton-main">
        <div class="skeleton-block" style="height: 56px; width: 56px; border-radius: var(--radius-lg)"></div>
        <div style="flex:1">
          <div class="skeleton-block" style="height: 32px; width: 60%; margin-bottom: var(--space-3)"></div>
          <div class="skeleton-block" style="height: 16px; width: 40%"></div>
        </div>
      </div>
    </div>

    <!-- Not found -->
    <div v-else-if="notFound" class="container not-found">
      <h2>职位不存在或已下架</h2>
      <RouterLink to="/jobs" class="btn btn--ghost" style="margin-top: var(--space-4)">返回职位列表</RouterLink>
    </div>

    <!-- Detail -->
    <div v-else-if="job" class="container detail-inner">
      <!-- Main -->
      <article class="detail-main fade-up">
        <header class="detail-header">
          <div class="detail-company-logo">
            <img v-if="job.company?.logo_url" :src="job.company.logo_url" :alt="companyName" />
            <span v-else>{{ companyInitials }}</span>
          </div>
          <div>
            <h1 class="detail-title">{{ job.title }}</h1>
            <div class="detail-meta">
              <span>{{ companyName }}</span>
              <span class="dot">·</span>
              <span>{{ job.location }}</span>
              <span class="dot">·</span>
              <span class="detail-salary">{{ salary }}</span>
            </div>
            <div class="detail-tags">
              <span class="tag tag--muted">{{ typeLabel[job.job_type] ?? job.job_type }}</span>
              <span class="tag tag--green" v-for="t in job.tags" :key="t">{{ t }}</span>
            </div>
          </div>
        </header>

        <hr class="divider" />

        <section v-if="job.description" class="detail-section">
          <h2 class="detail-section__title">职位描述</h2>
          <p class="detail-section__body">{{ job.description }}</p>
        </section>

        <section v-if="job.requirements" class="detail-section">
          <h2 class="detail-section__title">任职要求</h2>
          <p class="detail-section__body">{{ job.requirements }}</p>
        </section>
      </article>

      <!-- Sidebar -->
      <aside class="detail-aside">
        <div class="detail-apply-card">
          <div class="detail-apply-salary">{{ salary }}</div>
          <div class="detail-apply-type tag tag--muted" style="margin-bottom: var(--space-5)">
            {{ typeLabel[job.job_type] ?? job.job_type }}
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

              <p v-if="applyError" class="apply-error">{{ applyError }}</p>

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
            <CheckCircle :size="32" :stroke-width="1.5" class="apply-success__icon" />
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
  overflow: hidden;
}
.detail-company-logo img { width: 100%; height: 100%; object-fit: cover; }

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
  white-space: pre-wrap;
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

.apply-error {
  font-size: var(--text-sm);
  color: var(--gs-error);
  margin-top: var(--space-2);
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
.apply-success__icon { color: var(--gs-success); }

/* Skeleton */
.skeleton-main { display: flex; gap: var(--space-5); padding-top: var(--space-6); }
.skeleton-block {
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-md);
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }

.not-found {
  padding-block: var(--space-20);
  text-align: center;
  color: var(--gs-text-2);
}

.divider { border: none; border-top: 1px solid var(--gs-border); margin-block: var(--space-6); }

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
