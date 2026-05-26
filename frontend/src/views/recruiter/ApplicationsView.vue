<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { MailOpen, ChevronDown } from 'lucide-vue-next'
import api from '@/api'

const route  = useRoute()
const jobId  = route.params.id as string

const job    = ref<any>(null)
const apps   = ref<any[]>([])
const loading = ref(true)
const filter  = ref('all')

onMounted(async () => {
  try {
    const [jRes, aRes] = await Promise.all([
      api.get(`/jobs/${jobId}`),
      api.get(`/applications/job/${jobId}`),
    ])
    job.value  = jRes.data
    apps.value = aRes.data
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

const statusOptions = ['pending', 'reviewing', 'accepted', 'rejected']

const openMenuId = ref<string | null>(null)
function toggleMenu(id: string) {
  openMenuId.value = openMenuId.value === id ? null : id
}
function closeMenus() { openMenuId.value = null }

const filtered = computed(() =>
  filter.value === 'all' ? apps.value : apps.value.filter(a => a.status === filter.value)
)

async function updateStatus(appId: string, status: string) {
  await api.patch(`/applications/${appId}/status`, { status })
  const app = apps.value.find(a => a.id === appId)
  if (app) app.status = status
  openMenuId.value = null
}

function relTime(iso: string) {
  const d = Math.floor((Date.now() - new Date(iso).getTime()) / 86400000)
  return d === 0 ? '今天' : d === 1 ? '昨天' : `${d}天前`
}
</script>

<template>
  <div class="page-wrap" @click="closeMenus">
    <div class="container">
      <div class="page-head fade-up">
        <div>
          <RouterLink to="/recruiter" class="back-link">← 返回招聘管理</RouterLink>
          <h1 class="page-title">
            {{ job ? job.title : '申请列表' }}
            <span v-if="job" class="job-company">· {{ job.company?.name }}</span>
          </h1>
        </div>
        <span class="apps-count">共 {{ apps.length }} 份申请</span>
      </div>

      <!-- Filter tabs -->
      <div class="filter-tabs fade-up">
        <button
          v-for="f in ['all', ...statusOptions]" :key="f"
          class="filter-tab" :class="{ 'filter-tab--active': filter === f }"
          @click="filter = f"
        >
          {{ f === 'all' ? '全部' : statusLabel[f] }}
          <span class="filter-tab__count">
            {{ f === 'all' ? apps.length : apps.filter(a => a.status === f).length }}
          </span>
        </button>
      </div>

      <!-- Skeleton -->
      <div v-if="loading" class="apps-list">
        <div v-for="n in 4" :key="n" class="skeleton-card" style="height:110px"></div>
      </div>

      <!-- Empty -->
      <div v-else-if="filtered.length === 0" class="empty-state">
        <div class="empty-state__icon"><MailOpen :size="48" :stroke-width="1.2" /></div>
        <h3>{{ filter === 'all' ? '暂无申请记录' : `没有「${statusLabel[filter]}」的申请` }}</h3>
      </div>

      <!-- List -->
      <ul v-else class="apps-list" role="list">
        <li v-for="app in filtered" :key="app.id" class="app-card">
          <div class="app-card__left">
            <div class="app-card__header">
              <span class="app-card__name">{{ app.seeker?.name ?? '匿名用户' }}</span>
              <span class="app-card__email">{{ app.seeker?.email }}</span>
            </div>
            <p v-if="app.cover_letter" class="app-card__letter">{{ app.cover_letter }}</p>
            <span class="app-card__time">投递于 {{ relTime(app.created_at) }}</span>
          </div>
          <div class="app-card__right">
            <div class="status-picker" :class="`status-picker--${app.status}`" @click.stop="toggleMenu(app.id)">
              <span class="status-picker__label">{{ statusLabel[app.status] }}</span>
              <ChevronDown :size="12" :stroke-width="2.5" class="status-picker__chevron" :class="{ 'status-picker__chevron--open': openMenuId === app.id }" />
              <Transition name="dropdown">
                <ul v-if="openMenuId === app.id" class="status-picker__menu" @click.stop>
                  <li
                    v-for="s in statusOptions" :key="s"
                    class="status-picker__option"
                    :class="[`status-option--${s}`, { 'status-picker__option--active': s === app.status }]"
                    @click="updateStatus(app.id, s)"
                  >{{ statusLabel[s] }}</li>
                </ul>
              </Transition>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.page-wrap { padding-block: var(--space-10); }
.back-link { font-size: var(--text-sm); color: var(--gs-primary); margin-bottom: var(--space-2); display: inline-block; }
.page-head { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-4); margin-bottom: var(--space-6); }
.page-title { font-family: var(--font-display); font-size: var(--text-2xl); font-weight: 800; color: var(--gs-text); letter-spacing: -0.02em; margin-top: var(--space-1); }
.job-company { font-weight: 400; color: var(--gs-text-2); font-size: var(--text-xl); }
.apps-count { font-size: var(--text-sm); color: var(--gs-text-3); white-space: nowrap; padding-top: var(--space-8); }

.filter-tabs { display: flex; gap: var(--space-2); flex-wrap: wrap; margin-bottom: var(--space-6); }
.filter-tab { display: flex; align-items: center; gap: var(--space-2); height: 32px; padding-inline: var(--space-4); font-size: var(--text-sm); font-weight: 500; color: var(--gs-text-2); background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-full); cursor: pointer; transition: all var(--duration-fast); }
.filter-tab:hover { border-color: var(--gs-border-strong); color: var(--gs-text); }
.filter-tab--active { background: var(--gs-primary-tint); color: var(--gs-primary); border-color: var(--gs-primary); }
.filter-tab__count { font-size: var(--text-xs); opacity: 0.7; }

.apps-list { list-style: none; display: flex; flex-direction: column; gap: var(--space-3); }
.app-card { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-6); padding: var(--space-5); background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-lg); }
.app-card__left { flex: 1; min-width: 0; }
.app-card__header { display: flex; align-items: baseline; gap: var(--space-3); margin-bottom: var(--space-2); }
.app-card__name { font-weight: 700; color: var(--gs-text); font-size: var(--text-md); }
.app-card__email { font-size: var(--text-sm); color: var(--gs-text-2); }
.app-card__letter { font-size: var(--text-sm); color: var(--gs-text-2); margin-bottom: var(--space-2); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.app-card__time { font-size: var(--text-xs); color: var(--gs-text-3); }
.app-card__right { flex-shrink: 0; }

.status-picker {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  border: 1px solid;
  white-space: nowrap;
}
.status-picker--pending   { background: oklch(95% 0.01 100); color: var(--gs-text-2); border-color: var(--gs-border); }
.status-picker--reviewing { background: oklch(93% 0.05 220); color: oklch(40% 0.12 230); border-color: oklch(80% 0.07 220); }
.status-picker--accepted  { background: var(--gs-primary-tint); color: var(--gs-primary); border-color: oklch(80% 0.08 144); }
.status-picker--rejected  { background: oklch(96% 0.03 25); color: var(--gs-error); border-color: oklch(85% 0.06 25); }

.status-picker__chevron { flex-shrink: 0; transition: transform var(--duration-fast) var(--ease-out); }
.status-picker__chevron--open { transform: rotate(180deg); }

.status-picker__menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  list-style: none;
  z-index: 200;
  padding: var(--space-1);
  min-width: 110px;
  overflow: hidden;
}
.status-picker__option {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  font-weight: 500;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--gs-text-2);
  transition: background var(--duration-fast), color var(--duration-fast);
}
.status-picker__option:hover { background: var(--gs-surface-2); color: var(--gs-text); }
.status-picker__option--active { font-weight: 700; }
.status-option--pending.status-picker__option--active   { color: var(--gs-text-2); }
.status-option--reviewing.status-picker__option--active { color: oklch(40% 0.12 230); }
.status-option--accepted.status-picker__option--active  { color: var(--gs-primary); }
.status-option--rejected.status-picker__option--active  { color: var(--gs-error); }

.dropdown-enter-active { transition: opacity var(--duration-fast) var(--ease-out), transform var(--duration-fast) var(--ease-out); }
.dropdown-leave-active { transition: opacity 80ms ease-in, transform 80ms ease-in; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-6px); }

.empty-state { text-align: center; padding-block: var(--space-20); }
.empty-state__icon { color: var(--gs-text-3); margin-bottom: var(--space-4); display: flex; justify-content: center; }
.empty-state h3 { font-size: var(--text-xl); color: var(--gs-text-2); }

.skeleton-card { background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-lg); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
</style>
