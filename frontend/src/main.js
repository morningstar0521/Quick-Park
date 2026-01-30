import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap";
import axios from "axios";

axios.defaults.baseURL = "http://127.0.0.1:5000"; 
const token = localStorage.getItem('accessToken');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

const app = createApp(App);
app.use(router);

app.config.globalProperties.$axios = axios;

app.mount("#app");