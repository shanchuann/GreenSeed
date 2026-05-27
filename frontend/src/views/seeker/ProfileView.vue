<script setup lang="ts">
import { ref, watch } from 'vue'
import { Check, Upload, FileText, ExternalLink, Camera } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import ResumeEditor from '@/components/resume/ResumeEditor.vue'

const auth = useAuthStore()
const activeTab = ref<'online-resume' | 'resume'>('online-resume')

// ── Avatar ────────────────────────────────────────────────────────
const avatarUploading = ref(false)
const avatarError     = ref('')

async function uploadAvatar(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  avatarError.value    = ''
  avatarUploading.value = true
  try {
    const form = new FormData()
    form.append('file', file)
    const res = await api.post('/auth/me/avatar', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    auth.user = res.data
  } catch (e: any) {
    avatarError.value = e?.response?.data?.detail ?? '上传失败，请重试'
  } finally {
    avatarUploading.value = false
    ;(e.target as HTMLInputElement).value = ''
  }
}

// ── Resume file ───────────────────────────────────────────────────
const resumeUrl   = ref('')
const resumeFile  = ref<File | null>(null)
const uploading   = ref(false)
const uploadError = ref('')
const saving      = ref(false)
const saved       = ref(false)

watch(() => auth.user, u => {
  if (u) resumeUrl.value = (u as any).resume_url ?? ''
}, { immediate: true })

function onFileChange(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) { resumeFile.value = f; uploadError.value = '' }
}

async function uploadResume() {
  if (!resumeFile.value) return
  uploading.value   = true
  uploadError.value = ''
  try {
    const form = new FormData()
    form.append('file', resumeFile.value)
    const res = await api.post('/auth/me/resume', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    resumeUrl.value  = res.data.resume_url ?? ''
    auth.user        = res.data
    resumeFile.value = null
  } catch (e: any) {
    uploadError.value = e?.response?.data?.detail ?? '上传失败，请重试'
  } finally {
    uploading.value = false
  }
}

async function saveResumeUrl() {
  saving.value = true
  saved.value  = false
  try {
    const res = await api.patch('/auth/me', { resume_url: resumeUrl.value })
    auth.user    = res.data
    saved.value  = true
    setTimeout(() => { saved.value = false }, 2200)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="page-wrap">
    <div class="container">

      <!-- ── Profile hero ───────────────────────────────────────── -->
      <div class="profile-hero fade-up">
        <div class="profile-hero__banner"></div>
        <div class="profile-hero__body">
          <div class="profile-avatar-wrap">
            <div class="profile-avatar" :class="{ 'profile-avatar--uploading': avatarUploading }">
              <img v-if="auth.user?.avatar_url" :src="auth.user.avatar_url" class="profile-avatar__img" alt="头像" />
              <span v-else>{{ auth.user?.name?.[0]?.toUpperCase() ?? '?' }}</span>
            </div>
            <label class="profile-avatar__camera" :title="avatarUploading ? '上传中…' : '修改头像'">
              <Camera :size="13" />
              <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" style="display:none" @change="uploadAvatar" :disabled="avatarUploading" />
            </label>
          </div>
          <div class="profile-hero__info">
            <h1 class="profile-name">{{ auth.user?.name ?? '—' }}</h1>
            <div class="profile-badges">
              <span class="tag tag--green">{{ auth.user?.role === 'seeker' ? '求职者' : '招聘方' }}</span>
            </div>
            <p v-if="avatarError" class="avatar-error">{{ avatarError }}</p>
          </div>
        </div>
      </div>

      <!-- ── Tab nav ───────────────────────────────────────────── -->
      <nav class="tab-nav fade-up" role="tablist">
        <button
          v-for="tab in [
            { key: 'online-resume', label: '在线简历' },
            { key: 'resume',        label: '我的简历' },
          ]"
          :key="tab.key"
          role="tab"
          :aria-selected="activeTab === tab.key"
          class="tab-nav__item"
          :class="{ 'tab-nav__item--active': activeTab === tab.key }"
          @click="activeTab = (tab.key as any)"
        >{{ tab.label }}</button>
      </nav>

      <!-- ── 在线简历 ───────────────────────────────────────────── -->
      <ResumeEditor v-if="activeTab === 'online-resume'" />

      <!-- ── 我的简历 ───────────────────────────────────────────── -->
      <div v-else-if="activeTab === 'resume'" class="resume-tab-content fade-up">
        <div class="profile-card">
          <div v-if="resumeUrl" class="resume-current">
            <FileText :size="20" color="var(--gs-primary)" />
            <span class="resume-current__name">当前简历</span>
            <a :href="resumeUrl" target="_blank" rel="noopener" class="btn btn--ghost btn--sm">
              <ExternalLink :size="13" style="margin-right:3px" />查看
            </a>
          </div>
          <div v-else class="resume-empty">
            <FileText :size="40" color="var(--gs-text-3)" />
            <p>尚未上传简历</p>
          </div>

          <hr class="divider" style="margin-block:var(--space-6)" />

          <div class="field">
            <label class="field__label">上传附件简历</label>
            <p class="field__hint">支持 PDF、DOC、DOCX 格式，建议 5MB 以内</p>
            <label class="upload-zone">
              <Upload :size="22" color="var(--gs-primary)" />
              <span v-if="resumeFile">{{ resumeFile.name }}</span>
              <span v-else>点击选择文件</span>
              <input type="file" accept=".pdf,.doc,.docx" style="display:none" @change="onFileChange" />
            </label>
            <p v-if="uploadError" class="field__error">{{ uploadError }}</p>
            <button
              v-if="resumeFile"
              type="button"
              class="btn btn--primary"
              style="margin-top:var(--space-3)"
              :disabled="uploading"
              @click="uploadResume"
            >{{ uploading ? '上传中…' : '确认上传' }}</button>
          </div>

          <hr class="divider" style="margin-block:var(--space-6)" />

          <div class="field">
            <label class="field__label">或填写在线简历链接</label>
            <p class="field__hint">可粘贴 Google Drive、OneDrive、超简历等平台的分享链接</p>
            <input v-model="resumeUrl" class="input" placeholder="https://…" />
          </div>

          <div class="form-actions">
            <button class="btn btn--primary" :disabled="saving" @click="saveResumeUrl">
              <Check v-if="saved" :size="16" style="margin-right:4px" />
              {{ saving ? '保存中…' : saved ? '已保存 ✓' : '保存链接' }}
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.page-wrap { padding-block: var(--space-10); }

/* ── Hero ── */
.profile-hero {
  border-radius: var(--radius-xl);
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  overflow: hidden;
  margin-bottom: var(--space-5);
  box-shadow: var(--shadow-sm);
}
.profile-hero__banner {
  height: 80px;
  background: linear-gradient(120deg, var(--gs-primary) 0%, oklch(62% 0.13 160) 100%);
}
.profile-hero__body {
  display: flex;
  align-items: flex-end;
  gap: var(--space-5);
  padding: 0 var(--space-8) var(--space-6) var(--space-8);
  margin-top: -44px;
}

.profile-avatar-wrap { position: relative; flex-shrink: 0; }
.profile-avatar {
  width: 88px; height: 88px;
  border-radius: var(--radius-full);
  background: var(--gs-primary-tint);
  border: 4px solid var(--gs-surface);
  box-shadow: 0 2px 10px rgba(0,0,0,0.12);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display);
  font-size: var(--text-3xl); font-weight: 800;
  color: var(--gs-primary);
  overflow: hidden;
  transition: opacity var(--duration-fast);
}
.profile-avatar--uploading { opacity: 0.6; }
.profile-avatar__img { width: 100%; height: 100%; object-fit: cover; }
.profile-avatar__camera {
  position: absolute; bottom: 2px; right: 2px;
  width: 26px; height: 26px;
  display: flex; align-items: center; justify-content: center;
  background: var(--gs-primary); border: 2px solid var(--gs-surface);
  border-radius: var(--radius-full); color: #fff; cursor: pointer;
  transition: background var(--duration-fast);
}
.profile-avatar__camera:hover { background: oklch(40% 0.138 144); }

.profile-hero__info {
  padding-bottom: var(--space-2);
  align-self: flex-end;
}
.profile-name {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--gs-text);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-2);
}
.profile-badges { display: flex; align-items: center; gap: var(--space-2); }
.avatar-error { font-size: var(--text-xs); color: oklch(55% 0.18 25); margin-top: var(--space-2); }

