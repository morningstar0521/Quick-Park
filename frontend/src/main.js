import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap";
import axios from "axios";

// Relative URLs: in production Caddy serves the app and proxies /api to Flask.
// In local dev, vue.config.js proxies /api to http://127.0.0.1:5000.
axios.defaults.baseURL = process.env.VUE_APP_API_URL || ""; 
const token = localStorage.getItem('accessToken');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

const app = createApp(App);
app.use(router);

app.config.globalProperties.$axios = axios;

app.mount("#app");