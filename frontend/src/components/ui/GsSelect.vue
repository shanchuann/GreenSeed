<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ChevronDown } from 'lucide-vue-next'

export interface SelectOption {
  value: string
  label: string
}

const props = withDefaults(
  defineProps<{
    options: SelectOption[]
    modelValue: string
    placeholder?: string
    ariaLabel?: string
  }>(),
  { placeholder: '请选择' }
)

const emit = defineEmits<{
  (e: 'update:modelValue', v: string): void
}>()

const open      = ref(false)
const root      = ref<HTMLElement | null>(null)

const selected = computed(() =>
  props.options.find(o => o.value === props.modelValue) ?? null
)

function select(val: string) {
  emit('update:modelValue', val)
  open.value = false
}

function toggle() {
  open.value = !open.value
}

function onClickOutside(e: MouseEvent) {
  if (root.value && !root.value.contains(e.target as Node)) {
    open.value = false
  }
}

function onKeydown(e: KeyboardEvent) {
  if (!open.value) {
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
      e.preventDefault()
      open.value = true
    }
    return
  }
  const idx = props.options.findIndex(o => o.value === props.modelValue)
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    const next = props.options[(idx + 1) % props.options.length]
    emit('update:modelValue', next.value)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    const prev = props.options[(idx - 1 + props.options.length) % props.options.length]
    emit('update:modelValue', prev.value)
  } else if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault()
    open.value = false
  } else if (e.key === 'Escape') {
    open.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', onClickOutside, true))
onBeforeUnmount(() => document.removeEventListener('mousedown', onClickOutside, true))
</script>

<template>
  <div
    ref="root"
    class="gs-select"
    :class="{ 'gs-select--open': open }"
    :aria-label="ariaLabel"
    role="combobox"
    :aria-expanded="open"
    tabindex="0"
    @click="toggle"
    @keydown="onKeydown"
  >
    <span class="gs-select__value" :class="{ 'gs-select__value--placeholder': !selected }">
      {{ selected?.label ?? placeholder }}
    </span>
    <ChevronDown :size="14" :stroke-width="2" class="gs-select__chevron" aria-hidden="true" />

    <Transition name="dropdown">
      <ul v-if="open" class="gs-select__menu" role="listbox">
        <li
          v-for="opt in options"
          :key="opt.value"
          class="gs-select__option"
          :class="{ 'gs-select__option--selected': opt.value === modelValue }"
          role="option"
          :aria-selected="opt.value === modelValue"
          @mousedown.prevent="select(opt.value)"
        >
          {{ opt.label }}
        </li>
      </ul>
    </Transition>
  </div>
</template>

<style scoped>
.gs-select {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  height: 38px;
  padding-inline: var(--space-3) var(--space-3);
  background: var(--gs-surface);
  border: 1.5px solid var(--gs-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  user-select: none;
  outline: none;
  transition: border-color var(--duration-fast), box-shadow var(--duration-fast);
  white-space: nowrap;
}
.gs-select:focus,
.gs-select--open {
  border-color: var(--gs-primary);
  box-shadow: 0 0 0 3px var(--gs-primary-tint);
}

.gs-select__value {
  flex: 1;
  font-size: var(--text-sm);
  color: var(--gs-text-2);
  min-width: 60px;
}
.gs-select__value--placeholder { color: var(--gs-text-3); }

.gs-select__chevron {
  color: var(--gs-text-3);
  flex-shrink: 0;
  transition: transform var(--duration-fast) var(--ease-out);
}
.gs-select--open .gs-select__chevron {
  transform: rotate(180deg);
  color: var(--gs-primary);
}

/* Dropdown */
.gs-select__menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  min-width: 100%;
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  list-style: none;
  z-index: 200;
  padding: var(--space-1);
  overflow: hidden;
}

.gs-select__option {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  color: var(--gs-text-2);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast), color var(--duration-fast);
}
.gs-select__option:hover {
  background: var(--gs-surface-2);
  color: var(--gs-text);
}
.gs-select__option--selected {
  color: var(--gs-primary);
  font-weight: 600;
  background: var(--gs-primary-tint);
}

/* Animation */
.dropdown-enter-active {
  transition: opacity var(--duration-fast) var(--ease-out),
              transform var(--duration-fast) var(--ease-out);
}
.dropdown-leave-active {
  transition: opacity 80ms ease-in, transform 80ms ease-in;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
