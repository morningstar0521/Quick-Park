const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    host: '127.0.0.1',
    port: 8080,
    client: {
      webSocketURL: 'ws://127.0.0.1:8080/ws'
    },
    // Local dev: forward API calls to Flask so the same relative URLs work everywhere
    proxy: {
      '/api': { target: 'http://127.0.0.1:5000', changeOrigin: true }
    }
  }
})
