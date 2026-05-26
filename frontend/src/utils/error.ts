/**
 * 把 FastAPI / Pydantic 的错误响应转成一句用户可读的中文。
 * detail 可能是字符串（业务错误）或数组（字段校验错误）。
 */
export function parseApiError(e: any, fallback = '操作失败，请重试'): string {
  const detail = e?.response?.data?.detail
  if (!detail) return fallback
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0]
    const field = (first?.loc ?? []).at(-1) as string | undefined
    if (field === 'email')    return '请输入正确的邮箱格式'
    if (field === 'password') return '密码格式不符合要求'
    if (field === 'name')     return '姓名不能为空'
    return first?.ctx?.reason ?? first?.msg ?? fallback
  }
  return fallback
}
