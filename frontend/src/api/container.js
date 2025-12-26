import request from './request'

// 启动容器
export const startContainer = (challengeId) => {
  return request.post(`/containers/start/${challengeId}`)
}

// 停止容器
export const stopContainer = (instanceId) => {
  return request.post(`/containers/${instanceId}/stop`)
}

// 延长容器时间
export const extendContainer = (instanceId, minutes) => {
  return request.post(`/containers/${instanceId}/extend`, { minutes })
}

// 获取我的容器
export const getMyContainers = () => {
  return request.get('/containers/my')
}

// 获取容器信息
export const getContainerInfo = (instanceId) => {
  return request.get(`/containers/${instanceId}`)
}
