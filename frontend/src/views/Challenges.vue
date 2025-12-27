<template>
  <div class="challenges-container">
    <el-container>
      <el-aside width="250px">
        <div class="logo">CyberPrism</div>
        <el-menu :default-active="'challenges'" @select="handleMenuSelect">
          <el-menu-item index="challenges">
            <el-icon><Document /></el-icon>
            <span>题目挑战</span>
          </el-menu-item>
          <el-menu-item index="profile">
            <el-icon><UserFilled /></el-icon>
            <span>个人资料</span>
          </el-menu-item>
          <el-menu-item index="containers">
            <el-icon><Box /></el-icon>
            <span>我的容器</span>
          </el-menu-item>
          <el-menu-item index="leaderboard">
            <el-icon><TrendCharts /></el-icon>
            <span>排行榜</span>
          </el-menu-item>
          <el-menu-item v-if="user.is_admin" index="admin">
            <el-icon><Setting /></el-icon>
            <span>管理后台</span>
          </el-menu-item>
          <el-menu-item index="logout" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main>
        <el-card>
          <template #header>
            <div class="card-header">
              <h2>题目挑战</h2>
              <el-space>
                <el-select v-model="filters.category" placeholder="一级分类" clearable @change="handleCategoryChange" style="width: 180px">
                  <el-option label="全部分类" value="" />
                  <el-option
                    v-for="category in categories"
                    :key="category"
                    :label="category"
                    :value="category"
                  />
                </el-select>
                <el-select v-model="filters.skillTag" placeholder="二级技能标签" clearable @change="loadChallenges" :disabled="!filters.category" style="width: 180px">
                  <el-option label="全部技能" value="" />
                  <el-option
                    v-for="(code, skillName) in getSkillOptions()"
                    :key="code"
                    :label="`${skillName}`"
                    :value="code"
                  />
                </el-select>
                <el-select v-model="filters.type" placeholder="题目类型" clearable @change="loadChallenges" style="width: 120px">
                  <el-option label="全部类型" value="" />
                  <el-option label="选择题" value="choice" />
                  <el-option label="靶场题" value="docker" />
                </el-select>
                <el-select v-model="filters.difficulty" placeholder="难度" clearable @change="loadChallenges" style="width: 100px">
                  <el-option label="全部" value="" />
                  <el-option label="简单" value="easy" />
                  <el-option label="中等" value="medium" />
                  <el-option label="困难" value="hard" />
                </el-select>
              </el-space>
            </div>
          </template>

          <div v-loading="loading">
            <el-empty v-if="groupedChallenges.length === 0" description="暂无题目" />

            <!-- 按类别分组显示 -->
            <div v-else>
              <div v-for="group in groupedChallenges" :key="group.category" style="margin-bottom: 40px">
                <div class="category-header">
                  <h3>{{ group.category }}</h3>
                  <el-tag type="info" size="large">{{ group.challenges.length }} 道题目</el-tag>
                </div>

                <!-- 按技能标签分组 -->
                <div v-for="skillGroup in group.skillGroups" :key="skillGroup.skillCode" style="margin-bottom: 20px">
                  <div class="skill-header">
                    <h4>{{ skillGroup.skillName }} ({{ skillGroup.skillCode }})</h4>
                    <el-tag size="small">{{ skillGroup.challenges.length }} 道</el-tag>
                  </div>

                  <el-row :gutter="15">
                    <el-col :span="8" v-for="challenge in skillGroup.challenges" :key="challenge.id">
                      <el-card shadow="hover" class="challenge-card" @click="openChallenge(challenge)">
                        <template #header>
                          <div class="challenge-header">
                            <span class="challenge-title">{{ challenge.title }}</span>
                            <el-tag v-if="challenge.solved" type="success" size="small">✓</el-tag>
                          </div>
                        </template>

                        <div class="challenge-info">
                          <el-space direction="vertical" :size="5" style="width: 100%">
                            <div style="display: flex; justify-content: space-between">
                              <el-tag v-if="challenge.type === 'choice'" type="info" size="small">选择题</el-tag>
                              <el-tag v-else type="warning" size="small">靶场题</el-tag>
                              <el-tag :type="getDifficultyType(challenge.difficulty)" size="small">
                                {{ getDifficultyText(challenge.difficulty) }}
                              </el-tag>
                            </div>
                            <div style="text-align: center; font-size: 24px; font-weight: bold; color: #409EFF">
                              {{ challenge.points }}分
                            </div>
                          </el-space>
                        </div>
                      </el-card>
                    </el-col>
                  </el-row>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 题目详情对话框 -->
        <el-dialog
          v-model="dialogVisible"
          :title="currentChallenge?.title"
          width="600px"
        >
          <div v-if="currentChallenge">
            <!-- 选择题 -->
            <div v-if="currentChallenge.type === 'choice'">
              <h3 style="margin-bottom: 20px;">{{ currentChallenge.question }}</h3>
              <el-radio-group v-model="userAnswer" style="width: 100%;">
                <el-radio
                  v-for="(text, key) in currentChallenge.options"
                  :key="key"
                  :label="key"
                  class="option-radio"
                >
                  {{ key }}. {{ text }}
                </el-radio>
              </el-radio-group>
            </div>

            <!-- 靶场题 -->
            <div v-else-if="currentChallenge.type === 'docker'">
              <el-alert
                title="靶场说明"
                type="info"
                :closable="false"
                style="margin-bottom: 15px;"
              >
                <p>点击"启动容器"后,系统会为你创建独立的靶场环境</p>
                <p>容器将在60分钟后自动过期,你可以延长时间</p>
                <p>每个用户最多同时运行3个容器</p>
              </el-alert>

              <!-- 容器信息卡片 -->
              <el-card v-if="containerInfo" shadow="hover" style="margin-bottom: 15px;">
                <template #header>
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold;">容器信息</span>
                    <el-tag type="success" size="small">运行中</el-tag>
                  </div>
                </template>

                <p style="margin: 8px 0;">
                  <strong>访问地址:</strong>
                  <a :href="containerAccessUrl" target="_blank" style="color: #409EFF; margin-left: 8px;">
                    {{ containerAccessUrl }}
                  </a>
                  <el-button
                    type="primary"
                    size="small"
                    text
                    @click="copyToClipboard(containerAccessUrl)"
                    style="margin-left: 8px;"
                  >
                    复制
                  </el-button>
                </p>
                <p style="margin: 8px 0;">
                  <strong>剩余时间:</strong>
                  <span :style="{ color: remainingMinutes < 10 ? '#F56C6C' : '#67C23A', marginLeft: '8px', fontWeight: 'bold' }">
                    {{ remainingTimeText }}
                  </span>
                </p>
                <div style="margin-top: 15px;">
                  <el-space>
                    <el-button
                      type="warning"
                      size="small"
                      @click="extendContainerTime"
                      :loading="extendLoading"
                    >
                      延长30分钟
                    </el-button>
                    <el-button
                      type="danger"
                      size="small"
                      @click="destroyContainer"
                      :loading="destroyLoading"
                    >
                      销毁容器
                    </el-button>
                  </el-space>
                </div>
              </el-card>

              <el-input
                v-model="userAnswer"
                placeholder="请输入找到的FLAG"
                style="margin-top: 10px;"
              />
            </div>

            <!-- 分类和分值 -->
            <el-descriptions :column="2" border style="margin-top: 20px;">
              <el-descriptions-item label="分类">{{ currentChallenge.category }}</el-descriptions-item>
              <el-descriptions-item label="分值">{{ currentChallenge.points }}分</el-descriptions-item>
            </el-descriptions>

            <!-- 描述 (无边框) -->
            <div v-if="currentChallenge.description" class="description-section">
              {{ currentChallenge.description }}
            </div>
          </div>

          <template #footer>
            <el-space>
              <el-button @click="dialogVisible = false">取消</el-button>
              <el-button
                v-if="currentChallenge?.type === 'docker'"
                type="warning"
                @click="startContainer"
                :loading="containerLoading"
                :disabled="containerInfo && containerInfo.status === 'running'"
              >
                {{ containerInfo && containerInfo.status === 'running' ? '容器已启动' : '启动容器' }}
              </el-button>
              <el-button
                type="primary"
                @click="submitAnswer"
                :loading="submitLoading"
                :disabled="!userAnswer"
              >
                提交答案
              </el-button>
            </el-space>
          </template>
        </el-dialog>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getChallenges, submitAnswer as submitAnswerAPI } from '@/api/challenge'
