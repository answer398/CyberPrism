<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>CyberPrism</h2>
          <p>CTF能力评估平台</p>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="loginForm" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" style="width: 100%">
            登录
          </el-button>
        </el-form-item>

        <el-form-item>
          <router-link to="/register">还没有账号?立即注册</router-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/api/user'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const loginForm = ref(null)
    const loading = ref(false)

    const form = ref({
      username: '',
      password: ''
    })

    const rules = {
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
    }

    const handleLogin = () => {
      loginForm.value.validate(async (valid) => {
        if (!valid) return

        loading.value = true
        try {
          const res = await login(form.value)
          localStorage.setItem('token', res.access_token)
          localStorage.setItem('user', JSON.stringify(res.user))

          ElMessage.success('登录成功!')

          // 判断是否是管理员
          if (res.user.is_admin) {
            router.push('/admin')
          } else {
            router.push('/dashboard')
          }
        } catch (error) {
          console.error(error)
        } finally {
          loading.value = false
        }
      })
    }

    return {
      form,
      rules,
      loginForm,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 450px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #409eff;
  font-size: 28px;
}

.card-header p {
  margin: 5px 0 0;
  color: #909399;
  font-size: 14px;
}
</style>
