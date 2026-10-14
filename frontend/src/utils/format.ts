export function formatDate(value: string | null | undefined): string {
  return value ? new Date(value).toLocaleString() : '-'
}

export function fullName(user: { first_name: string | null; last_name: string | null }): string {
  return [user.first_name, user.last_name].filter(Boolean).join(' ')
}
