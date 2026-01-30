<template>
  <div class="auth-page d-flex justify-content-center align-items-center">
    <div class="overlay"></div>

    <div class="auth-box d-flex shadow-lg rounded">
      <div class="auth-left text-center p-4 d-flex flex-column justify-content-center align-items-center">
        <img src="@/assets/logo.png" alt="Quick Park Logo" class="logo mb-3" />
        <h2 class="brand-name">Quick Park</h2>
        <p class="text-white fw-light">Welcome back! Please login to your account</p>
      </div>

      <div class="auth-right flex-fill p-5 d-flex flex-column justify-content-center">
        <h4 class="mb-4 fw-bold text-center">Login</h4>
        <form @submit.prevent="login">
          <div class="mb-3 input-group">
            <span class="input-icon"><i class="fas fa-envelope"></i></span>
            <input type="email" v-model="email" class="form-control modern-input input-field" placeholder="Email" required />
          </div>
          <div class="mb-3 input-group">
            <span class="input-icon"><i class="fas fa-lock"></i></span>
            <input type="password" v-model="password" class="form-control modern-input input-field" placeholder="Password" required />
          </div>
          <div class="d-flex justify-content-between align-items-center mb-4">
            <div></div>
            <a href="#" class="text-primary text-decoration-none fw-bold" @click.prevent="$emit('switchView','ForgotPassword')">Forgot Password?</a>
          </div>
          <button type="submit" class="btn btn-primary w-100 btn-lg btn-modern">Login</button>
        </form>
        <p class="mt-4 text-center text-muted">
          Don't have an account? 
          <a href="#" class="text-primary text-decoration-none fw-bold" @click="$emit('switchView','Register')">Register</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return { email: "", password: ""};
  },
  methods: {
    async login() {
      try {
        const loginRes = await axios.post(
          "http://127.0.0.1:5000/api/login",
          {
            email: this.email, 
            password: this.password,
          },
        );

        if (loginRes.data.ok && loginRes.data.token) {
          const token = loginRes.data.token;
          const role = loginRes.data.user.role;
          
          localStorage.setItem('accessToken', token);
          
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

          console.log("Login successful. Token stored and headers set.");

          this.$emit("loginSuccess", { 
              role: role.toLowerCase(),
              initialData: loginRes.data 
          });
          
        } else {
          alert(loginRes.data.message || "Login failed");
        }
      } catch (err) {
        console.error("Login error:", err.response || err);
        const errorMsg = err.response?.data?.message || "Invalid credentials or server error";
        alert(errorMsg);
      }
    },
  },
};
</script>

<style scoped>
.auth-page {
  position: relative;
  height: calc(100vh - 56px); 
  width: 100%;
  background: url("@/assets/car-bg.jpg") no-repeat center center/cover;
}
.overlay {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(30, 40, 50, 0.8); 
  z-index: 1;
}


.auth-box {
  background: rgba(255,255,255,0.95);
  color: #222;
  max-width: 900px;
  width: 100%;
  position: relative;
  z-index: 2;
  border-radius: 15px;
  overflow: hidden; 
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.auth-left {
  flex: 1;
  background: linear-gradient(135deg, #2c3e50, #3498db); 
  color: white;
  border-right: none; 
  padding: 40px; 
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.logo {
  max-width: 120px; 
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2)); 
}
.brand-name {
  font-weight: bold;
  font-size: 2.2rem; 
  color: #fff; 
  text-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.auth-left p {
  font-size: 1.1rem;
  margin-top: 10px;
}

.auth-right {
  flex: 1.5;
  padding: 50px; 
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.auth-right h4 {
    color: #007bff; 
    margin-bottom: 30px;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 20px; 
}
.input-icon {
  position: absolute;
  left: 15px;
  color: #a0a0a0;
  font-size: 1rem;
  z-index: 3; 
}
.input-field {
  padding-left: 45px; 
  border-radius: 10px;
  padding: 12px 15px 12px 45px; 
  font-size: 1rem;
  border: 1px solid #ddd;
  transition: all 0.3s ease;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
}
.input-field::placeholder {
  color: #b0b0b0;
}
.input-field:focus {
  border-color: #007bff; 
  box-shadow: 0px 0px 8px rgba(0,123,255,0.4), inset 0 1px 3px rgba(0,0,0,0.05);
  outline: none;
}
.input-group:focus-within .input-icon {
  color: #007bff; 
}

.btn-modern {
  border-radius: 30px;
  font-weight: bold;
  padding: 12px 25px;
  font-size: 1.1rem;
  background-color: #007bff; 
  border-color: #007bff;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(0,123,255,0.2);
}
.btn-modern:hover {
  background-color: #0056b3; 
  border-color: #0056b3;
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0,123,255,0.3);
}

.auth-right p a {
  color: #007bff; 
  transition: color 0.3s ease;
}
.auth-right p a:hover {
  color: #0056b3;
  text-decoration: underline !important;
}

@media (max-width: 768px) {
  .auth-box {
    flex-direction: column;
    max-width: 500px;
  }
  .auth-left {
    border-right: none;
    border-bottom: 1px solid rgba(255,255,255,0.2);
    border-radius: 15px 15px 0 0;
  }
  .auth-right {
    padding: 30px;
  }
}
</style>