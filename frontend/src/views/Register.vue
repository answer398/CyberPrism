<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>用户注册</h2>
          <p>创建你的CyberPrism账号</p>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="registerForm" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item label="姓名" prop="display_name">
          <el-input v-model="form.display_name" placeholder="请输入真实姓名" />
        </el-form-item>

        <el-form-item label="常用ID" prop="common_id">
          <el-input v-model="form.common_id" placeholder="请输入常用ID(选填)" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading" style="width: 100%">
            注册
          </el-button>
        </el-form-item>

        <el-form-item>
          <router-link to="/login">已有账号?立即登录</router-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '@/api/user'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const registerForm = ref(null)
    const loading = ref(false)

    const form = ref({
      username: '',
      email: '',
      display_name: '',
      common_id: '',
      password: '',
      confirmPassword: ''
    })

    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else if (value.length < 6) {
        callback(new Error('密码至少6位'))
      } else {
        callback()
      }
    }

    const validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== form.value.password) {
        callback(new Error('两次输入密码不一致'))
      } else {
        callback()
      }
    }

    const rules = {
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      display_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
      password: [{ validator: validatePass, trigger: 'blur' }],
      confirmPassword: [{ validator: validatePass2, trigger: 'blur' }]
    }

    const handleRegister = () => {
      registerForm.value.validate(async (valid) => {
        if (!valid) return

        loading.value = true
        try {
          const { confirmPassword, ...data } = form.value
          const res = await register(data)

          localStorage.setItem('token', res.access_token)
          localStorage.setItem('user', JSON.stringify(res.user))

          ElMessage.success('注册成功!')
          router.push('/dashboard')
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
      registerForm,
      loading,
      handleRegister
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
  width: 500px;
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