/* ── Tab nav ── */
.tab-nav {
  display: flex;
  margin-bottom: var(--space-6);
  border-bottom: 2px solid var(--gs-border);
}
.tab-nav__item {
  padding: var(--space-3) var(--space-5);
  font-size: var(--text-sm); font-weight: 500;
  color: var(--gs-text-2); background: none; border: none;
  border-bottom: 2px solid transparent; margin-bottom: -2px;
  cursor: pointer; white-space: nowrap;
  transition: color var(--duration-fast), border-color var(--duration-fast);
}
.tab-nav__item:hover { color: var(--gs-text); }
.tab-nav__item--active { color: var(--gs-primary); border-bottom-color: var(--gs-primary); font-weight: 600; }

/* ── 我的简历 tab wrap ── */
.resume-tab-content {
  max-width: 680px;
}

/* ── Card ── */
.profile-card {
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  box-shadow: var(--shadow-sm);
}

/* ── Fields ── */
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field__label { font-size: var(--text-sm); font-weight: 500; color: var(--gs-text-2); }
.field__hint { font-size: var(--text-xs); color: var(--gs-text-3); margin-top: -4px; }
.field__error { font-size: var(--text-xs); color: oklch(55% 0.18 25); margin-top: var(--space-1); }

/* ── Resume ── */
.resume-current {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  background: var(--gs-primary-tint); border: 1px solid var(--gs-border); border-radius: var(--radius-lg);
}
.resume-current__name { flex: 1; font-size: var(--text-sm); font-weight: 500; color: var(--gs-text); }
.resume-empty {
  display: flex; flex-direction: column; align-items: center;
  gap: var(--space-3); padding: var(--space-8);
  color: var(--gs-text-3); font-size: var(--text-sm);
}
.upload-zone {
  display: flex; flex-direction: column; align-items: center;
  gap: var(--space-2); padding: var(--space-8);
  border: 2px dashed var(--gs-border); border-radius: var(--radius-lg);
  cursor: pointer; color: var(--gs-text-2); font-size: var(--text-sm);
  transition: border-color var(--duration-fast), background var(--duration-fast);
}
.upload-zone:hover { border-color: var(--gs-primary); background: var(--gs-primary-tint); }

.form-actions { display: flex; justify-content: flex-end; padding-top: var(--space-2); }
</style>
