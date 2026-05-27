<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api'
import GsSelect, { type SelectOption } from '@/components/ui/GsSelect.vue'

const router    = useRouter()
const route     = useRoute()
const companyId = route.params.id as string | undefined
const isEdit    = computed(() => !!companyId)

const loading = ref(false)
const error   = ref('')

const form = reactive({
  name:        '',
  description: '',
  industry:    '',
  location:    '',
  website:     '',
})

const industries = ['互联网·软件', '金融·投资', '设计·创意', '市场·运营', '教育·培训', '咨询·管理', '制造·硬件', '医疗·健康', '其他']
const industryOptions: SelectOption[] = [
  { value: '', label: '请选择' },
  ...industries.map(i => ({ value: i, label: i })),
]

onMounted(async () => {
  if (!isEdit.value) return
  const res = await api.get(`/companies/${companyId}`)
  const c = res.data
  form.name        = c.name        ?? ''
  form.description = c.description ?? ''
  form.industry    = c.industry    ?? ''
  form.location    = c.location    ?? ''
  form.website     = c.website     ?? ''
})

async function submit() {
  if (!form.name.trim()) { error.value = '公司名称不能为空'; return }
  error.value  = ''
  loading.value = true
  try {
    if (isEdit.value) {
      await api.patch(`/companies/${companyId}`, form)
    } else {
      await api.post('/companies', form)
    }
    router.push('/recruiter')
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? (isEdit.value ? '保存失败，请重试' : '创建失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page-wrap">
    <div class="container container--narrow">
      <RouterLink to="/recruiter" class="back-link fade-up">← 返回招聘管理</RouterLink>
      <h1 class="page-title fade-up">{{ isEdit ? '编辑公司信息' : '创建公司主页' }}</h1>

      <form @submit.prevent="submit" class="create-form fade-up">
        <div class="form-section">
          <h2 class="form-section__title">基本信息</h2>
          <div class="field">
            <label class="field__label">公司名称 <span class="required">*</span></label>
            <input v-model="form.name" class="input" placeholder="如：青禾科技有限公司" required />
          </div>
          <div class="field-row">
            <div class="field">
              <label class="field__label">行业</label>
              <GsSelect v-model="form.industry" :options="industryOptions" placeholder="请选择" />
            </div>
            <div class="field">
              <label class="field__label">所在城市</label>
              <input v-model="form.location" class="input" placeholder="如：北京" />
            </div>
          </div>
          <div class="field">
            <label class="field__label">官网</label>
            <input v-model="form.website" class="input" placeholder="https://example.com" type="url" />
          </div>
        </div>

        <div class="form-section">
          <h2 class="form-section__title">公司介绍</h2>
          <div class="field">
            <label class="field__label">简介</label>
            <textarea v-model="form.description" class="input" style="height:140px;resize:vertical;padding-block:var(--space-3)" placeholder="介绍公司的业务、文化和规模…"></textarea>
          </div>
        </div>

        <Transition name="error">
          <p v-if="error" class="form-error" role="alert">{{ error }}</p>
        </Transition>

        <div class="form-actions">
          <RouterLink to="/recruiter" class="btn btn--ghost">取消</RouterLink>
          <button type="submit" class="btn btn--primary btn--lg" :disabled="loading">
            {{ loading ? (isEdit ? '保存中…' : '创建中…') : (isEdit ? '保存修改' : '创建公司') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.page-wrap { padding-block: var(--space-10); }
.back-link { font-size: var(--text-sm); color: var(--gs-primary); margin-bottom: var(--space-4); display: inline-block; }
.page-title { font-family: var(--font-display); font-size: var(--text-3xl); font-weight: 800; color: var(--gs-text); letter-spacing: -0.02em; margin-bottom: var(--space-8); }
.create-form { display: flex; flex-direction: column; gap: var(--space-6); }
.form-section { background: var(--gs-surface); border: 1px solid var(--gs-border); border-radius: var(--radius-xl); padding: var(--space-6); display: flex; flex-direction: column; gap: var(--space-4); }
.form-section__title { font-family: var(--font-display); font-size: var(--text-lg); font-weight: 700; color: var(--gs-text); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field__label { font-size: var(--text-sm); font-weight: 500; color: var(--gs-text-2); }
.required { color: var(--gs-error); }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.form-error { font-size: var(--text-sm); color: var(--gs-error); padding: var(--space-3) var(--space-4); background: oklch(from var(--gs-error) l c h / 0.08); border-radius: var(--radius-md); }
.form-actions { display: flex; justify-content: flex-end; gap: var(--space-3); }
.error-enter-active,.error-leave-active{transition:opacity .15s,transform .15s}.error-enter-from,.error-leave-to{opacity:0;transform:translateY(-4px)}
@media (max-width: 640px) { .field-row { grid-template-columns: 1fr; } }
</style>
