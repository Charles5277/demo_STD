import { boot } from 'quasar/wrappers'
import axios from 'axios'

// Create the default axios instance
const defaultApi = axios.create({ baseURL: 'https://api.example.com' })

// Create the custom axios instance with your desired configuration
const api = axios.create({
  baseURL: '/api/',
  timeout: 3000,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

export default boot(({ app }) => {
  // Set the default axios instance to the globalProperties
  app.config.globalProperties.$axios = defaultApi

  // Set the custom api instance to the globalProperties
  app.config.globalProperties.$api = api

  // Provide the api object
  app.provide('api', api)
})

export { defaultApi as axios, api }
