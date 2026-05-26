<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Monitor, TrendingUp, Palette, Megaphone, BookOpen, Briefcase,
} from 'lucide-vue-next'
import api from '@/api'
import JobCard, { type Job } from '@/components/ui/JobCard.vue'

const router  = useRouter()
const keyword = ref('')
const city    = ref('')

function search() {
  router.push({ name: 'jobs', query: { q: keyword.value, city: city.value } })
}

const hotKeywords = ['产品经理', '前端开发', 'UI 设计', '数据分析', '运营']

const categories = [
  { label: '互联网·软件', icon: Monitor,    count: null as number | null },
  { label: '金融·投资',   icon: TrendingUp, count: null as number | null },
  { label: '设计·创意',   icon: Palette,    count: null as number | null },
  { label: '市场·运营',   icon: Megaphone,  count: null as number | null },
  { label: '教育·培训',   icon: BookOpen,   count: null as number | null },
  { label: '咨询·管理',   icon: Briefcase,  count: null as number | null },
]

const stats = [
  { value: '—', unit: '家', label: '入驻企业' },
  { value: '—', unit: '个', label: '在招职位' },
  { value: '—', unit: '+', label: '注册求职者' },
]

const featuredJobs = ref<Job[]>([])
const featuredLoading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('/jobs', { params: { limit: 6, sort_by: 'newest' } })
    featuredJobs.value = res.data
  } catch {
    // silently ignore — page still works without featured jobs
  } finally {
    featuredLoading.value = false
  }
})
</script>

<template>
  <!-- ── Hero ─────────────────────────────────────────────── -->
  <section class="hero">
    <div class="container hero__inner">
      <div class="hero__copy fade-up">
        <h1 class="hero__brand">
          <span class="hero__brand-text">青禾<em class="hero__brand-accent">招聘</em></span>
        </h1>
        <p class="hero__tagline">以青春为籽，启职场新章</p>
        <p class="hero__desc">专为本科生打造的求职平台，连接优质企业与充满活力的应届人才</p>

        <!-- Search bar -->
        <form class="hero__search" @submit.prevent="search" aria-label="职位搜索">
          <div class="hero__search-field">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              v-model="keyword"
              type="text"
              placeholder="搜索职位、公司或技能"
              aria-label="搜索关键词"
            />
          </div>
          <select v-model="city" aria-label="选择城市" class="hero__city">
            <option value="">全国</option>
            <option>北京</option>
            <option>上海</option>
            <option>杭州</option>
            <option>深圳</option>
            <option>广州</option>
            <option>成都</option>
            <option>武汉</option>
          </select>
          <button type="submit" class="btn btn--primary btn--lg hero__search-btn">找工作</button>
        </form>

        <!-- Hot keywords -->
        <div class="hero__hot">
          <span class="hero__hot-label">热门：</span>
          <button
            v-for="kw in hotKeywords"
            :key="kw"
            class="hero__hot-tag"
            @click="keyword = kw; search()"
          >{{ kw }}</button>
        </div>
      </div>

      <!-- Stats panel -->
      <div class="hero__stats fade-up" style="--delay: 100ms">
        <div v-for="s in stats" :key="s.label" class="hero__stat">
          <div class="hero__stat-value">
            {{ s.value }}<span class="hero__stat-unit">{{ s.unit }}</span>
          </div>
          <div class="hero__stat-label">{{ s.label }}</div>
        </div>
      </div>
    </div>

    <!-- Decorative botanical lines -->
    <div class="hero__deco" aria-hidden="true">
      <div class="hero__deco-line hero__deco-line--1"></div>
      <div class="hero__deco-line hero__deco-line--2"></div>
      <div class="hero__deco-line hero__deco-line--3"></div>
    </div>
  </section>

  <!-- ── Categories ─────────────────────────────────────── -->
  <section class="section section--alt">
    <div class="container">
      <header class="section__head">
        <h2 class="section__title">按行业浏览</h2>
        <RouterLink to="/jobs" class="section__more">查看全部 →</RouterLink>
      </header>

      <div class="categories">
        <RouterLink
          v-for="cat in categories"
          :key="cat.label"
          :to="`/jobs?category=${encodeURIComponent(cat.label)}`"
          class="category-card"
        >
          <span class="category-card__icon" aria-hidden="true"><component :is="cat.icon" :size="22" :stroke-width="1.5" /></span>
          <span class="category-card__label">{{ cat.label }}</span>
          <span class="category-card__count">{{ cat.count !== null ? `${cat.count} 个职位` : '浏览职位' }}</span>
        </RouterLink>
      </div>
    </div>
  </section>

  <!-- ── Featured Jobs ──────────────────────────────────── -->
  <section class="section">
    <div class="container">
      <header class="section__head">
        <h2 class="section__title">最新发布</h2>
        <RouterLink to="/jobs" class="section__more">查看全部 →</RouterLink>
      </header>

      <div v-if="featuredLoading" class="jobs-grid">
        <div v-for="n in 6" :key="n" class="skeleton-job-card"></div>
      </div>
      <div v-else class="jobs-grid">
        <JobCard
          v-for="job in featuredJobs"
          :key="job.id"
          :job="job"
          variant="grid"
        />
      </div>
    </div>
  </section>

  <!-- ── CTA Banner ─────────────────────────────────────── -->
  <section class="cta-section">
    <div class="container cta-section__inner">
      <div class="cta-section__copy">
        <h2 class="cta-section__title">准备好开始了吗？</h2>
        <p class="cta-section__desc">加入青禾招聘，与 12,000 位应届生一起探索职场新起点</p>
      </div>
      <div class="cta-section__actions">
        <RouterLink to="/register" class="btn btn--primary btn--lg">免费注册求职</RouterLink>
        <RouterLink to="/jobs" class="btn btn--ghost btn--lg">先看看职位</RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ── Hero ── */
