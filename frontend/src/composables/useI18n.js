import { ref, computed } from 'vue'

const currentLocale = ref(localStorage.getItem('locale') || 'en')

const translations = {
  en: {
    appTitle: 'Recording Management',
    queryRecordings: 'Recordings',
    importRecordings: 'Import',
    userManagement: 'Users',
    logout: 'Logout',
    admin: 'Admin',
    login: 'Sign In',
    username: 'Username',
    password: 'Password',
    signIn: 'Sign In',
    defaultCredentials: 'Default admin:',
    common: {
      confirm: 'Confirm',
      cancel: 'Cancel'
    },
    query: {
      title: 'Query Recordings',
      startTime: 'Start Time',
      endTime: 'End Time',
      channel: 'Channel',
      participantName: 'Participant Name (Optional)',
      searchByParticipant: 'Search by participant',
      search: 'Search Recordings',
      searching: 'Searching...',
      results: 'Results',
      recordingsFound: 'recordings found',
      noRecordings: 'No recordings found for the specified criteria',
      emptyState: 'Enter query parameters and search for recordings',
      recentSearches: 'Recent searches',
      clearHistory: 'Clear',
      details: 'Details',
      delete: 'Delete',
      deleteSelected: 'Delete Selected',
      transcribed: 'Transcribed',
      actions: 'Actions',
      confirmDelete: 'Are you sure you want to delete this recording? This will also delete the audio file.'
    },
    users: {
      title: 'User Management',
      createUser: 'Create User',
      username: 'Username',
      password: 'Password',
      delete: 'Delete',
      admin: 'Admin'
    },
    player: {
      title: 'Audio Player',
      userName: 'User Name',
      startTime: 'Start Time',
      duration: 'Duration',
      play: 'Play',
      resume: 'Resume',
      pause: 'Pause',
      stop: 'Stop',
      quit: 'Quit',
      transcription: 'Transcription',
      transcribing: 'Transcribing...',
      noTranscription: 'No transcription available'
    },
    import: {
      title: 'Recording Import',
      selected: 'selected',
      selectAll: 'Select All',
      deselectAll: 'Deselect All',
      import: 'Import',
      importing: 'Importing...'
    },
    theme: {
      light: 'Light',
      dark: 'Dark'
    }
  },
  zh: {
    appTitle: '录音管理系统',
    queryRecordings: '录音查询',
    importRecordings: '录音导入',
    userManagement: '用户管理',
    logout: '退出登录',
    admin: '管理员',
    login: '登录',
    username: '用户名',
    password: '密码',
    signIn: '登录',
    defaultCredentials: '默认管理员:',
    common: {
      confirm: '确认',
      cancel: '取消'
    },
    query: {
      title: '录音查询',
      startTime: '开始时间',
      endTime: '结束时间',
      channel: '渠道',
      participantName: '参与人姓名 (可选)',
      searchByParticipant: '按参与人搜索',
      search: '搜索录音',
      searching: '搜索中...',
      results: '结果',
      recordingsFound: '条录音',
      noRecordings: '未找到符合条件录音',
      emptyState: '输入查询条件并搜索录音',
      recentSearches: '最近搜索',
      clearHistory: '清除',
      details: '录音详情',
      delete: '删除',
      deleteSelected: '删除所选',
      transcribed: '已转录',
      actions: '操作',
      confirmDelete: '确定要删除此录音吗？这将同时删除音频文件。'
    },
    users: {
      title: '用户管理',
      createUser: '创建用户',
      username: '用户名',
      password: '密码',
      delete: '删除',
      admin: '管理员'
    },
    player: {
      title: '音频播放器',
      userName: '用户姓名',
      startTime: '开始时间',
      duration: '时长',
      play: '播放',
      resume: '继续',
      pause: '暂停',
      stop: '停止',
      quit: '退出',
      transcription: '转录文本',
      transcribing: '转录中...',
      noTranscription: '暂无转录文本'
    },
    import: {
      title: '录音导入',
      selected: '已选择',
      selectAll: '全选',
      deselectAll: '取消全选',
      import: '导入',
      importing: '导入中...'
    },
    theme: {
      light: '浅色',
      dark: '深色'
    }
  }
}

export function useI18n() {
  const t = (key) => {
    const keys = key.split('.')
    let value = translations[currentLocale.value]
    for (const k of keys) {
      value = value?.[k]
    }
    return value || key
  }
  
  const locale = computed(() => currentLocale.value)
  
  function setLocale(lang) {
    currentLocale.value = lang
    localStorage.setItem('locale', lang)
  }
  
  return { t, locale, setLocale }
}
