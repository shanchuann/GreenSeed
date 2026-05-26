<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Chart as ChartJS,
  ArcElement, CategoryScale, LinearScale,
  PointElement, LineElement, BarElement,
  Tooltip, Legend, Title, Filler,
} from 'chart.js'
import { Pie, Line, Bar } from 'vue-chartjs'
import api from '@/api'

ChartJS.register(
  ArcElement, CategoryScale, LinearScale,
  PointElement, LineElement, BarElement,
  Tooltip, Legend, Title, Filler,
)

const loading = ref(true)
const stats   = ref<any>(null)
const users   = ref<any[]>([])

onMounted(async () => {
  try {
    const [sRes, uRes] = await Promise.all([
      api.get('/admin/stats'),
      api.get('/admin/users'),
    ])
    stats.value = sRes.data
    users.value = uRes.data
  } finally {
    loading.value = false
  }
})

// ── Chart data ────────────────────────────────────────────────────

const pieData = computed(() => {
  if (!stats.value) return null
  const items: any[] = stats.value.jobs_by_category
  return {
    labels: items.map(i => i.category),
    datasets: [{
      data:            items.map(i => i.count),
      backgroundColor: [
        'oklch(52% 0.138 144)',
        'oklch(62% 0.12 168)',
        'oklch(72% 0.11 100)',
        'oklch(56% 0.13 240)',
        'oklch(66% 0.12 30)',
        'oklch(60% 0.10 280)',
      ],
      borderWidth: 0,
    }],
  }
})

const lineData = computed(() => {
  if (!stats.value) return null
  const items: any[] = stats.value.applications_by_day
  return {
    labels: items.map(i => i.date.slice(5)),  // MM-DD
    datasets: [{
      label:            '每日新增申请',
      data:             items.map(i => i.count),
      borderColor:      'oklch(52% 0.138 144)',
      backgroundColor:  'oklch(52% 0.138 144 / 0.1)',
      fill:             true,
      tension:          0.4,
      pointRadius:      4,
      pointBackgroundColor: 'oklch(52% 0.138 144)',
    }],
  }
})

const barData = computed(() => {
  if (!stats.value) return null
  const items: any[] = stats.value.jobs_by_company
  return {
    labels: items.map(i => i.company),
    datasets: [{
      label:           '职位数',
      data:            items.map(i => i.count),
      backgroundColor: 'oklch(52% 0.138 144)',
      borderRadius:    4,
    }],
  }
})

const chartOpts = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' as const } },
}

const lineOpts = {
  ...chartOpts,
  scales: {
    y: { beginAtZero: true, grid: { color: 'oklch(87% 0.02 128)' } },
    x: { grid: { display: false } },
  },
}

const barOpts = {
  ...chartOpts,
  indexAxis: 'y' as const,
  scales: {
    x: { beginAtZero: true },
    y: { grid: { display: false } },
  },
}

// ── User management ───────────────────────────────────────────────
const roleLabel: Record<string, string> = { seeker: '求职者', recruiter: '招聘方', admin: '管理员' }

async function changeRole(userId: string, newRole: string) {
  await api.patch(`/admin/users/${userId}/role`, null, { params: { role: newRole } })
  const user = users.value.find(u => u.id === userId)
  if (user) user.role = newRole
}

async function deleteUser(userId: string) {
  if (!confirm('确认删除该用户？此操作不可撤销')) return
  await api.delete(`/admin/users/${userId}`)
  users.value = users.value.filter(u => u.id !== userId)
}
</script>