.hero {
  position: relative;
  overflow: hidden;
  padding-block: var(--space-16) var(--space-20);
  background: var(--gs-bg);
}

.hero__inner {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: var(--space-12);
  align-items: center;
}

.hero__copy { max-width: 640px; }

.hero__brand {
  display: flex;
  align-items: baseline;
  margin-bottom: var(--space-4);
  font-family: var(--font-display);
  line-height: 0.9;
}

.hero__brand-text {
  font-size: var(--text-hero);
  font-weight: 800;
  font-style: normal;
  color: var(--gs-ink);
  letter-spacing: -0.04em;
}

.hero__brand-accent {
  color: var(--gs-primary);
  font-style: normal;
  font-weight: 800;
}

.hero__brand-main {
  font-size: var(--text-hero);
  font-weight: 800;
  font-style: normal;
  color: var(--gs-ink);
  letter-spacing: -0.04em;
}

.hero__brand-suffix {
  font-size: var(--text-hero);
  font-weight: 800;
  color: var(--gs-primary);
  letter-spacing: -0.04em;
}

.hero__tagline {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 500;
  color: var(--gs-text);
  margin-bottom: var(--space-3);
  letter-spacing: 0.01em;
}

.hero__desc {
  font-size: var(--text-base);
  color: var(--gs-text-2);
  line-height: 1.7;
  max-width: 52ch;
  margin-bottom: var(--space-8);
}

/* Search */
.hero__search {
  display: flex;
  gap: var(--space-2);
  background: var(--gs-surface);
  border: 1.5px solid var(--gs-border);
  border-radius: var(--radius-xl);
  padding: var(--space-2);
  margin-bottom: var(--space-4);
  transition: border-color var(--duration-fast);
}
.hero__search:focus-within { border-color: var(--gs-primary); }

.hero__search-field {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex: 1;
  padding-inline: var(--space-3);
  color: var(--gs-text-3);
}
.hero__search-field input {
  flex: 1;
  height: 40px;
  background: none;
  border: none;
  font-size: var(--text-base);
  color: var(--gs-text);
  outline: none;
}
.hero__search-field input::placeholder { color: var(--gs-text-3); }

.hero__city {
  height: 40px;
  padding-inline: var(--space-3);
  background: none;
  border: none;
  border-left: 1px solid var(--gs-border);
  font-size: var(--text-sm);
  color: var(--gs-text-2);
  outline: none;
  cursor: pointer;
}

.hero__search-btn {
  height: 44px;
  flex-shrink: 0;
  border-radius: var(--radius-lg);
}

