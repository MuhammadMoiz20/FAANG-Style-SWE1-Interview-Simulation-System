import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// API methods
export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

export const startPipeline = async (candidateId: number, jobProfileId: number) => {
  const response = await api.post('/pipeline/start', {
    candidate_id: candidateId,
    job_profile_id: jobProfileId,
  })
  return response.data
}

export const getPipeline = async (pipelineId: number) => {
  const response = await api.get(`/pipeline/${pipelineId}`)
  return response.data
}

export default api
