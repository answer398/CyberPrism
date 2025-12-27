<template>
  <div class="admin-challenges-container">
    <el-container>
      <el-aside width="250px">
        <div class="logo">CyberPrism</div>
        <el-menu :default-active="'admin/challenges'" @select="handleMenuSelect">
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
          <el-sub-menu v-if="user.is_admin" index="admin">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>管理后台</span>
            </template>
            <el-menu-item index="admin/dashboard">
              <el-icon><DataAnalysis /></el-icon>
              <span>控制台</span>
            </el-menu-item>
            <el-menu-item index="admin/users">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="admin/challenges">
              <el-icon><Document /></el-icon>
              <span>题目管理</span>
            </el-menu-item>
            <el-menu-item index="admin/submissions">
              <el-icon><List /></el-icon>
              <span>提交记录</span>
            </el-menu-item>
            <el-menu-item index="admin/containers">
              <el-icon><Box /></el-icon>
              <span>容器管理</span>
            </el-menu-item>
          </el-sub-menu>
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
              <h2>题目管理</h2>
              <el-button type="primary" @click="showAddDialog">添加题目</el-button>
            </div>
          </template>

          <!-- 筛选器 -->
          <div style="margin-bottom: 15px;">
            <el-space wrap>
              <el-select v-model="filterCategory" placeholder="一级分类" clearable @change="handleFilterCategoryChange" style="width: 200px;">
                <el-option label="全部分类" value="" />
                <el-option
                  v-for="category in Object.keys(skillMatrix)"
                  :key="category"
                  :label="category"
                  :value="category"
                />
              </el-select>

              <el-select v-model="filterSkillTag" placeholder="二级技能标签" clearable style="width: 200px;">
                <el-option label="全部技能" value="" />
                <el-option
                  v-for="(code, skillName) in getFilterSkillOptions()"
                  :key="code"
                  :label="`${skillName} (${code})`"
                  :value="skillName"
                />
              </el-select>

              <el-select v-model="filterType" placeholder="题目类型" clearable style="width: 150px;">
                <el-option label="全部类型" value="" />
                <el-option label="选择题" value="choice" />
                <el-option label="靶场题" value="docker" />
              </el-select>

              <el-select v-model="filterDifficulty" placeholder="难度" clearable style="width: 150px;">
                <el-option label="全部难度" value="" />
                <el-option label="简单" value="easy" />
                <el-option label="中等" value="medium" />
                <el-option label="困难" value="hard" />
              </el-select>
            </el-space>
          </div>

          <el-table :data="filteredChallenges" v-loading="loading" border>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
            <el-table-column prop="category" label="分类" width="150" />
            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.type === 'choice'" type="info" size="small">选择题</el-tag>
                <el-tag v-else type="warning" size="small">靶场题</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="difficulty" label="难度" width="100">
              <template #default="{ row }">
                <el-tag :type="getDifficultyType(row.difficulty)" size="small">
                  {{ getDifficultyText(row.difficulty) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="points" label="分值" width="80" />
            <el-table-column label="技能标签" width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <el-tag v-for="(value, key) in row.skill_tags" :key="key" size="small" style="margin: 2px">
                  {{ key }}: {{ value }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editChallenge(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteChallenge(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-main>
    </el-container>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'add' ? '添加题目' : '编辑题目'"
      width="800px"
    >
      <el-form :model="form" label-width="120px" ref="formRef" :rules="rules">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入题目标题" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="题目描述(可选)" />
        </el-form-item>

        <el-form-item label="一级分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择一级分类" @change="handleCategoryChange">
            <el-option
              v-for="category in Object.keys(skillMatrix)"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="二级技能标签" prop="skillTag">
          <el-select v-model="form.skillTag" placeholder="请选择技能标签（仅限一个）">
            <el-option
              v-for="(code, skillName) in getSkillOptions()"
              :key="code"
              :label="`${skillName} (${code})`"
              :value="skillName"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio value="choice">选择题</el-radio>
            <el-radio value="docker">靶场题</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="难度" prop="difficulty">
          <el-select v-model="form.difficulty" placeholder="请选择难度">
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>

        <el-form-item label="分值" prop="points">
          <el-input-number v-model="form.points" :min="10" :max="1000" :step="10" />
        </el-form-item>

        <!-- 选择题特定字段 -->
        <template v-if="form.type === 'choice'">
          <el-form-item label="问题" prop="question">
            <el-input v-model="form.question" type="textarea" :rows="2" placeholder="请输入选择题问题" />
          </el-form-item>

          <el-form-item label="选项A" prop="optionA">
            <el-input v-model="form.optionA" placeholder="选项A内容" />
          </el-form-item>

          <el-form-item label="选项B" prop="optionB">
            <el-input v-model="form.optionB" placeholder="选项B内容" />
          </el-form-item>

          <el-form-item label="选项C" prop="optionC">
            <el-input v-model="form.optionC" placeholder="选项C内容" />
          </el-form-item>

          <el-form-item label="选项D" prop="optionD">
            <el-input v-model="form.optionD" placeholder="选项D内容" />
          </el-form-item>

          <el-form-item label="正确答案" prop="correct_answer">
            <el-radio-group v-model="form.correct_answer">
              <el-radio value="A">A</el-radio>
              <el-radio value="B">B</el-radio>
              <el-radio value="C">C</el-radio>
              <el-radio value="D">D</el-radio>
            </el-radio-group>
          </el-form-item>
        </template>

        <!-- 靶场题特定字段 -->
        <template v-if="form.type === 'docker'">
          <el-form-item label="镜像名称" prop="docker_image">
            <el-select
              v-model="form.docker_image"
              placeholder="请选择Docker镜像"
              filterable
              style="width: 100%"
              :loading="dockerImagesLoading"
            >
              <el-option
                v-for="image in dockerImages"
                :key="image.name"
                :label="`${image.name} (${image.size}MB)`"
                :value="image.name"
              >
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span>{{ image.name }}</span>
                  <span style="color: #8492a6; font-size: 13px;">{{ image.size }}MB</span>
                </div>
              </el-option>
            </el-select>
            <div class="form-help">从已构建的Docker镜像中选择</div>
          </el-form-item>

          <el-form-item label="容器端口" prop="docker_port">
            <el-input-number v-model="form.docker_port" :min="1" :max="65535" placeholder="如: 80" />
          </el-form-item>

          <el-form-item label="FLAG" prop="flag">
            <el-input v-model="form.flag" placeholder="如: FLAG{test_flag_123}" />
          </el-form-item>
        </template>
      </el-form>

      <template #footer>
        <el-space>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">
            {{ dialogMode === 'add' ? '添加' : '保存' }}
          </el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllChallenges, createChallenge, updateChallenge, deleteChallenge as deleteChallengeAPI, getDockerImages } from '@/api/admin'

// 技能标签矩阵
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
  name: 'AdminChallenges',
  setup() {
    const router = useRouter()
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const loading = ref(false)
    const challenges = ref([])
    const dialogVisible = ref(false)
    const dialogMode = ref('add')
    const submitLoading = ref(false)
    const formRef = ref(null)
    const skillMatrix = SKILL_MATRIX

    // Docker镜像相关
    const dockerImages = ref([])
    const dockerImagesLoading = ref(false)

    // 筛选器
    const filterCategory = ref('')
    const filterSkillTag = ref('')
    const filterType = ref('')
    const filterDifficulty = ref('')

    const form = reactive({
      id: null,
      title: '',
      description: '',
      category: '',
      skillTag: '',
      type: 'choice',
      difficulty: 'easy',
      points: 50,
      question: '',
      optionA: '',
      optionB: '',
      optionC: '',
      optionD: '',
      correct_answer: 'A',
      docker_image: '',
      docker_port: 80,
      flag: ''
    })

    const rules = {
      title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
      category: [{ required: true, message: '请选择分类', trigger: 'change' }],
      skillTag: [{ required: true, message: '请选择技能标签', trigger: 'change' }],
      type: [{ required: true, message: '请选择类型', trigger: 'change' }],
      difficulty: [{ required: true, message: '请选择难度', trigger: 'change' }],
      points: [{ required: true, message: '请输入分值', trigger: 'blur' }],
      // 选择题必填字段
      question: [{ required: true, message: '请输入问题', trigger: 'blur' }],
      optionA: [{ required: true, message: '请输入选项A', trigger: 'blur' }],
      optionB: [{ required: true, message: '请输入选项B', trigger: 'blur' }],
      optionC: [{ required: true, message: '请输入选项C', trigger: 'blur' }],
      optionD: [{ required: true, message: '请输入选项D', trigger: 'blur' }],
      correct_answer: [{ required: true, message: '请选择正确答案', trigger: 'change' }],
      // 靶场题必填字段
      docker_image: [{ required: true, message: '请输入镜像名称', trigger: 'blur' }],
      docker_port: [{ required: true, message: '请输入容器端口', trigger: 'blur' }],
      flag: [{ required: true, message: '请输入FLAG', trigger: 'blur' }]
    }

    const loadChallenges = async () => {
      loading.value = true
      try {
        challenges.value = await getAllChallenges()
      } finally {
        loading.value = false
      }
    }

    const loadDockerImages = async () => {
      dockerImagesLoading.value = true
      try {
        const response = await getDockerImages()
        dockerImages.value = response.images || []

        if (dockerImages.value.length === 0) {
          ElMessage.info('未找到已构建的Docker镜像，请先使用 docker-compose build 构建镜像')
        }
      } catch (error) {
        console.error('加载Docker镜像失败:', error)
        dockerImages.value = []
        ElMessage.warning('无法加载Docker镜像列表，请确保Docker服务正常运行并已构建镜像')
      } finally {
        dockerImagesLoading.value = false
      }
    }

    const getSkillOptions = () => {
      if (!form.category) return {}
      return skillMatrix[form.category] || {}
    }

    const getFilterSkillOptions = () => {
      if (!filterCategory.value) return {}
      return skillMatrix[filterCategory.value] || {}
    }

    const handleCategoryChange = () => {
      form.skillTag = ''
    }

    const handleFilterCategoryChange = () => {
      filterSkillTag.value = ''
    }

    // 筛选后的题目列表
    const filteredChallenges = computed(() => {
      let result = challenges.value

      if (filterCategory.value) {
        result = result.filter(c => c.category === filterCategory.value)
      }

      if (filterSkillTag.value) {
        result = result.filter(c => {
          if (!c.skill_tags) return false
          const skillNames = Object.values(c.skill_tags)
          return skillNames.includes(filterSkillTag.value)
        })
      }

      if (filterType.value) {
        result = result.filter(c => c.type === filterType.value)
      }

      if (filterDifficulty.value) {
        result = result.filter(c => c.difficulty === filterDifficulty.value)
      }

      return result
    })

    const showAddDialog = () => {
      dialogMode.value = 'add'
      resetForm()
      dialogVisible.value = true
      // 加载Docker镜像列表
      loadDockerImages()
    }

    const editChallenge = (challenge) => {
      dialogMode.value = 'edit'
      // 加载Docker镜像列表
      loadDockerImages()

      form.id = challenge.id
      form.title = challenge.title
      form.description = challenge.description
      form.category = challenge.category
      form.type = challenge.type
      form.difficulty = challenge.difficulty
      form.points = challenge.points
      form.question = challenge.question || ''
      form.correct_answer = challenge.correct_answer || 'A'
      form.docker_image = challenge.docker_image || ''
      form.docker_port = challenge.docker_port || 80
      form.flag = challenge.flag || ''

      // 解析技能标签 - 只取第一个
      if (challenge.skill_tags) {
        const skillNames = Object.values(challenge.skill_tags)
        form.skillTag = skillNames.length > 0 ? skillNames[0] : ''
      } else {
        form.skillTag = ''
      }

      // Parse options
      if (challenge.options) {
        form.optionA = challenge.options.A || ''
        form.optionB = challenge.options.B || ''
        form.optionC = challenge.options.C || ''
        form.optionD = challenge.options.D || ''
      }

      dialogVisible.value = true
    }

    const deleteChallenge = async (id) => {
      try {
        await ElMessageBox.confirm('确定要删除这个题目吗?', '警告', {
          type: 'warning',
          confirmButtonText: '确定',
          cancelButtonText: '取消'
        })

        await deleteChallengeAPI(id)
        ElMessage.success('删除成功')
        loadChallenges()
      } catch (error) {
        if (error !== 'cancel') {
          console.error(error)
        }
      }
    }

    const resetForm = () => {
      form.id = null
      form.title = ''
      form.description = ''
      form.category = ''
      form.skillTag = ''
      form.type = 'choice'
      form.difficulty = 'easy'
      form.points = 50
      form.question = ''
      form.optionA = ''
      form.optionB = ''
      form.optionC = ''
      form.optionD = ''
      form.correct_answer = 'A'
      form.docker_image = ''
      form.docker_port = 80
      form.flag = ''
    }

    const submitForm = async () => {
      try {
        await formRef.value.validate()

        submitLoading.value = true

        // 构建技能标签对象 {"技能代码": "技能名称"} - 只支持单个标签
        const skill_tags = {}
        if (form.skillTag) {
          const skillsInCategory = skillMatrix[form.category] || {}
          const code = skillsInCategory[form.skillTag]
          if (code) {
            skill_tags[code] = form.skillTag
          }
        }

        const data = {
          title: form.title,
          description: form.description,
          category: form.category,
          type: form.type,
          difficulty: form.difficulty,
          points: form.points,
          skill_tags: skill_tags
        }

        if (form.type === 'choice') {
          data.question = form.question
          data.options = {
            A: form.optionA,
            B: form.optionB,
            C: form.optionC,
            D: form.optionD
          }
          data.correct_answer = form.correct_answer
        } else {
          data.docker_image = form.docker_image
          data.docker_port = form.docker_port
          data.flag = form.flag
        }

        if (dialogMode.value === 'add') {
          await createChallenge(data)
          ElMessage.success('添加成功')
        } else {
          await updateChallenge(form.id, data)
          ElMessage.success('更新成功')
        }

        dialogVisible.value = false
        loadChallenges()
      } catch (error) {
        console.error(error)
        ElMessage.error('操作失败: ' + (error.response?.data?.error || error.message))
      } finally {
        submitLoading.value = false
      }
    }

    const getDifficultyType = (difficulty) => {
      const map = { easy: 'success', medium: 'warning', hard: 'danger' }
      return map[difficulty] || 'info'
    }

    const getDifficultyText = (difficulty) => {
      const map = { easy: '简单', medium: '中等', hard: '困难' }
      return map[difficulty] || difficulty
    }

    const handleMenuSelect = (index) => {
      if (index.startsWith('admin/')) {
        router.push(`/${index}`)
      } else if (index === 'admin') {
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

    return {
      user,
      loading,
      challenges,
      dialogVisible,
      dialogMode,
      submitLoading,
      formRef,
      form,
      rules,
      skillMatrix,
      dockerImages,
      dockerImagesLoading,
      filterCategory,
      filterSkillTag,
      filterType,
      filterDifficulty,
      filteredChallenges,
      loadChallenges,
      loadDockerImages,
      getSkillOptions,
      getFilterSkillOptions,
      handleCategoryChange,
      handleFilterCategoryChange,
      showAddDialog,
      editChallenge,
      deleteChallenge,
      submitForm,
      getDifficultyType,
      getDifficultyText,
      handleMenuSelect,
      handleLogout
    }
  }
}
</script>

<style scoped>
.admin-challenges-container {
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

:deep(.el-sub-menu__title) {
  color: rgba(255,255,255,0.65);
}

:deep(.el-sub-menu__title:hover) {
  color: #fff;
  background: rgba(255,255,255,0.1) !important;
}

:deep(.el-sub-menu.is-active .el-sub-menu__title) {
  color: #fff;
}

:deep(.el-sub-menu .el-menu-item) {
  background: #000c17 !important;
  min-width: 200px;
}

:deep(.el-sub-menu .el-menu-item span) {
  color: rgba(255,255,255,0.65) !important;
}

:deep(.el-sub-menu .el-menu-item .el-icon) {
  color: rgba(255,255,255,0.65) !important;
}

:deep(.el-sub-menu .el-menu-item:hover) {
  background: #001529 !important;
}

:deep(.el-sub-menu .el-menu-item:hover span) {
  color: #fff !important;
}

:deep(.el-sub-menu .el-menu-item:hover .el-icon) {
  color: #fff !important;
}

:deep(.el-sub-menu .el-menu-item.is-active) {
  background: #1890ff !important;
}

:deep(.el-sub-menu .el-menu-item.is-active span) {
  color: #fff !important;
}

:deep(.el-sub-menu .el-menu-item.is-active .el-icon) {
  color: #fff !important;
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

.form-help {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
