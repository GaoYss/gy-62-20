<template>
  <section>
    <PageHeader eyebrow="预约" title="家属预约探视" description="家属提交探视申请，工作人员可登记预约状态和备注。" />

    <article class="panel">
      <h3>{{ formTitle }}</h3>
      <p v-if="editingId && isTerminalStatus" class="terminal-notice">当前为终态预约，仅可修改备注信息。</p>
      <AppointmentForm
        :model="form"
        :residents="residents"
        :isEdit="!!editingId"
        :currentStatus="originalStatus"
        @submit="saveAppointment"
        @cancel="cancelEdit"
      />
      <p v-if="message" :class="['message', messageType]">{{ message }}</p>
    </article>

    <article class="panel">
      <h3>预约列表</h3>
      <EmptyState v-if="appointments.length === 0" />
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>老人</th>
              <th>家属</th>
              <th>探视时间</th>
              <th>人数</th>
              <th>状态</th>
              <th>备注</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in appointments" :key="item.id">
              <td>{{ item.resident.name }} · {{ item.resident.room_number }}</td>
              <td>{{ item.family_name }} · {{ item.family_phone }}</td>
              <td>{{ formatTime(item.visit_time) }}</td>
              <td>{{ item.visitor_count }}</td>
              <td><span :class="['badge', item.status]">{{ statusText[item.status] }}</span></td>
              <td>{{ item.notes || '无' }}</td>
              <td>
                <div class="actions">
                  <button
                    v-for="action in availableActions(item.status)"
                    :key="action.key"
                    :class="['btn', action.className]"
                    @click="doAction(item, action.key)"
                  >{{ action.label }}</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import AppointmentForm from '../components/AppointmentForm.vue'
import EmptyState from '../components/EmptyState.vue'
import PageHeader from '../components/PageHeader.vue'
import { appointmentsApi } from '../services/appointments'
import { residentsApi } from '../services/residents'

const residents = ref([])
const appointments = ref([])
const message = ref('')
const messageType = ref('')
const editingId = ref(null)
const originalStatus = ref('')
const statusText = { pending: '待审核', approved: '已通过', rejected: '已拒绝', completed: '已完成', cancelled: '已取消' }

const ACTION_MAP = {
  approve: { key: 'approve', label: '通过', className: 'success', status: 'approved' },
  reject: { key: 'reject', label: '拒绝', className: 'danger', status: 'rejected' },
  complete: { key: 'complete', label: '完成', className: 'primary', status: 'completed' },
  cancel: { key: 'cancel', label: '取消', className: 'warning', status: 'cancelled' },
  edit: { key: 'edit', label: '编辑', className: 'secondary' },
  note: { key: 'edit', label: '修改备注', className: 'secondary' }
}

const TERMINAL_STATUSES = ['completed', 'cancelled', 'rejected']

const TRANSITION_RULES = {
  pending: ['approve', 'reject', 'cancel', 'edit'],
  approved: ['complete', 'cancel', 'edit'],
  rejected: ['note'],
  completed: ['note'],
  cancelled: ['note']
}

const initialForm = {
  resident_id: '',
  family_name: '',
  family_phone: '',
  relationship: '',
  visit_time: '',
  visitor_count: 1,
  status: 'pending',
  notes: ''
}
const form = reactive({ ...initialForm })

const isTerminalStatus = computed(() => TERMINAL_STATUSES.includes(originalStatus.value))

const formTitle = computed(() => {
  if (!editingId.value) return '新建预约'
  return isTerminalStatus.value ? '修改备注' : '编辑预约'
})

onMounted(async () => {
  await Promise.all([loadResidents(), loadAppointments()])
})

async function loadResidents() {
  residents.value = (await residentsApi.list()).results
}

async function loadAppointments() {
  appointments.value = (await appointmentsApi.list()).results
}

function availableActions(status) {
  const keys = TRANSITION_RULES[status] || []
  return keys.map(k => ACTION_MAP[k])
}

async function saveAppointment() {
  try {
    if (editingId.value) {
      await appointmentsApi.update(editingId.value, { ...form })
      showMessage('修改已保存', 'success')
    } else {
      await appointmentsApi.create(form)
      Object.assign(form, initialForm)
      showMessage('预约已提交', 'success')
    }
    cancelEdit()
    await loadAppointments()
  } catch (e) {
    showMessage(e.message || '操作失败', 'error')
  }
}

async function doAction(item, actionKey) {
  if (actionKey === 'edit') {
    startEdit(item)
    return
  }
  const action = ACTION_MAP[actionKey]
  const confirmMsg = actionKey === 'cancel'
    ? `确定要取消此预约吗？`
    : `确定将状态变更为「${statusText[action.status]}」吗？`
  if (!window.confirm(confirmMsg)) return
  try {
    if (actionKey === 'cancel') {
      await appointmentsApi.remove(item.id)
    } else {
      await appointmentsApi.update(item.id, { status: action.status })
    }
    showMessage(`操作成功：${action.label}`, 'success')
    await loadAppointments()
  } catch (e) {
    showMessage(e.message || '操作失败', 'error')
  }
}

function startEdit(item) {
  editingId.value = item.id
  originalStatus.value = item.status
  const t = new Date(item.visit_time)
  const pad = n => String(n).padStart(2, '0')
  const localTime = `${t.getFullYear()}-${pad(t.getMonth() + 1)}-${pad(t.getDate())}T${pad(t.getHours())}:${pad(t.getMinutes())}`
  Object.assign(form, {
    resident_id: item.resident_id,
    family_name: item.family_name,
    family_phone: item.family_phone,
    relationship: item.relationship,
    visit_time: localTime,
    visitor_count: item.visitor_count,
    status: item.status,
    notes: item.notes || ''
  })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelEdit() {
  editingId.value = null
  originalStatus.value = ''
  Object.assign(form, initialForm)
}

function showMessage(msg, type) {
  message.value = msg
  messageType.value = type
  setTimeout(() => { message.value = '' }, 4000)
}

function formatTime(value) {
  return value ? new Date(value).toLocaleString('zh-CN') : ''
}
</script>
