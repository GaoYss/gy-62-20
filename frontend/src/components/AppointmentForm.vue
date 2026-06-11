<template>
  <form class="form-grid" @submit.prevent="$emit('submit')">
    <label>
      探视老人
      <select v-model.number="model.resident_id" required :disabled="isEdit && isTerminal">
        <option disabled value="">请选择</option>
        <option v-for="resident in residents" :key="resident.id" :value="resident.id">
          {{ resident.name }} · {{ resident.room_number }}
        </option>
      </select>
    </label>
    <label>
      家属姓名
      <input v-model="model.family_name" required :disabled="isEdit && isTerminal" />
    </label>
    <label>
      家属电话
      <input v-model="model.family_phone" required :disabled="isEdit && isTerminal" />
    </label>
    <label>
      关系
      <input v-model="model.relationship" required :disabled="isEdit && isTerminal" />
    </label>
    <label>
      探视时间
      <input v-model="model.visit_time" type="datetime-local" required :disabled="isEdit && isTerminal" />
    </label>
    <label>
      人数
      <input v-model.number="model.visitor_count" type="number" min="1" required :disabled="isEdit && isTerminal" />
    </label>
    <label>
      状态
      <select v-model="model.status" :disabled="isEdit && isTerminal">
        <option v-for="opt in allowedStatusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
      <p v-if="isEdit && isTerminal" class="hint">当前为终态，不可变更</p>
    </label>
    <label class="span-2">
      备注
      <textarea v-model="model.notes" rows="3"></textarea>
    </label>
    <div class="form-actions">
      <button class="primary" type="submit">{{ isEdit ? '保存修改' : '提交预约' }}</button>
      <button v-if="isEdit" type="button" class="secondary" @click="$emit('cancel')">取消编辑</button>
    </div>
  </form>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  model: { type: Object, required: true },
  residents: { type: Array, default: () => [] },
  isEdit: { type: Boolean, default: false },
  currentStatus: { type: String, default: '' }
})
defineEmits(['submit', 'cancel'])

const TERMINAL_STATUSES = ['completed', 'cancelled', 'rejected']

const ALL_STATUS_OPTIONS = [
  { value: 'pending', label: '待审核', from: [] },
  { value: 'approved', label: '已通过', from: ['pending'] },
  { value: 'rejected', label: '已拒绝', from: ['pending'] },
  { value: 'completed', label: '已完成', from: ['approved'] },
  { value: 'cancelled', label: '已取消', from: ['pending', 'approved'] }
]

const isTerminal = computed(() => TERMINAL_STATUSES.includes(props.currentStatus || props.model.status))

const allowedStatusOptions = computed(() => {
  if (!props.isEdit) {
    return ALL_STATUS_OPTIONS
  }
  const cur = props.currentStatus || props.model.status
  if (TERMINAL_STATUSES.includes(cur)) {
    return ALL_STATUS_OPTIONS.filter(o => o.value === cur)
  }
  return ALL_STATUS_OPTIONS.filter(o => {
    if (o.value === cur) return true
    return o.from.includes(cur)
  })
})
</script>
