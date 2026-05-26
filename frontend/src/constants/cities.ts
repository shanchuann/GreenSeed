import type { SelectOption } from '@/components/ui/GsSelect.vue'

const CITY_LIST = [
  '北京', '上海', '广州', '深圳',
  '天津', '重庆', '杭州', '成都', '武汉', '西安', '南京', '苏州',
  '郑州', '长沙', '青岛', '宁波', '合肥', '昆明', '福州', '厦门',
  '济南', '沈阳', '哈尔滨', '大连', '长春', '贵阳', '南宁', '南昌',
  '太原', '石家庄', '呼和浩特', '海口', '兰州', '银川', '西宁',
  '乌鲁木齐', '拉萨',
]

export const cityOptions: SelectOption[] = [
  { value: '', label: '全国' },
  ...CITY_LIST.map(c => ({ value: c, label: c })),
]
