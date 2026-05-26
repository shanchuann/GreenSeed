<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Check } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()
const saving = ref(false)
const saved  = ref(false)

const form = reactive({
  name:      '',
  phone:     '',
  bio:       '',
  education: '',
  skills:    [] as string[],
})

const skillInput = ref('')

onMounted(() => {
  if (auth.user) {
    form.name      = auth.user.name      ?? ''
    form.phone     = (auth.user as any).phone     ?? ''
    form.bio       = (auth.user as any).bio       ?? ''
    form.education = (auth.user as any).education ?? ''
    form.skills    = [...((auth.user as any).skills ?? [])]
  }
})

function addSkill() {
  const s = skillInput.value.trim()
  if (s && !form.skills.includes(s)) form.skills.push(s)
  skillInput.value = ''
}

function removeSkill(i: number) { form.skills.splice(i, 1) }

async function save() {
  saving.value = true
  saved.value  = false
  try {
    await api.patch('/auth/me', form)
    saved.value = true
    setTimeout(() => { saved.value = false }, 2000)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="page-wrap">
    <div class="container container--narrow">
      <h1 class="page-title fade-up">个人资料</h1>

      <div class="profile-card fade-up">
        <!-- Avatar -->
        <div class="avatar-section">
          <div class="profile-avatar">
            <span>{{ auth.user?.name?.[0]?.toUpperCase() ?? '?' }}</span>
          </div>
          <div>
            <p class="profile-name">{{ auth.user?.name }}</p>
            <span class="tag tag--green">{{ auth.user?.role === 'seeker' ? '求职者' : '招聘方' }}</span>
          </div>
        </div>

        <hr class="divider" style="margin-block: var(--space-6)" />

        <form @submit.prevent="save" class="profile-form">
          <div class="field-row">
            <div class="field">
              <label class="field__label">姓名</label>
              <input v-model="form.name" class="input" placeholder="你的姓名" />
            </div>
            <div class="field">
              <label class="field__label">手机号</label>
              <input v-model="form.phone" class="input" placeholder="138..." type="tel" />
            </div>
          </div>

          <div class="field">
            <label class="field__label">教育经历</label>
            <input v-model="form.education" class="input" placeholder="例：XX大学 计算机科学 2024届" />
          </div>

          <div class="field">
            <label class="field__label">个人简介</label>
            <textarea v-model="form.bio" class="input" style="height:100px;resize:vertical;padding-block:var(--space-3)" placeholder="简短介绍自己..."></textarea>
          </div>

          <div class="field">
            <label class="field__label">技能标签</label>
            <div class="skill-tags">
              <span v-for="(s, i) in form.skills" :key="s" class="tag tag--green skill-tag">
                {{ s }}
                <button type="button" class="skill-tag__remove" @click="removeSkill(i)">×</button>
              </span>
            </div>
            <div class="skill-input-row">
              <input v-model="skillInput" class="input" placeholder="输入技能后按 Enter" @keydown.enter.prevent="addSkill" />
              <button type="button" class="btn btn--outline btn--sm" @click="addSkill">添加</button>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn--primary" :disabled="saving">
              <Check v-if="saved" :size="16" style="margin-right:4px" />
              {{ saving ? '保存中…' : saved ? '已保存' : '保存修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-wrap { padding-block: var(--space-10); }
.page-title {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: 800;
  color: var(--gs-text);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-8);
}
.profile-card {
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  box-shadow: var(--shadow-sm);
}
.avatar-section {
  display: flex;
  align-items: center;
  gap: var(--space-5);
}
.profile-avatar {
  width: 64px; height: 64px;
  border-radius: var(--radius-full);
  background: var(--gs-primary-tint);
  border: 2px solid var(--gs-border);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display);
  font-size: var(--text-2xl); font-weight: 800;
  color: var(--gs-primary);
}
.profile-name { font-size: var(--text-xl); font-weight: 700; color: var(--gs-text); margin-bottom: var(--space-2); }
.profile-form { display: flex; flex-direction: column; gap: var(--space-5); }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field__label { font-size: var(--text-sm); font-weight: 500; color: var(--gs-text-2); }
.skill-tags { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-2); min-height: 28px; }
.skill-tag { gap: var(--space-1); }
.skill-tag__remove { background: none; border: none; color: inherit; cursor: pointer; font-size: 1rem; line-height: 1; padding: 0 2px; }
.skill-input-row { display: flex; gap: var(--space-2); }
.skill-input-row .input { flex: 1; height: 36px; }
.form-actions { display: flex; justify-content: flex-end; padding-top: var(--space-4); }

@media (max-width: 600px) { .field-row { grid-template-columns: 1fr; } }
</style>
