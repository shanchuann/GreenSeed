<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

export interface Job {
  id: string
  title: string
  company?: { name: string; logo_url?: string | null }
  company_name?: string   // fallback for local mock data
  company_logo?: string
  location?: string
  job_type: 'full' | 'part' | 'intern'
  salary_min?: number
  salary_max?: number
  tags?: string[]
  created_at: string
  status?: string
  description?: string
  requirements?: string
  category?: string
  source_platform?: string
  source_url?: string
}

const props = withDefaults(
  defineProps<{ job: Job; variant?: 'list' | 'grid' }>(),
  { variant: 'list' }
)

const typeLabel: Record<Job['job_type'], string> = {
  full:   '全职',
  part:   '兼职',
  intern: '实习',
}

const companyName = computed(() =>
  props.job.company?.name ?? props.job.company_name ?? '未知公司'
)
const companyLogo = computed(() =>
  props.job.company?.logo_url ?? props.job.company_logo
)

const salary = computed(() => {
  const { salary_min: min, salary_max: max } = props.job
  if (!min && !max) return '薪资面议'
  if (min && max)   return `¥${min / 1000}k–${max / 1000}k`
  if (min)          return `¥${min / 1000}k 起`
  return `¥${max! / 1000}k 以内`
})

function relativeTime(iso: string) {
  const diff = Date.now() - new Date(iso).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 30)  return `${days}天前`
  return `${Math.floor(days / 30)}个月前`
}

const initials = computed(() => companyName.value.slice(0, 2))

const platformLabel: Record<string, string> = {
  local:      '',
  boss:       'BOSS直聘',
  zhilian:    '智联招聘',
  lagou:      '拉勾',
  liepin:     '猎聘',
  '51job':    '前程无忧',
}

const isExternal = computed(() =>
  !!props.job.source_platform && props.job.source_platform !== 'local'
)
const platformName = computed(() =>
  platformLabel[props.job.source_platform ?? 'local'] ?? props.job.source_platform ?? ''
)
</script>

<template>
  <component
    :is="isExternal ? 'a' : RouterLink"
    v-bind="isExternal
      ? { href: job.source_url, target: '_blank', rel: 'noopener noreferrer' }
      : { to: `/jobs/${job.id}` }"
    class="job-card"
    :class="`job-card--${variant}`"
  >
    <div class="job-card__logo">
      <img v-if="companyLogo" :src="companyLogo" :alt="companyName" />
      <span v-else class="job-card__initials">{{ initials }}</span>
    </div>

    <div class="job-card__info">
      <div class="job-card__top">
        <h3 class="job-card__title">{{ job.title }}</h3>
        <span class="job-card__salary">{{ salary }}</span>
      </div>
      <div class="job-card__meta">
        <span>{{ companyName }}</span>
        <span class="job-card__dot" aria-hidden="true">·</span>
        <span>{{ job.location }}</span>
        <span class="job-card__dot" aria-hidden="true">·</span>
        <span>{{ relativeTime(job.created_at) }}</span>
      </div>
      <div class="job-card__tags">
        <span class="tag tag--muted">{{ typeLabel[job.job_type] }}</span>
        <span v-if="isExternal" class="tag tag--platform">{{ platformName }}</span>
        <span v-for="tag in (job.tags ?? []).slice(0, 3)" :key="tag" class="tag tag--green">{{ tag }}</span>
      </div>
    </div>

    <svg v-if="variant === 'list'" class="job-card__arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M5 12h14M12 5l7 7-7 7"/>
    </svg>
  </component>
</template>

<style scoped>
.job-card {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  padding: var(--space-5);
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: inherit;
  transition: border-color var(--duration-fast) var(--ease-out),
              background var(--duration-fast) var(--ease-out),
              box-shadow var(--duration-fast) var(--ease-out);
}
.job-card:hover {
  border-color: var(--gs-border-strong);
  background: var(--gs-bg);
  box-shadow: var(--shadow-sm);
}
.job-card--grid { flex-direction: column; }
.job-card--grid .job-card__top { flex-direction: column; align-items: flex-start; gap: var(--space-1); }
.job-card--grid .job-card__salary { font-size: var(--text-sm); }
.job-card--grid .job-card__arrow { display: none; }

.job-card__logo {
  width: 44px; height: 44px; flex-shrink: 0;
  border-radius: var(--radius-md); overflow: hidden;
  background: var(--gs-primary-tint);
  display: flex; align-items: center; justify-content: center;
  border: 1px solid var(--gs-border);
}
.job-card__logo img { width: 100%; height: 100%; object-fit: cover; }
.job-card__initials { font-family: var(--font-display); font-size: var(--text-sm); font-weight: 700; color: var(--gs-primary); }

.job-card__info { flex: 1; min-width: 0; }
.job-card__top { display: flex; align-items: baseline; justify-content: space-between; gap: var(--space-3); margin-bottom: var(--space-1); }
.job-card__title { font-size: var(--text-md); font-weight: 600; color: var(--gs-text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-family: var(--font-display); }
.job-card__salary { font-size: var(--text-base); font-weight: 600; color: var(--gs-primary); white-space: nowrap; flex-shrink: 0; }
.job-card__meta { display: flex; align-items: center; gap: var(--space-2); flex-wrap: wrap; font-size: var(--text-sm); color: var(--gs-text-2); margin-bottom: var(--space-3); }
.job-card__dot { color: var(--gs-border-strong); }
.job-card__tags { display: flex; flex-wrap: wrap; gap: var(--space-2); min-height: 22px; }

.tag--platform {
  background: oklch(96% 0.04 255);
  color: oklch(45% 0.14 255);
  border: 1px solid oklch(88% 0.06 255);
}
.job-card__arrow { flex-shrink: 0; color: var(--gs-text-3); margin-top: var(--space-2); transition: transform var(--duration-fast) var(--ease-out), color var(--duration-fast); }
.job-card:hover .job-card__arrow { color: var(--gs-primary); transform: translateX(3px); }
</style>
