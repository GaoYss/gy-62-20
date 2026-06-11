export const STATUS_TEXT = {
  pending: '待审核',
  approved: '已通过',
  rejected: '已拒绝',
  completed: '已完成',
  cancelled: '已取消'
}

export const TERMINAL_STATUSES = ['completed', 'cancelled', 'rejected']

export const VALID_TRANSITIONS = {
  pending: ['approved', 'rejected', 'cancelled'],
  approved: ['completed', 'cancelled'],
  rejected: [],
  completed: [],
  cancelled: []
}

export const STATUS_OPTIONS = [
  { value: 'pending', label: STATUS_TEXT.pending, from: [] },
  { value: 'approved', label: STATUS_TEXT.approved, from: ['pending'] },
  { value: 'rejected', label: STATUS_TEXT.rejected, from: ['pending'] },
  { value: 'completed', label: STATUS_TEXT.completed, from: ['approved'] },
  { value: 'cancelled', label: STATUS_TEXT.cancelled, from: ['pending', 'approved'] }
]

export function isTerminalStatus(status) {
  return TERMINAL_STATUSES.includes(status)
}

export function getAllowedStatusOptions(status, isEdit) {
  if (!isEdit) return STATUS_OPTIONS
  if (isTerminalStatus(status)) {
    return STATUS_OPTIONS.filter(o => o.value === status)
  }
  return STATUS_OPTIONS.filter(o => o.value === status || o.from.includes(status))
}
