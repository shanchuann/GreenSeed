<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Sprout } from 'lucide-vue-next'
import api from '@/api'
import JobCard, { type Job } from '@/components/ui/JobCard.vue'
import GsSelect, { type SelectOption } from '@/components/ui/GsSelect.vue'
import { cityOptions } from '@/constants/cities'

const route  = useRoute()
const router = useRouter()

const keyword  = ref((route.query.q    as string) ?? '')
const city     = ref((route.query.city as string) ?? '')
const jobType  = ref((route.query.type as string) ?? '')
const sortBy   = ref((route.query.sort as string) ?? 'newest')
const loading     = ref(false)
const loadingMore = ref(false)
const jobs        = ref<Job[]>([])
const hasMore     = ref(false)
const PAGE        = 20

const typeOptions: SelectOption[] = [
  { value: '',       label: '全部类型' },
  { value: 'full',   label: '全职' },
  { value: 'part',   label: '兼职' },
  { value: 'intern', label: '实习' },
]

const sortOptions: SelectOption[] = [
  { value: 'newest', label: '最新发布' },
  { value: 'salary', label: '薪资最高' },
]


function buildParams(offset = 0) {
  return {
    q:        keyword.value  || undefined,
    city:     city.value     || undefined,
    job_type: jobType.value  || undefined,
    sort_by:  sortBy.value,
    limit:    PAGE + 1,
    offset,
  }
}

async function fetchJobs() {
  loading.value = true
  try {
    const res = await api.get('/jobs', { params: buildParams(0) })
    const data: Job[] = res.data
    hasMore.value = data.length > PAGE
    jobs.value = data.slice(0, PAGE)
  } catch {
    jobs.value = []
    hasMore.value = false
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  loadingMore.value = true
  try {
    const res = await api.get('/jobs', { params: buildParams(jobs.value.length) })
    const data: Job[] = res.data
    hasMore.value = data.length > PAGE
    jobs.value.push(...data.slice(0, PAGE))
  } finally {
    loadingMore.value = false
  }
}

let searchTimer: ReturnType<typeof setTimeout>
function scheduleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchJobs, 300)
}

watch(keyword, scheduleSearch)
watch([city, jobType, sortBy], () => {
  router.replace({
    query: {
      ...(keyword.value  && { q:    keyword.value }),
      ...(city.value     && { city: city.value }),
      ...(jobType.value  && { type: jobType.value }),
      ...(sortBy.value !== 'newest' && { sort: sortBy.value }),
    },
  })
  fetchJobs()
})

onMounted(fetchJobs)
</script>

