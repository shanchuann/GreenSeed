<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api'
import GsSelect, { type SelectOption } from '@/components/ui/GsSelect.vue'

const router  = useRouter()
const route   = useRoute()
const jobId   = route.params.id as string | undefined
const isEdit  = computed(() => !!jobId)

const loading = ref(false)
const error   = ref('')
const companies = ref<any[]>([])

const form = reactive({
  company_id:   '',
  title:        '',
  description:  '',
  requirements: '',
  salary_min:   undefined as number | undefined,
  salary_max:   undefined as number | undefined,
  job_type:     'full' as 'full' | 'part' | 'intern',
  location:     '',
  category:     '',
  tags:         [] as string[],
})

const tagInput = ref('')

onMounted(async () => {
  const res = await api.get('/companies/mine')
  companies.value = res.data
  if (isEdit.value) {
    const jRes = await api.get(`/jobs/${jobId}`)
    const j = jRes.data
    form.company_id   = j.company_id
    form.title        = j.title
    form.description  = j.description  ?? ''
    form.requirements = j.requirements ?? ''
    form.salary_min   = j.salary_min   ?? undefined
    form.salary_max   = j.salary_max   ?? undefined
    form.job_type     = j.job_type
    form.location     = j.location     ?? ''
    form.category     = j.category     ?? ''
    form.tags         = [...(j.tags    ?? [])]
  } else if (companies.value.length > 0) {
    form.company_id = companies.value[0].id
  }
})

function addTag() {
  const t = tagInput.value.trim()
  if (t && !form.tags.includes(t)) form.tags.push(t)
  tagInput.value = ''
}
function removeTag(i: number) { form.tags.splice(i, 1) }

