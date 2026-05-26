<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/api'

interface Application {
  id: string
  status: 'pending' | 'reviewing' | 'accepted' | 'rejected'
  created_at: string
  cover_letter?: string
  job: {
    id: string
    title: string
    location: string
    job_type: string
    salary_min?: number
    salary_max?: number
    company: { name: string }
  }
}

const apps    = ref<Application[]>([])
const loading = ref(true)
const filter  = ref<string>('all')

onMounted(async () => {
  try {
    const res = await api.get('/applications/mine')
    apps.value = res.data
  } finally {
    loading.value = false
  }
})

const statusLabel: Record<string, string> = {
  pending:   '待查看',
  reviewing: '审核中',
  accepted:  '已录用',
  rejected:  '未通过',
}

const statusClass: Record<string, string> = {
  pending:   'tag--muted',
  reviewing: 'tag--accent',
  accepted:  'tag--green',
  rejected:  'tag--error',
}

const filtered = computed(() =>
  filter.value === 'all' ? apps.value : apps.value.filter(a => a.status === filter.value)
)

function salary(a: Application) {
  const { salary_min: min, salary_max: max } = a.job
  if (!min && !max) return '薪资面议'
  if (min && max)   return `¥${min/1000}k–${max/1000}k`
  return min ? `¥${min/1000}k+` : `¥${max!/1000}k`
}

function relTime(iso: string) {
  const d = Math.floor((Date.now() - new Date(iso).getTime()) / 86400000)
  return d === 0 ? '今天' : d === 1 ? '昨天' : `${d}天前`
}
</script>

<template>
  <div class="page-wrap">
    <div class="container">
      <div class="page-head fade-up">
        <h1 class="page-title">我的申请</h1>
        <span class="apps-count">共 {{ apps.length }} 条</span>
      </div>

      <!-- Filter tabs -->
      <div class="filter-tabs fade-up">
        <button v-for="f in ['all','pending','reviewing','accepted','rejected']" :key="f"
          class="filter-tab" :class="{ 'filter-tab--active': filter === f }"
          @click="filter = f">
          {{ f === 'all' ? '全部' : statusLabel[f] }}
          <span class="filter-tab__count">
            {{ f === 'all' ? apps.length : apps.filter(a => a.status === f).length }}
          </span>
        </button>
      </div>

      <!-- Skeleton -->
      <div v-if="loading" class="apps-list">
        <div v-for="n in 4" :key="n" class="skeleton-card" style="height:90px"></div>
      </div>

      <!-- Empty -->
      <div v-else-if="filtered.length === 0" class="empty-state">
        <div class="empty-state__icon">📋</div>
        <h3>{{ filter === 'all' ? '还没有申请记录' : `没有「${statusLabel[filter]}」的申请` }}</h3>
        <RouterLink to="/jobs" class="btn btn--outline" style="margin-top:var(--space-4)">去投递职位</RouterLink>
      </div>

      <!-- List -->
      <ul v-else class="apps-list" role="list">
        <li v-for="app in filtered" :key="app.id" class="app-card">
          <div class="app-card__main">
            <div class="app-card__header">
              <RouterLink :to="`/jobs/${app.job.id}`" class="app-card__title">
                {{ app.job.title }}
              </RouterLink>
              <span :class="['tag', statusClass[app.status]]">{{ statusLabel[app.status] }}</span>
            </div>
            <div class="app-card__meta">
              <span>{{ app.job.company.name }}</span>
              <span class="dot">·</span>
              <span>{{ app.job.location }}</span>
              <span class="dot">·</span>
              <span class="salary">{{ salary(app) }}</span>
            </div>
          </div>
          <div class="app-card__time">{{ relTime(app.created_at) }}</div>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.page-wrap { padding-block: var(--space-10); }
.page-head { display: flex; align-items: baseline; gap: var(--space-4); margin-bottom: var(--space-6); }
.page-title { font-family: var(--font-display); font-size: var(--text-3xl); font-weight: 800; color: var(--gs-text); letter-spacing: -0.02em; }
.apps-count  { font-size: var(--text-sm); color: var(--gs-text-3); }

.filter-tabs {
  display: flex; gap: var(--space-2); flex-wrap: wrap;
  margin-bottom: var(--space-6);
}
.filter-tab {
  display: flex; align-items: center; gap: var(--space-2);
  height: 32px; padding-inline: var(--space-4);
  font-size: var(--text-sm); font-weight: 500;
  color: var(--gs-text-2); background: var(--gs-surface);
  border: 1px solid var(--gs-border); border-radius: var(--radius-full);
  cursor: pointer; transition: all var(--duration-fast);
}
.filter-tab:hover { border-color: var(--gs-border-strong); color: var(--gs-text); }
.filter-tab--active { background: var(--gs-primary-tint); color: var(--gs-primary); border-color: var(--gs-primary); }
.filter-tab__count { font-size: var(--text-xs); color: inherit; opacity: 0.7; }

.apps-list { list-style: none; display: flex; flex-direction: column; gap: var(--space-3); }

.app-card {
  display: flex; align-items: center; justify-content: space-between; gap: var(--space-4);
  padding: var(--space-5);
  background: var(--gs-surface); border: 1px solid var(--gs-border);
  border-radius: var(--radius-lg);
}
.app-card__header { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-2); flex-wrap: wrap; }
.app-card__title { font-size: var(--text-md); font-weight: 600; color: var(--gs-text); font-family: var(--font-display); }
.app-card__title:hover { color: var(--gs-primary); }
.app-card__meta { display: flex; align-items: center; gap: var(--space-2); font-size: var(--text-sm); color: var(--gs-text-2); flex-wrap: wrap; }
.dot { color: var(--gs-border-strong); }
.salary { color: var(--gs-primary); font-weight: 600; }
.app-card__time { font-size: var(--text-sm); color: var(--gs-text-3); white-space: nowrap; flex-shrink: 0; }
.tag--error { background: oklch(from var(--gs-error) l c h / 0.1); color: var(--gs-error); }

.empty-state { text-align: center; padding-block: var(--space-20); }
.empty-state__icon { font-size: 3rem; margin-bottom: var(--space-4); }
.empty-state h3 { font-size: var(--text-xl); color: var(--gs-text-2); }

.skeleton-card { background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-lg); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
</style>
