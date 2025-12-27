<template>
  <div class="admin-submissions-container">
    <el-container>
      <el-aside width="250px">
        <div class="logo">CyberPrism</div>
        <el-menu :default-active="'admin/submissions'" @select="handleMenuSelect">
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
              <h2>提交记录管理</h2>
              <el-space>
                <el-input
                  v-model="searchQuery"
                  placeholder="搜索用户名或题目"
                  clearable
                  style="width: 200px"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-select v-model="filterCorrect" placeholder="筛选状态" clearable style="width: 150px">
                  <el-option label="全部" value="" />
                  <el-option label="仅正确" value="true" />
                  <el-option label="仅错误" value="false" />
                </el-select>
                <el-button type="primary" @click="loadSubmissions">刷新</el-button>
              </el-space>
            </div>
          </template>

          <el-table :data="filteredSubmissions" v-loading="loading" border stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="display_name" label="姓名" width="120" />
            <el-table-column prop="challenge_title" label="题目" min-width="180" />
            <el-table-column prop="challenge_points" label="分数" width="80" align="center" />
            <el-table-column prop="is_correct" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.is_correct" type="success" size="small">正确</el-tag>
                <el-tag v-else type="danger" size="small">错误</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="submitted_at" label="提交时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.submitted_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right" align="center">
              <template #default="{ row }">
                <el-button
                  type="danger"
                  size="small"
                  @click="handleDelete(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-text type="info">
              共 {{ submissions.length }} 条记录，其中正确 {{ correctCount }} 条，错误 {{ incorrectCount }} 条
            </el-text>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllSubmissions, deleteSubmission } from '@/api/admin'

export default {
  name: 'AdminSubmissions',
  setup() {
    const router = useRouter()
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const loading = ref(false)
    const submissions = ref([])
    const searchQuery = ref('')
    const filterCorrect = ref('')

    const correctCount = computed(() => {
      return submissions.value.filter(s => s.is_correct).length
    })

    const incorrectCount = computed(() => {
      return submissions.value.filter(s => !s.is_correct).length
    })

    const filteredSubmissions = computed(() => {
      let result = submissions.value

      // 搜索过滤
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(sub =>
          sub.username.toLowerCase().includes(query) ||
          sub.display_name.toLowerCase().includes(query) ||
          sub.challenge_title.toLowerCase().includes(query)
        )
      }

      return result
    })

    const loadSubmissions = async () => {
      loading.value = true
      try {
        const params = {}
        if (filterCorrect.value) {
          params.is_correct = filterCorrect.value
        }
        const data = await getAllSubmissions(params)
        submissions.value = data
      } catch (error) {
        ElMessage.error('加载提交记录失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    const handleDelete = async (row) => {
      try {
        const message = row.is_correct
          ? `确定要删除用户 "${row.username}" 对题目 "${row.challenge_title}" 的正确提交记录吗？删除后将同步扣除该用户 ${row.challenge_points} 分。`
          : `确定要删除用户 "${row.username}" 对题目 "${row.challenge_title}" 的错误提交记录吗？`

        await ElMessageBox.confirm(
          message,
          '删除提交记录',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        const result = await deleteSubmission(row.id)
        ElMessage.success('提交记录已删除')

        // 显示更新后的用户分数（仅针对正确提交）
        if (row.is_correct && result.user) {
          ElMessage.info(`用户当前总分: ${result.user.total_points}，解题数: ${result.user.solved_count}`)
        }

        // 重新加载数据
        await loadSubmissions()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(error.response?.data?.error || '删除失败')
        }
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString('zh-CN')
    }

    const handleMenuSelect = (index) => {
      if (index === 'logout') return
      if (index.startsWith('admin/')) {
        router.push(`/${index}`)
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
      loadSubmissions()
    })

    return {
      user,
      loading,
      submissions,
      searchQuery,
      filterCorrect,
      correctCount,
      incorrectCount,
      filteredSubmissions,
      loadSubmissions,
      handleDelete,
      formatDate,
      handleMenuSelect,
      handleLogout
    }
  }
}
</script>

<style scoped>
.admin-submissions-container {
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
  color: #303133;
}

.pagination-container {
  margin-top: 20px;
  text-align: center;
}
</style>
