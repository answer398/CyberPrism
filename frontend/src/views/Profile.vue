<template>
  <div class="profile-container">
    <el-container>
      <el-aside width="250px">
        <div class="logo">CyberPrism</div>
        <el-menu :default-active="activeMenu" @select="handleMenuSelect">
          <el-menu-item index="dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>个人中心</span>
          </el-menu-item>
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
          <el-menu-item @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main>
        <el-card>
          <template #header>
            <div class="card-header">
              <h2>个人资料</h2>
            </div>
          </template>

          <div v-loading="loading">
            <!-- 用户信息 -->
            <el-descriptions :column="2" border>
              <el-descriptions-item label="用户名">{{ profileData.user?.username }}</el-descriptions-item>
              <el-descriptions-item label="邮箱">{{ profileData.user?.email }}</el-descriptions-item>
              <el-descriptions-item label="姓名">{{ profileData.user?.display_name }}</el-descriptions-item>
              <el-descriptions-item label="常用ID">{{ profileData.user?.common_id || '-' }}</el-descriptions-item>
              <el-descriptions-item label="注册时间">{{ formatDate(profileData.user?.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="用户类型">
                <el-tag v-if="profileData.user?.is_admin" type="danger">管理员</el-tag>
                <el-tag v-else>普通用户</el-tag>
              </el-descriptions-item>
            </el-descriptions>

            <!-- 统计信息 -->
            <div class="stats-container">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-card shadow="hover">
                    <div class="stat-item">
                      <div class="stat-value">{{ profileData.stats?.total_submissions || 0 }}</div>
                      <div class="stat-label">总提交数</div>
                    </div>
                  </el-card>
                </el-col>
                <el-col :span="8">
                  <el-card shadow="hover">
                    <div class="stat-item">
                      <div class="stat-value">{{ profileData.stats?.correct_submissions || 0 }}</div>
                      <div class="stat-label">正确解答</div>
                    </div>
                  </el-card>
                </el-col>
                <el-col :span="8">
                  <el-card shadow="hover">
                    <div class="stat-item">
                      <div class="stat-value">{{ profileData.stats?.skills_unlocked || 0 }}</div>
                      <div class="stat-label">技能解锁</div>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>

            <!-- 能力矩阵图 -->
            <el-card style="margin-top: 20px">
              <template #header>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <h3>能力矩阵</h3>
                  <div style="display: flex; gap: 15px; font-size: 12px; align-items: center;">
                    <span>攻击完成技术: <strong style="color: #409EFF;">{{ attackTechCount }}</strong></span>
                    <span>已完成技能数: <strong style="color: #67C23A;">{{ completedSkillCount }}</strong></span>
                  </div>
                </div>
              </template>

              <div v-if="Object.keys(profileData.skills_matrix || {}).length === 0">
                <el-empty description="暂无数据,快去挑战题目吧!" />
              </div>
              <div v-else class="matrix-container">
                <!-- 遍历每个类别 -->
                <div v-for="(categoryData, category) in profileData.skills_matrix" :key="category" class="category-section">
                  <div class="category-header">
                    <h4>{{ category }}</h4>
                    <el-tag :type="categoryData.completion_rate >= 60 ? 'success' : 'info'" size="small">
                      {{ categoryData.completed }}/{{ categoryData.total }} ({{ categoryData.completion_rate }}%)
                    </el-tag>
                  </div>

                  <!-- 技能卡片网格 -->
                  <div class="skills-grid">
                    <div
                      v-for="skill in categoryData.skills"
                      :key="skill.skill_code"
                      class="skill-card"
                      :class="{
                        'skill-mastered': skill.mastered,
                        'skill-learning': skill.completion_rate > 0 && !skill.mastered,
                        'skill-locked': skill.completion_rate === 0
                      }"
                    >
                      <div class="skill-code">{{ skill.skill_code }}</div>
                      <div class="skill-name">{{ skill.skill_name }}</div>
                      <div class="skill-progress">
                        <div class="progress-bar" :style="{ width: skill.completion_rate + '%' }"></div>
                      </div>
                      <div class="skill-stats">{{ skill.completed }}/{{ skill.total }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>

            <!-- 技能标签列表 -->
            <el-card style="margin-top: 20px">
              <template #header>
                <h3>技能完成度</h3>
              </template>
              <div v-if="Object.keys(profileData.skills_matrix || {}).length === 0">
                <el-empty description="暂无数据,快去挑战题目吧!" />
              </div>
              <div v-else>
                <div v-for="(categoryData, category) in profileData.skills_matrix" :key="category" style="margin-bottom: 30px">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px">
                    <h4 style="margin: 0">{{ category }}</h4>
                    <el-tag :type="categoryData.completion_rate >= 60 ? 'success' : 'info'">
                      {{ categoryData.completed }}/{{ categoryData.total }} ({{ categoryData.completion_rate }}%)
                    </el-tag>
                  </div>
                  <el-progress
                    :percentage="categoryData.completion_rate"
                    :color="getProgressColor(categoryData.completion_rate)"
                    :stroke-width="20"
                    style="margin-bottom: 15px"
                  />
                  <div style="display: flex; flex-wrap: wrap; gap: 10px">
                    <el-tooltip
                      v-for="skill in categoryData.skills"
                      :key="skill.skill_code"
                      :content="`${skill.completed}/${skill.total} 题 (${skill.completion_rate}%)`"
                      placement="top"
                    >
                      <el-tag
                        :type="skill.mastered ? 'success' : skill.completion_rate > 0 ? 'warning' : 'info'"
                        :effect="skill.mastered ? 'dark' : 'plain'"
                        size="large"
                      >
                        <span style="font-weight: bold">{{ skill.skill_code }}</span>: {{ skill.skill_name }}
                        <el-progress
                          :percentage="skill.completion_rate"
                          :show-text="false"
                          :stroke-width="3"
                          :color="getProgressColor(skill.completion_rate)"
                          style="margin-top: 5px; width: 100%"
                        />
                      </el-tag>
                    </el-tooltip>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getUserProfile } from '@/api/user'

export default {
  name: 'Profile',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const profileData = ref({})
    const activeMenu = ref('profile')

    const user = JSON.parse(localStorage.getItem('user') || '{}')

    // 计算攻击完成技术总数
    const attackTechCount = computed(() => {
      const matrix = profileData.value.skills_matrix || {}
      let total = 0
      Object.values(matrix).forEach(categoryData => {
        total += categoryData.skills?.length || 0
      })
      return total
    })

    // 计算已完成的技能数
    const completedSkillCount = computed(() => {
      return profileData.value.stats?.skills_unlocked || 0
    })

    const loadProfile = async () => {
      loading.value = true
      try {
        const data = await getUserProfile()
        profileData.value = data
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    const getProgressColor = (percentage) => {
      if (percentage >= 80) return '#2e7d32'
      if (percentage >= 60) return '#4caf50'
      if (percentage >= 40) return '#8bc34a'
      if (percentage >= 20) return '#ffeb3b'
      return '#e0e0e0'
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleString('zh-CN')
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
      loadProfile()
    })

    return {
      loading,
      profileData,
      activeMenu,
      user,
      attackTechCount,
      completedSkillCount,
      formatDate,
      handleMenuSelect,
      handleLogout,
      getProgressColor
    }
  }
}
</script>

<style scoped>
.profile-container {
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

.card-header h2 {
  margin: 0;
  color: #303133;
}

.stats-container {
  margin-top: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  margin-top: 10px;
  color: #909399;
  font-size: 14px;
}

/* 能力矩阵样式 */
.matrix-container {
  padding: 10px 0;
}

.category-section {
  margin-bottom: 30px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409EFF;
}

.category-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.skill-card {
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.skill-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 已掌握的技能 - 蓝色 */
.skill-mastered {
  background: #409EFF;
  border-color: #409EFF;
  color: #fff;
}

.skill-mastered .skill-code,
.skill-mastered .skill-name,
.skill-mastered .skill-stats {
  color: #fff;
}

.skill-mastered .progress-bar {
  background: rgba(255, 255, 255, 0.9);
}

/* 学习中的技能 - 橙色 */
.skill-learning {
  background: #E6A23C;
  border-color: #E6A23C;
  color: #fff;
}

.skill-learning .skill-code,
.skill-learning .skill-name,
.skill-learning .skill-stats {
  color: #fff;
}

.skill-learning .progress-bar {
  background: rgba(255, 255, 255, 0.9);
}

/* 未开始的技能 - 灰色 */
.skill-locked {
  background: #f5f7fa;
  border-color: #e4e7ed;
}

.skill-code {
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 6px;
  font-family: 'Courier New', monospace;
}

.skill-name {
  font-size: 13px;
  margin-bottom: 8px;
  line-height: 1.4;
  min-height: 36px;
}

.skill-progress {
  width: 100%;
  height: 4px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 6px;
}

.progress-bar {
  height: 100%;
  background: #409EFF;
  transition: width 0.3s ease;
}

.skill-stats {
  font-size: 11px;
  text-align: right;
  opacity: 0.8;
}
</style>