async function submit() {
  if (!form.company_id) { error.value = '请先创建公司'; return }
  if (!form.title || !form.description) { error.value = '标题和描述不能为空'; return }
  error.value = ''
  loading.value = true
  try {
    if (isEdit.value) {
      await api.patch(`/jobs/${jobId}`, form)
      router.push('/recruiter')
    } else {
      const res = await api.post('/jobs', form)
      router.push(`/jobs/${res.data.id}`)
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? (isEdit.value ? '保存失败，请重试' : '发布失败，请重试')
  } finally {
    loading.value = false
  }
}

const categories = ['互联网·软件', '金融·投资', '设计·创意', '市场·运营', '教育·培训', '咨询·管理', '其他']

const companyOptions = computed<SelectOption[]>(() =>
  companies.value.map(c => ({ value: c.id, label: c.name }))
)
const jobTypeOptions: SelectOption[] = [
  { value: 'full',   label: '全职' },
  { value: 'part',   label: '兼职' },
  { value: 'intern', label: '实习' },
]
const categoryOptions: SelectOption[] = [
  { value: '', label: '请选择' },
  ...categories.map(c => ({ value: c, label: c })),
]
</script>

<template>
  <div class="page-wrap">
    <div class="container container--narrow">
      <h1 class="page-title fade-up">{{ isEdit ? '编辑职位' : '发布职位' }}</h1>

      <div v-if="companies.length === 0 && !loading" class="no-company-hint fade-up">
        <p>发布职位前需要先创建公司主页</p>
        <RouterLink to="/recruiter" class="btn btn--primary" style="margin-top:var(--space-4)">去创建公司</RouterLink>
      </div>

      <form v-else @submit.prevent="submit" class="post-form fade-up">
        <!-- Company -->
        <div class="form-section">
          <h2 class="form-section__title">基本信息</h2>
          <div class="field">
            <label class="field__label">所属公司</label>
            <GsSelect v-model="form.company_id" :options="companyOptions" placeholder="选择公司" />
          </div>
          <div class="field">
            <label class="field__label">职位名称 <span class="required">*</span></label>
            <input v-model="form.title" class="input" placeholder="如：产品经理（实习）" required />
          </div>
          <div class="field-row">
            <div class="field">
              <label class="field__label">工作类型</label>
              <GsSelect v-model="form.job_type" :options="jobTypeOptions" />
            </div>
            <div class="field">
              <label class="field__label">工作城市</label>
              <input v-model="form.location" class="input" placeholder="如：北京" />
            </div>
            <div class="field">
              <label class="field__label">行业分类</label>
              <GsSelect v-model="form.category" :options="categoryOptions" />
            </div>
          </div>
        </div>

        <!-- Salary -->
        <div class="form-section">
          <h2 class="form-section__title">薪资范围</h2>
          <div class="field-row">
            <div class="field">
              <label class="field__label">最低月薪（元）</label>
              <input v-model.number="form.salary_min" class="input" type="number" min="0" placeholder="如：5000" />
            </div>
            <div class="field">
              <label class="field__label">最高月薪（元）</label>
              <input v-model.number="form.salary_max" class="input" type="number" min="0" placeholder="如：10000" />
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="form-section">
          <h2 class="form-section__title">职位详情</h2>
          <div class="field">
            <label class="field__label">职位描述 <span class="required">*</span></label>
            <textarea v-model="form.description" class="input" style="height:140px;resize:vertical;padding-block:var(--space-3)" placeholder="工作内容、职责等" required></textarea>
          </div>
          <div class="field">
            <label class="field__label">任职要求</label>
            <textarea v-model="form.requirements" class="input" style="height:100px;resize:vertical;padding-block:var(--space-3)" placeholder="学历、技能要求等"></textarea>
          </div>
        </div>

        <!-- Tags -->
        <div class="form-section">
          <h2 class="form-section__title">技能标签</h2>
          <div class="field">
            <div class="skill-tags">
              <span v-for="(t, i) in form.tags" :key="t" class="tag tag--green skill-tag">
                {{ t }}
                <button type="button" class="skill-tag__remove" @click="removeTag(i)">×</button>
              </span>
            </div>
            <div class="skill-input-row">
              <input v-model="tagInput" class="input" placeholder="输入标签后按 Enter（如 Vue3、Python）" @keydown.enter.prevent="addTag" />
              <button type="button" class="btn btn--outline btn--sm" @click="addTag">添加</button>
            </div>
          </div>
        </div>

        <Transition name="error">
          <p v-if="error" class="form-error" role="alert">{{ error }}</p>
        </Transition>

        <div class="form-actions">
          <RouterLink to="/recruiter" class="btn btn--ghost">取消</RouterLink>
          <button type="submit" class="btn btn--primary btn--lg" :disabled="loading">
            {{ loading ? (isEdit ? '保存中…' : '发布中…') : (isEdit ? '保存修改' : '发布职位') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.page-wrap { padding-block: var(--space-10); }
.page-title { font-family: var(--font-display); font-size: var(--text-3xl); font-weight: 800; color: var(--gs-text); letter-spacing: -0.02em; margin-bottom: var(--space-8); }
.post-form { display: flex; flex-direction: column; gap: var(--space-6); }
.form-section { background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-xl); padding: var(--space-6); display: flex; flex-direction: column; gap: var(--space-4); }
.form-section__title { font-family: var(--font-display); font-size: var(--text-lg); font-weight: 700; color: var(--gs-text); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field__label { font-size: var(--text-sm); font-weight: 500; color: var(--gs-text-2); }
.required { color: var(--gs-error); }
.field-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4); }
.skill-tags { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-2); min-height: 28px; }
.skill-tag { gap: var(--space-1); }
.skill-tag__remove { background: none; border: none; color: inherit; cursor: pointer; font-size: 1rem; padding: 0 2px; }
.skill-input-row { display: flex; gap: var(--space-2); }
.skill-input-row .input { flex: 1; height: 36px; }
.form-error { font-size: var(--text-sm); color: var(--gs-error); padding: var(--space-3) var(--space-4); background: oklch(from var(--gs-error) l c h / 0.08); border-radius: var(--radius-md); }
.form-actions { display: flex; justify-content: flex-end; gap: var(--space-3); }
.no-company-hint { text-align: center; padding: var(--space-12); background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-xl); color: var(--gs-text-2); }
.error-enter-active,.error-leave-active{transition:opacity .15s,transform .15s}.error-enter-from,.error-leave-to{opacity:0;transform:translateY(-4px)}
@media (max-width: 640px) { .field-row { grid-template-columns: 1fr; } }
</style>