<template>
  <div class="page-wrap">
    <div class="container">
      <h1 class="page-title fade-up">管理控制台</h1>

      <!-- Stat cards -->
      <div v-if="loading" class="stats-row">
        <div v-for="n in 4" :key="n" class="skeleton-card" style="height:90px"></div>
      </div>
      <div v-else-if="stats" class="stats-row fade-up">
        <div class="stat-card">
          <div class="stat-card__value">{{ stats.total_users }}</div>
          <div class="stat-card__label">注册用户</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">{{ stats.total_companies }}</div>
          <div class="stat-card__label">入驻企业</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">{{ stats.total_jobs }}</div>
          <div class="stat-card__label">发布职位</div>
        </div>
        <div class="stat-card">
          <div class="stat-card__value">{{ stats.total_applications }}</div>
          <div class="stat-card__label">投递申请</div>
        </div>
      </div>

      <!-- Charts -->
      <div v-if="!loading && stats" class="charts-grid fade-up">
        <div class="chart-card">
          <h3 class="chart-title">职位分类分布</h3>
          <div class="chart-body">
            <Pie v-if="pieData" :data="pieData" :options="chartOpts" />
          </div>
        </div>
        <div class="chart-card chart-card--wide">
          <h3 class="chart-title">近期每日新增申请</h3>
          <div class="chart-body">
            <Line v-if="lineData" :data="lineData" :options="lineOpts" />
          </div>
        </div>
        <div class="chart-card chart-card--full">
          <h3 class="chart-title">各公司发布职位数（Top 10）</h3>
          <div class="chart-body" style="height:280px">
            <Bar v-if="barData" :data="barData" :options="barOpts" />
          </div>
        </div>
      </div>

      <!-- User table -->
      <section class="section fade-up">
        <h2 class="section-title">用户管理</h2>
        <div class="table-wrap">
          <table class="user-table">
            <thead>
              <tr>
                <th>姓名</th>
                <th>邮箱</th>
                <th>角色</th>
                <th>注册时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td class="user-name">{{ u.name }}</td>
                <td class="user-email">{{ u.email }}</td>
                <td>
                  <select
                    :value="u.role"
                    class="role-select"
                    @change="changeRole(u.id, ($event.target as HTMLSelectElement).value)"
                  >
                    <option value="seeker">求职者</option>
                    <option value="recruiter">招聘方</option>
                    <option value="admin">管理员</option>
                  </select>
                </td>
                <td class="user-date">{{ u.created_at?.slice(0, 10) }}</td>
                <td>
                  <button class="btn btn--ghost btn--sm" style="color:var(--gs-error)" @click="deleteUser(u.id)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.page-wrap { padding-block: var(--space-10); }
.page-title { font-family: var(--font-display); font-size: var(--text-3xl); font-weight: 800; color: var(--gs-text); letter-spacing: -0.02em; margin-bottom: var(--space-8); }

.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-4); margin-bottom: var(--space-8); }
.stat-card { padding: var(--space-6); background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-lg); text-align: center; }
.stat-card__value { font-family: var(--font-display); font-size: var(--text-3xl); font-weight: 800; color: var(--gs-ink); }
.stat-card__label { font-size: var(--text-sm); color: var(--gs-text-3); margin-top: var(--space-1); }

/* Charts grid: pie (1 col) | line (2 col) | bar (full) */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--space-4);
  margin-bottom: var(--space-10);
}
.chart-card { background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-xl); padding: var(--space-6); }
.chart-card--full { grid-column: 1 / -1; }
.chart-title { font-family: var(--font-display); font-size: var(--text-lg); font-weight: 700; color: var(--gs-text); margin-bottom: var(--space-4); }
.chart-body { height: 240px; position: relative; }

/* User table */
.section { margin-bottom: var(--space-10); }
.section-title { font-family: var(--font-display); font-size: var(--text-2xl); font-weight: 700; color: var(--gs-text); margin-bottom: var(--space-5); }
.table-wrap { overflow-x: auto; border: 1px solid var(--gs-border); border-radius: var(--radius-lg); }
.user-table { width: 100%; border-collapse: collapse; }
.user-table th { padding: var(--space-3) var(--space-4); font-size: var(--text-sm); font-weight: 600; color: var(--gs-text-2); background: var(--gs-surface-2); text-align: left; border-bottom: 1px solid var(--gs-border); }
.user-table td { padding: var(--space-3) var(--space-4); font-size: var(--text-sm); color: var(--gs-text); border-bottom: 1px solid var(--gs-border); vertical-align: middle; }
.user-table tr:last-child td { border-bottom: none; }
.user-name { font-weight: 600; }
.user-email { color: var(--gs-text-2); }
.user-date  { color: var(--gs-text-3); }
.role-select { background: var(--gs-bg); border: 1px solid var(--gs-border); border-radius: var(--radius-sm); padding: 2px 6px; font-size: var(--text-sm); color: var(--gs-text); cursor: pointer; }

.skeleton-card { background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-lg); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
@media (max-width: 900px) { .stats-row { grid-template-columns: 1fr 1fr; } .charts-grid { grid-template-columns: 1fr; } .chart-card--wide,.chart-card--full { grid-column: auto; } }
</style>
