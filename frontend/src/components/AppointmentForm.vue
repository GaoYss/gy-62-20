<template>
  <form class="form-grid" @submit.prevent="$emit('submit')">
    <template v-if="!(isEdit && isTerminal)">
      <label>
        探视老人
        <select v-model.number="model.resident_id" required>
          <option disabled value="">请选择</option>
          <option v-for="resident in residents" :key="resident.id" :value="resident.id">
            {{ resident.name }} · {{ resident.room_number }}
          </option>
        </select>
      </label>
      <label>
        家属姓名
        <input v-model="model.family_name" required />
      </label>
      <label>
        家属电话
        <input v-model="model.family_phone" required />
      </label>
      <label>
        关系
        <input v-model="model.relationship" required />
      </label>
      <label>
        探视时间
        <input v-model="model.visit_time" type="datetime-local" required />
      </label>
      <label>
        人数
        <input v-model.number="model.visitor_count" type="number" min="1" required />
      </label>
      <label>
        状态
        <select v-model="model.status">
          <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </label>
    </template>
    <label class="span-2">
      备注
      <textarea v-model="model.notes" rows="5" placeholder="请输入备注信息"></textarea>
    </label>
    <div class="form-actions">
      <button class="primary" type="submit">{{ isEdit ? '保存修改' : '提交预约' }}</button>
      <button v-if="isEdit" type="button" class="secondary" @click="$emit('cancel')">取消编辑</button>
    </div>
  </form>
</template>

<script setup>
import { computed } from 'vue'
import { getAllowedStatusOptions } from '../constants/appointments'

const props = defineProps({
  model: { type: Object, required: true },
  residents: { type: Array, default: () => [] },
  isEdit: { type: Boolean, default: false },
  isTerminal: { type: Boolean, default: false },
  currentStatus: { type: String, default: '' }
})
defineEmits(['submit', 'cancel'])

const statusOptions = computed(() => getAllowedStatusOptions(props.currentStatus || props.model.status, props.isEdit))
</script>
