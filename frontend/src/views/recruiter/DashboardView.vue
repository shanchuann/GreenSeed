<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router   = useRouter()
const loading  = ref(true)
const companies = ref<any[]>([])
const jobs      = ref<any[]>([])
const recentApps = ref<any[]>([])

onMounted(async () => {
  try {
    const [cRes, jRes] = await Promise.all([
      api.get('/companies/mine'),
      api.get('/jobs', { params: { limit: 100 } }),
    ])
    companies.value = cRes.data
    // Filter jobs belonging to recruiter's companies
    const myCompanyIds = new Set(companies.value.map((c: any) => c.id))
    jobs.value = jRes.data.filter((j: any) => myCompanyIds.has(j.company_id))
  } finally {
    loading.value = false
  }
})

const openJobs   = computed(() => jobs.value.filter(j => j.status === 'open').length)
const closedJobs = computed(() => jobs.value.filter(j => j.status === 'closed').length)
</script>

<template>
  <div class="page-wrap">
    <div class="container">
      <div class="page-head fade-up">
        <h1 class="page-title">招聘管理</h1>
        <RouterLink to="/recruiter/post" class="btn btn--primary">+ 发布职位</RouterLink>
      </div>

      <!-- Stats row -->
      <div class="stats-row fade-up">
        <div class="stat-card">
          <div class="stat-card__value">{{ companies.length }}</div>
          <div class="stat-card__label">旗下公司</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">{{ openJobs }}</div>
          <div class="stat-card__label">在招职位</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">{{ closedJobs }}</div>
          <div class="stat-card__label">已关闭</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">{{ jobs.length }}</div>
          <div class="stat-card__label">全部职位</div>
        </div>
      </div>

      <!-- Companies -->
      <section class="section">
        <div class="section-head">
          <h2 class="section-title">我的公司</h2>
          <RouterLink to="/recruiter/company/create" class="section-link">+ 创建公司</RouterLink>
        </div>

        <div v-if="loading" class="skeleton-grid">
          <div v-for="n in 3" :key="n" class="skeleton-card" style="height:100px"></div>
        </div>
        <div v-else-if="companies.length === 0" class="empty-hint">
          还没有公司主页，<RouterLink to="/recruiter/company/create" class="link-primary">立即创建</RouterLink>
        </div>
        <div v-else class="company-grid">
          <div v-for="c in companies" :key="c.id" class="company-card">
            <div class="company-card__logo">{{ c.name.slice(0, 2) }}</div>
            <div class="company-card__info">
              <p class="company-card__name">{{ c.name }}</p>
              <p class="company-card__meta">{{ c.industry ?? '—' }} · {{ c.location ?? '—' }}</p>
            </div>
            <span :class="['tag', c.verified ? 'tag--green' : 'tag--muted']" style="flex-shrink:0">
              {{ c.verified ? '已认证' : '待认证' }}
            </span>
          </div>
        </div>
      </section>

      <!-- Jobs -->
      <section class="section">
        <div class="section-head">
          <h2 class="section-title">发布的职位</h2>
          <RouterLink to="/recruiter/post" class="section-link">+ 发布</RouterLink>
        </div>

        <div v-if="loading" class="apps-list">
          <div v-for="n in 4" :key="n" class="skeleton-card" style="height:72px"></div>
        </div>
        <div v-else-if="jobs.length === 0" class="empty-hint">还没有发布过职位</div>
        <ul v-else class="jobs-list" role="list">
          <li v-for="j in jobs" :key="j.id" class="job-row">
            <RouterLink :to="`/jobs/${j.id}`" class="job-row__title">{{ j.title }}</RouterLink>
            <span class="job-row__company">{{ j.company?.name }}</span>
            <span :class="['tag', j.status === 'open' ? 'tag--green' : 'tag--muted']">
              {{ j.status === 'open' ? '在招' : '关闭' }}
            </span>
            <RouterLink :to="`/recruiter/applications/${j.id}`" class="btn btn--ghost btn--sm">查看申请</RouterLink>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<style scoped>
.page-wrap { padding-block: var(--space-10); }
.page-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-8); }
.page-title { font-family: var(--font-display); font-size: var(--text-3xl); font-weight: 800; color: var(--gs-text); letter-spacing: -0.02em; }

.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-4); margin-bottom: var(--space-10); }
.stat-card { padding: var(--space-6); background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-lg); text-align: center; }
.stat-card__value { font-family: var(--font-display); font-size: var(--text-3xl); font-weight: 800; color: var(--gs-ink); }
.stat-card__label { font-size: var(--text-sm); color: var(--gs-text-3); margin-top: var(--space-1); }

.section { margin-bottom: var(--space-10); }
.section-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: var(--space-5); }
.section-title { font-family: var(--font-display); font-size: var(--text-xl); font-weight: 700; color: var(--gs-text); }
.section-link { font-size: var(--text-sm); color: var(--gs-primary); font-weight: 500; }

.company-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: var(--space-4); }
.company-card { display: flex; align-items: center; gap: var(--space-4); padding: var(--space-5); background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-lg); }
.company-card__logo { width: 44px; height: 44px; flex-shrink: 0; border-radius: var(--radius-md); background: var(--gs-primary-tint); display: flex; align-items: center; justify-content: center; font-family: var(--font-display); font-weight: 700; font-size: var(--text-sm); color: var(--gs-primary); }
.company-card__name { font-weight: 600; color: var(--gs-text); margin-bottom: 2px; }
.company-card__meta { font-size: var(--text-xs); color: var(--gs-text-3); }

.jobs-list { list-style: none; display: flex; flex-direction: column; gap: var(--space-2); }
.job-row { display: flex; align-items: center; gap: var(--space-4); padding: var(--space-4); background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-lg); flex-wrap: wrap; }
.job-row__title { font-weight: 600; color: var(--gs-text); flex: 1; min-width: 120px; }
.job-row__title:hover { color: var(--gs-primary); }
.job-row__company { font-size: var(--text-sm); color: var(--gs-text-2); }

.empty-hint { font-size: var(--text-sm); color: var(--gs-text-3); padding: var(--space-6) 0; }
.link-primary { color: var(--gs-primary); }
.skeleton-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: var(--space-4); }
.skeleton-card { background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-lg); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
@media (max-width: 768px) { .stats-row { grid-template-columns: 1fr 1fr; } }
</style>