import { startContainer as startContainerAPI, stopContainer, extendContainer, getMyContainers } from '@/api/container'

// 技能标签矩阵（与后端保持一致）
const SKILL_MATRIX = {
  "信息收集与侦察": {
    "信息收集": "T1071",
    "网络扫描": "T1046",
    "子域枚举": "T1071",
    "网络拓扑分析": "T1027"
  },
  "漏洞利用与攻击": {
    "利用公共漏洞": "T1203",
    "提权与横向移动": "T1075",
    "社会工程学攻击": "T1071",
    "恶意软件": "T1053"
  },
  "后渗透": {
    "横向移动": "T1021",
    "后门植入": "T1012",
    "权限提升": "T1088"
  },
  "防御规避与反侦察": {
    "权限提升": "T1088",
    "文件/日志清理": "T1070",
    "命令与控制": "T1071"
  }
}

export default {
  name: 'Challenges',
  setup() {
    const router = useRouter()
    const user = JSON.parse(localStorage.getItem('user') || '{}')

    const loading = ref(false)
    const challenges = ref([])
    const dialogVisible = ref(false)
    const currentChallenge = ref(null)
    const userAnswer = ref('')
    const submitLoading = ref(false)
    const containerLoading = ref(false)

    // 容器管理相关状态
    const containerInfo = ref(null)
    const extendLoading = ref(false)
    const destroyLoading = ref(false)
    const countdownTimer = ref(null)
    const remainingSeconds = ref(0)

    const filters = ref({
      category: '',
      skillTag: '',
      type: '',
      difficulty: ''
    })

    const categories = Object.keys(SKILL_MATRIX)

    const getSkillOptions = () => {
      if (!filters.value.category) return {}
      return SKILL_MATRIX[filters.value.category] || {}
    }

    const handleCategoryChange = () => {
      filters.value.skillTag = ''
      loadChallenges()
    }

    // 容器访问地址
    const containerAccessUrl = computed(() => {
      if (!containerInfo.value || !containerInfo.value.host_port) return ''
      return `http://${window.location.hostname}:${containerInfo.value.host_port}`
    })

    // 剩余时间(分钟)
    const remainingMinutes = computed(() => {
      return Math.floor(remainingSeconds.value / 60)
    })

    // 剩余时间文本
    const remainingTimeText = computed(() => {
      const minutes = Math.floor(remainingSeconds.value / 60)
      const seconds = remainingSeconds.value % 60
      return `${minutes}分${seconds}秒`
    })

    // 计算剩余秒数
    const calculateRemainingSeconds = () => {
      if (!containerInfo.value || !containerInfo.value.expires_at) {
        remainingSeconds.value = 0
        return
      }

      const expiresAt = new Date(containerInfo.value.expires_at)
      const now = new Date()
      const diff = Math.floor((expiresAt - now) / 1000)
      remainingSeconds.value = diff > 0 ? diff : 0

      if (remainingSeconds.value === 0 && containerInfo.value.status === 'running') {
        // 容器已过期
        containerInfo.value.status = 'stopped'
        ElMessage.warning('容器已过期')
        stopCountdown()
      }
    }

    // 启动倒计时
    const startCountdown = () => {
      stopCountdown()
      calculateRemainingSeconds()
      countdownTimer.value = setInterval(() => {
        if (remainingSeconds.value > 0) {
          remainingSeconds.value--
        } else {
          stopCountdown()
          if (containerInfo.value) {
            containerInfo.value.status = 'stopped'
          }
          ElMessage.warning('容器已过期')
        }
      }, 1000)
    }

    // 停止倒计时
    const stopCountdown = () => {
      if (countdownTimer.value) {
        clearInterval(countdownTimer.value)
        countdownTimer.value = null
      }
    }

    // 复制到剪贴板
    const copyToClipboard = async (text) => {
      try {
        await navigator.clipboard.writeText(text)
        ElMessage.success('已复制到剪贴板')
      } catch (error) {
        ElMessage.error('复制失败')
      }
    }

    // 检查当前题目的容器
    const checkChallengeContainer = async () => {
      if (!currentChallenge.value || currentChallenge.value.type !== 'docker') {
        return
      }

      try {
        const containers = await getMyContainers()

        // 查找当前题目的运行中容器(后端已只返回running状态的容器)
        const challengeContainer = containers.find(
          c => c.challenge_id === currentChallenge.value.id
        )

        if (challengeContainer) {
          containerInfo.value = challengeContainer
          startCountdown()
        } else {
          containerInfo.value = null
          stopCountdown()
        }
      } catch (error) {
        console.error('获取容器信息失败:', error)
      }
    }

    // 计算属性: 按类别和技能标签分组题目
    const groupedChallenges = computed(() => {
      if (challenges.value.length === 0) return []

      const groups = {}

      challenges.value.forEach(challenge => {
        const category = challenge.category
        if (!groups[category]) {
          groups[category] = {
            category: category,
            challenges: [],
            skillGroups: {}
          }
        }

        groups[category].challenges.push(challenge)

        // 按技能标签分组
        try {
          const skillTags = typeof challenge.skill_tags === 'string'
            ? JSON.parse(challenge.skill_tags)
            : challenge.skill_tags || {}

          Object.entries(skillTags).forEach(([skillCode, skillName]) => {
            if (!groups[category].skillGroups[skillCode]) {
              groups[category].skillGroups[skillCode] = {
                skillCode: skillCode,
                skillName: skillName,
                challenges: []
              }
            }
            groups[category].skillGroups[skillCode].challenges.push(challenge)
          })
        } catch (e) {
          console.error('Failed to parse skill_tags:', challenge.skill_tags, e)
        }
      })

      // 转换为数组
      return Object.values(groups).map(group => ({
        ...group,
        skillGroups: Object.values(group.skillGroups)
      }))
    })

    const loadChallenges = async () => {
      loading.value = true
      try {
        const params = {}
        if (filters.value.category) params.category = filters.value.category
        if (filters.value.type) params.type = filters.value.type
        if (filters.value.difficulty) params.difficulty = filters.value.difficulty

        challenges.value = await getChallenges(params)

        // 前端过滤技能标签（如果后端不支持）
        if (filters.value.skillTag) {
          challenges.value = challenges.value.filter(challenge => {
            try {
              const skillTags = typeof challenge.skill_tags === 'string'
                ? JSON.parse(challenge.skill_tags)
                : challenge.skill_tags || {}
              return Object.keys(skillTags).includes(filters.value.skillTag)
            } catch (e) {
              return false
            }
          })
        }
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    const openChallenge = async (challenge) => {
      // 检查是否已经正确解答过
      if (challenge.solved) {
        ElMessage.info('您已经正确解答过此题')
        return
      }

      currentChallenge.value = challenge
      userAnswer.value = ''
      containerInfo.value = null
      stopCountdown()
      dialogVisible.value = true

      // 如果是靶场题,检查是否有运行的容器
      if (challenge.type === 'docker') {
        await checkChallengeContainer()
      }
    }

    const submitAnswer = async () => {
      if (!userAnswer.value.trim()) {
        ElMessage.warning('请输入答案')
        return
      }

      submitLoading.value = true
      try {
        const result = await submitAnswerAPI(currentChallenge.value.id, {
          answer: userAnswer.value.trim()
        })

        if (result.is_correct) {
          ElMessage.success(`恭喜!答案正确!获得${result.points}分`)

          // 如果是靶场题,容器会被后端自动销毁,清除前端状态
          if (currentChallenge.value.type === 'docker') {
            containerInfo.value = null
            stopCountdown()
          }

          dialogVisible.value = false
          loadChallenges() // 重新加载以更新solved状态
        } else {
          ElMessage.error(result.message || '答案错误,请重试')
        }
      } catch (error) {
        console.error(error)
      } finally {
        submitLoading.value = false
      }
    }

    const startContainer = async () => {
      containerLoading.value = true
      try {
        const result = await startContainerAPI(currentChallenge.value.id)
        ElMessage.success('容器启动成功!')

        containerInfo.value = result.container
        startCountdown()
      } catch (error) {
        console.error(error)
        const errorMsg = error.response?.data?.error || error.message || '启动失败'
        ElMessage.error(errorMsg)
      } finally {
        containerLoading.value = false
      }
    }

    const extendContainerTime = async () => {
      if (!containerInfo.value) return

      extendLoading.value = true
      try {
        const result = await extendContainer(containerInfo.value.id, 30)
        ElMessage.success('容器时间已延长30分钟')

        containerInfo.value = result.container
        calculateRemainingSeconds()
      } catch (error) {
        console.error(error)
        const errorMsg = error.response?.data?.error || error.message || '延长失败'
        ElMessage.error(errorMsg)
      } finally {
        extendLoading.value = false
      }
    }

    const destroyContainer = async () => {
      if (!containerInfo.value) return

      try {
        await ElMessageBox.confirm('确定要销毁容器吗?', '警告', {
          type: 'warning',
          confirmButtonText: '确定',
          cancelButtonText: '取消'
        })

        destroyLoading.value = true
        await stopContainer(containerInfo.value.id)
        ElMessage.success('容器已销毁')

        containerInfo.value = null
        stopCountdown()
      } catch (error) {
        if (error !== 'cancel') {
          console.error(error)
          const errorMsg = error.response?.data?.error || error.message || '销毁失败'
          ElMessage.error(errorMsg)
        }
      } finally {
        destroyLoading.value = false
      }
    }

    const getDifficultyType = (difficulty) => {
      const types = {
        easy: 'success',
        medium: 'warning',
        hard: 'danger'
      }
      return types[difficulty] || 'info'
    }

    const getDifficultyText = (difficulty) => {
      const texts = {
        easy: '简单',
        medium: '中等',
        hard: '困难'
      }
      return texts[difficulty] || difficulty
    }

    const handleMenuSelect = (index) => {
      if (index === 'admin') {
        router.push('/admin')
      } else {
        router.push(`/${index}`)
      }
    }

    const handleLogout = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      ElMessage.success('已退出登录')
      router.push('/login')
    }

    onMounted(() => {
      loadChallenges()
    })

    onUnmounted(() => {
      stopCountdown()
    })

    return {
      user,
      loading,
      challenges,
      groupedChallenges,
      categories,
      filters,
      dialogVisible,
      currentChallenge,
      userAnswer,
      submitLoading,
      containerLoading,
      containerInfo,
      containerAccessUrl,
      remainingMinutes,
      remainingTimeText,
      extendLoading,
      destroyLoading,
      getSkillOptions,
      handleCategoryChange,
      loadChallenges,
      openChallenge,
      submitAnswer,
      startContainer,
      extendContainerTime,
      destroyContainer,
      copyToClipboard,
      getDifficultyType,
      getDifficultyText,
      handleMenuSelect,
      handleLogout
    }
  }
}
</script>

<style scoped>
.challenges-container {
  min-height: 100vh;
  background: #f0f2f5;
}

.el-aside {
  background: #001529;
  min-height: 100vh;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
  background: rgba(255,255,255,0.1);
}

.el-menu {
  border: none;
  background: #001529;
}

:deep(.el-menu-item) {
  color: rgba(255,255,255,0.65);
}

:deep(.el-menu-item:hover) {
  color: #fff;
  background: rgba(255,255,255,0.1) !important;
}

:deep(.el-menu-item.is-active) {
  color: #fff;
  background: #1890ff !important;
}

.el-main {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.category-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: bold;
}

.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 10px 15px;
  background: #f5f7fa;
  border-left: 4px solid #409EFF;
  border-radius: 4px;
}

.skill-header h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.challenge-card {
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.challenge-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.15);
}

.challenge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.challenge-title {
  font-weight: bold;
  font-size: 16px;
}

.challenge-info {
  margin-top: 10px;
}

/* 选项样式 - 带边框,每行一个 */
.option-radio {
  display: flex !important;
  align-items: center;
  width: 100%;
  margin: 10px 0 !important;
  padding: 15px 18px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  transition: all 0.3s;
  min-height: 50px;
}

.option-radio:hover {
  border-color: #409EFF;
  background-color: #f0f7ff;
}

:deep(.option-radio.is-checked) {
  border-color: #409EFF;
  background-color: #ecf5ff;
}

/* 描述区域样式 - 无边框 */
.description-section {
  margin-top: 15px;
  padding: 15px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  border-top: 1px dashed #e4e7ed;
}
</style>
