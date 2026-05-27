<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ChevronLeft, ChevronRight, X } from 'lucide-vue-next'

const props = defineProps<{
  modelValue: string   // "YYYY-MM" or ""
  placeholder?: string
  clearable?: boolean
}>()
const emit = defineEmits<{ 'update:modelValue': [v: string] }>()

const open    = ref(false)
const wrapRef = ref<HTMLElement>()

const currentYear = new Date().getFullYear()
const navYear = ref(
  props.modelValue ? parseInt(props.modelValue.slice(0, 4)) : currentYear
)

watch(() => props.modelValue, v => {
  if (v) navYear.value = parseInt(v.slice(0, 4))
})

const monthLabels = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']

const displayText = computed(() => {
  if (!props.modelValue) return props.placeholder ?? '选择年月'
  const [y, m] = props.modelValue.split('-')
  return `${y}年${parseInt(m)}月`
})

function selectMonth(m: number) {
  const mm = String(m).padStart(2, '0')
  emit('update:modelValue', `${navYear.value}-${mm}`)
  open.value = false
}

function isActive(m: number) {
  if (!props.modelValue) return false
  const [y, mo] = props.modelValue.split('-')
  return parseInt(y) === navYear.value && parseInt(mo) === m
}

function clear(e: Event) {
  e.stopPropagation()
  emit('update:modelValue', '')
}

function onOutside(e: MouseEvent) {
  if (wrapRef.value && !wrapRef.value.contains(e.target as Node)) open.value = false
}
onMounted(() => document.addEventListener('mousedown', onOutside))
onUnmounted(() => document.removeEventListener('mousedown', onOutside))
</script>

<template>
  <div class="gs-mp" ref="wrapRef">
    <div
      class="gs-mp__trigger input"
      :class="{ 'gs-mp__trigger--open': open }"
      role="button"
      tabindex="0"
      @click="open = !open"
      @keydown.enter.prevent="open = !open"
      @keydown.escape="open = false"
    >
      <span class="gs-mp__display" :class="{ 'gs-mp__display--empty': !modelValue }">
        {{ displayText }}
      </span>
      <button v-if="clearable && modelValue" type="button" class="gs-mp__clear" @click="clear">
        <X :size="12" />
      </button>
      <svg v-else class="gs-mp__arrow" :class="{ 'gs-mp__arrow--open': open }" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="m6 9 6 6 6-6"/></svg>
    </div>

    <Transition name="gs-mp-drop">
      <div v-if="open" class="gs-mp__popup" @click.stop>
        <div class="gs-mp__year-nav">
          <button type="button" class="gs-mp__nav-btn" @click="navYear--">
            <ChevronLeft :size="14" />
          </button>
          <span class="gs-mp__year-label">{{ navYear }} 年</span>
          <button type="button" class="gs-mp__nav-btn" @click="navYear++">
            <ChevronRight :size="14" />
          </button>
        </div>
        <div class="gs-mp__months">
          <button
            v-for="(label, idx) in monthLabels"
            :key="idx"
            type="button"
            class="gs-mp__month-btn"
            :class="{ 'gs-mp__month-btn--active': isActive(idx + 1) }"
            @click="selectMonth(idx + 1)"
          >{{ label }}</button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.gs-mp {
  position: relative;
  display: inline-block;
  width: 100%;
}

.gs-mp__trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
  gap: var(--space-2);
}
.gs-mp__trigger:focus { outline: 2px solid var(--gs-primary); outline-offset: 1px; }
.gs-mp__trigger--open { border-color: var(--gs-primary) !important; }

.gs-mp__display { flex: 1; }
.gs-mp__display--empty { color: var(--gs-text-3); }

.gs-mp__clear {
  display: flex; align-items: center; justify-content: center;
  width: 18px; height: 18px;
  border: none; background: var(--gs-surface-2); border-radius: var(--radius-full);
  color: var(--gs-text-3); cursor: pointer; flex-shrink: 0;
  transition: background var(--duration-fast), color var(--duration-fast);
}
.gs-mp__clear:hover { background: var(--gs-border); color: var(--gs-text); }

.gs-mp__arrow { color: var(--gs-text-3); flex-shrink: 0; transition: transform var(--duration-fast); }
.gs-mp__arrow--open { transform: rotate(180deg); }

.gs-mp__popup {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 200;
  width: 240px;
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--space-3);
}

.gs-mp__year-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--gs-border);
}
.gs-mp__year-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--gs-text);
}
.gs-mp__nav-btn {
  display: flex; align-items: center; justify-content: center;
  width: 28px; height: 28px;
  border: 1px solid var(--gs-border); border-radius: var(--radius-md);
  background: var(--gs-bg); color: var(--gs-text-2); cursor: pointer;
  transition: background var(--duration-fast), border-color var(--duration-fast);
}
.gs-mp__nav-btn:hover { background: var(--gs-primary-tint); border-color: var(--gs-primary); color: var(--gs-primary); }

.gs-mp__months {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-1);
}
.gs-mp__month-btn {
  padding: var(--space-2) 0;
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--gs-text-2);
  background: var(--gs-bg);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast), color var(--duration-fast), border-color var(--duration-fast);
  text-align: center;
}
.gs-mp__month-btn:hover {
  background: var(--gs-primary-tint);
  color: var(--gs-primary);
  border-color: var(--gs-primary);
}
.gs-mp__month-btn--active {
  background: var(--gs-primary);
  color: #fff;
  border-color: var(--gs-primary);
}

/* Dropdown transition */
.gs-mp-drop-enter-active,
.gs-mp-drop-leave-active { transition: opacity 0.15s, transform 0.15s; }
.gs-mp-drop-enter-from,
.gs-mp-drop-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