/* Hot keywords */
.hero__hot {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-2);
}
.hero__hot-label {
  font-size: var(--text-sm);
  color: var(--gs-text-3);
}
.hero__hot-tag {
  height: 28px;
  padding-inline: var(--space-3);
  font-size: var(--text-sm);
  color: var(--gs-text-2);
  background: var(--gs-surface-2);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: background var(--duration-fast), color var(--duration-fast), border-color var(--duration-fast);
}
.hero__hot-tag:hover {
  background: var(--gs-primary-tint);
  color: var(--gs-primary);
  border-color: var(--gs-primary);
}

/* Stats */
.hero__stats {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  padding: var(--space-8);
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-xl);
  min-width: 180px;
  animation-delay: var(--delay, 0ms);
}

.hero__stat-value {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: 800;
  color: var(--gs-ink);
  line-height: 1;
  letter-spacing: -0.03em;
}
.hero__stat-unit {
  font-size: var(--text-lg);
  font-weight: 400;
  color: var(--gs-primary);
  margin-left: 2px;
}
.hero__stat-label {
  font-size: var(--text-sm);
  color: var(--gs-text-3);
  margin-top: var(--space-1);
}

/* Decorative lines */
.hero__deco {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}
.hero__deco-line {
  position: absolute;
  background: var(--gs-primary);
  opacity: 0.06;
  border-radius: var(--radius-full);
}
.hero__deco-line--1 {
  width: 1px; height: 60%;
  right: 20%; top: -10%;
}
.hero__deco-line--2 {
  width: 1px; height: 40%;
  right: 25%; bottom: 5%;
}
.hero__deco-line--3 {
  height: 1px; width: 30%;
  right: 10%; top: 35%;
}

/* ── Section layout ── */
.section {
  padding-block: var(--space-16);
}
.section--alt {
  background: var(--gs-surface);
}
.section__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: var(--space-8);
}
.section__title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--gs-text);
  letter-spacing: -0.02em;
}
.section__more {
  font-size: var(--text-sm);
  color: var(--gs-primary);
  font-weight: 500;
  transition: opacity var(--duration-fast);
}
.section__more:hover { opacity: 0.75; }

/* ── Categories ── */
.categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--space-3);
}

.category-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-5);
  background: var(--gs-bg);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: inherit;
  transition: border-color var(--duration-fast), box-shadow var(--duration-fast), transform var(--duration-fast);
}
.category-card:hover {
  border-color: var(--gs-primary);
  box-shadow: var(--shadow-sm);
  transform: translateY(-2px);
}

.category-card__icon {
  display: flex;
  align-items: center;
  color: var(--gs-primary);
}
.category-card__label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--gs-text);
}
.category-card__count {
  font-size: var(--text-xs);
  color: var(--gs-text-3);
}

/* ── Jobs grid ── */
.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-4);
}

.skeleton-job-card {
  height: 140px;
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-lg);
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }

/* ── CTA banner ── */
.cta-section {
  background: var(--gs-ink);
  padding-block: var(--space-16);
}

.cta-section__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-8);
  flex-wrap: wrap;
}

.cta-section__title {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: 800;
  color: var(--gs-accent);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-2);
}
.cta-section__desc {
  font-size: var(--text-base);
  color: oklch(70% 0.020 100);
  max-width: 44ch;
}
.cta-section__actions {
  display: flex;
  gap: var(--space-3);
  flex-shrink: 0;
}
.cta-section .btn--ghost { color: oklch(70% 0.020 100); }
.cta-section .btn--ghost:hover { background: oklch(30% 0.040 147); color: oklch(90% 0.020 100); }

/* ── Responsive ── */
@media (max-width: 768px) {
  .hero__inner {
    grid-template-columns: 1fr;
  }
  .hero__stats {
    flex-direction: row;
    justify-content: space-around;
    min-width: unset;
  }
  .hero__search {
    flex-wrap: wrap;
  }
  .hero__city { border-left: none; border-top: 1px solid var(--gs-border); }
  .hero__search-btn { width: 100%; margin-top: var(--space-1); }
  .cta-section__inner { flex-direction: column; text-align: center; }
  .cta-section__desc { max-width: unset; }
  .cta-section__actions { justify-content: center; }
}
</style>