<template>
  <div class="jobs-page">
    <!-- Toolbar -->
    <div class="jobs-toolbar">
      <div class="container jobs-toolbar__inner">
        <div class="search-bar">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            v-model="keyword"
            type="text"
            class="search-bar__input"
            placeholder="职位、公司或关键词"
            aria-label="搜索"
          />
        </div>

        <GsSelect v-model="city"    :options="cityOptions" aria-label="城市" />
        <GsSelect v-model="jobType" :options="typeOptions" aria-label="职位类型" />

        <div class="sort-group">
          <span class="sort-group__label">排序</span>
          <button
            v-for="opt in sortOptions"
            :key="opt.value"
            class="sort-btn"
            :class="{ 'sort-btn--active': sortBy === opt.value }"
            @click="sortBy = opt.value"
          >{{ opt.label }}</button>
        </div>
      </div>
    </div>

    <!-- Results -->
    <div class="container jobs-content">
      <div class="jobs-meta">
        <span v-if="!loading">
          共 <strong>{{ jobs.length }}</strong> 个职位
          <template v-if="keyword"> · "{{ keyword }}"</template>
        </span>
      </div>

      <div v-if="loading" class="jobs-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-card"></div>
      </div>

      <div v-else-if="jobs.length === 0" class="jobs-empty">
        <div class="jobs-empty__icon" aria-hidden="true">
          <Sprout :size="48" :stroke-width="1.2" />
        </div>
        <h3 class="jobs-empty__title">暂无符合条件的职位</h3>
        <p class="jobs-empty__desc">试试调整搜索条件，或&nbsp;<button class="link-btn" @click="keyword = ''; city = ''; jobType = ''">清除筛选</button></p>
      </div>

      <ul v-else class="jobs-list" role="list">
        <li v-for="job in jobs" :key="job.id">
          <JobCard :job="job" variant="list" />
        </li>
      </ul>

      <div v-if="hasMore && !loading" class="load-more">
        <button class="load-more__btn" :disabled="loadingMore" @click="loadMore">
          <span v-if="loadingMore" class="load-more__spinner" aria-hidden="true"></span>
          {{ loadingMore ? '加载中…' : '加载更多职位' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.jobs-page { min-height: 60vh; }

/* ── Toolbar ── */
.jobs-toolbar {
  position: sticky;
  top: 60px;
  z-index: 50;
  background: var(--gs-overlay);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--gs-border);
  padding-block: var(--space-3);
}

.jobs-toolbar__inner {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex: 1;
  min-width: 200px;
  height: 38px;
  padding-inline: var(--space-4);
  background: var(--gs-surface);
  border: 1.5px solid var(--gs-border);
  border-radius: var(--radius-md);
  color: var(--gs-text-3);
  transition: border-color var(--duration-fast);
}
.search-bar:focus-within {
  border-color: var(--gs-primary);
  color: var(--gs-text);
}
.search-bar__input {
  flex: 1;
  background: none;
  border: none;
  font-size: var(--text-sm);
  color: var(--gs-text);
  outline: none;
}
.search-bar__input::placeholder { color: var(--gs-text-3); }


.sort-group {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  margin-left: auto;
}
.sort-group__label {
  font-size: var(--text-sm);
  color: var(--gs-text-3);
  margin-right: var(--space-1);
}
.sort-btn {
  height: 30px;
  padding-inline: var(--space-3);
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--gs-text-2);
  background: none;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast);
}
.sort-btn:hover        { background: var(--gs-surface-2); color: var(--gs-text); }
.sort-btn--active      { background: var(--gs-primary-tint); color: var(--gs-primary); border-color: var(--gs-primary); }

/* ── Content ── */
.jobs-content { padding-block: var(--space-6); }

.jobs-meta {
  font-size: var(--text-sm);
  color: var(--gs-text-3);
  margin-bottom: var(--space-5);
}
.jobs-meta strong { color: var(--gs-text); font-weight: 600; }

/* ── List ── */
.jobs-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* ── Empty ── */
.jobs-empty {
  text-align: center;
  padding-block: var(--space-20);
  color: var(--gs-text-3);
}
.jobs-empty__icon { display: flex; justify-content: center; margin-bottom: var(--space-4); color: var(--gs-primary); opacity: 0.5; }
.jobs-empty__title { font-size: var(--text-xl); font-weight: 600; color: var(--gs-text-2); margin-bottom: var(--space-2); }
.jobs-empty__desc { font-size: var(--text-base); }

.link-btn {
  background: none;
  border: none;
  color: var(--gs-primary);
  font-size: inherit;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}

/* ── Skeleton ── */
.skeleton-card {
  height: 90px;
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-lg);
  animation: pulse 1.4s ease-in-out infinite;
  margin-bottom: var(--space-3);
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.5; }
}

/* ── Load more ── */
.load-more {
  display: flex;
  justify-content: center;
  padding-top: var(--space-6);
}

.load-more__btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  height: 40px;
  padding-inline: var(--space-6);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--gs-text-2);
  background: var(--gs-surface);
  border: 1.5px solid var(--gs-border);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: border-color var(--duration-fast), color var(--duration-fast);
}
.load-more__btn:hover:not(:disabled) {
  border-color: var(--gs-primary);
  color: var(--gs-primary);
}
.load-more__btn:disabled { opacity: 0.6; cursor: default; }

.load-more__spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--gs-border);
  border-top-color: var(--gs-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
