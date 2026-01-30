<template>
  <div class="auth-page d-flex justify-content-center align-items-center">
    <div class="overlay"></div>

    <div class="auth-box d-flex shadow-lg rounded">
      
      <div class="auth-left text-center p-4 d-flex flex-column justify-content-center align-items-center">
        <img src="@/assets/logo.png" alt="Quick Park Logo" class="logo mb-3" />
        <h2 class="brand-name">Quick Park</h2>
        <p class="text-white fw-light">Set your new password to regain access.</p>
      </div>

      <div class="auth-right flex-fill p-5 d-flex flex-column justify-content-center">
        <h4 class="mb-4 fw-bold text-center">Reset Password</h4>
        <form @submit.prevent="resetPassword">
          <p class="text-muted text-center mb-2">Resetting password for <strong>{{ email || 'your account' }}</strong></p>
          <div v-if="message" class="mb-3">
            <div :class="`alert ${error ? 'alert-danger' : 'alert-success'}`">{{ message }}</div>
          </div>
          <div class="mb-3 input-group">
            <span class="input-icon"><i class="fas fa-lock"></i></span>
            <input type="password" v-model="password" class="form-control modern-input input-field" placeholder="New Password" :disabled="loading" />
          </div>
          <div class="mb-3 input-group">
            <span class="input-icon"><i class="fas fa-lock"></i></span>
            <input type="password" v-model="confirmPassword" class="form-control modern-input input-field" placeholder="Confirm Password" :disabled="loading" />
          </div>
          <button type="submit" class="btn btn-primary w-100 btn-lg btn-modern mt-3" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Reset Password
          </button>
        </form>
        <p class="mt-4 text-center text-muted">
          Remember your password? 
          <a href="#" class="text-primary text-decoration-none fw-bold" @click="$emit('switchView','Login')">Login</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return { 
      password: "",
      confirmPassword: "",
      token: "",
      email: '',
      loading: false,
      message: '',
      error: false
    };
  },
  props: {
    token: {
      type: String,
      default: ''
    }
  },
  created() {
    
    if (this.token) {
    }

    
    const storedEmail = sessionStorage.getItem('reset_email');
    const storedToken = sessionStorage.getItem('reset_token');
    if (storedEmail) {
      this.email = storedEmail;
    }
    if (!this.token && storedToken) {
      this.token = storedToken;
    }

    if (!this.email && !this.token) {
      this.message = 'No reset session found. Please request a new OTP.';
      this.error = true;
      setTimeout(() => this.$emit('switchView', 'ForgotPassword'), 1200);
    }
  },
  methods: {
    async resetPassword() {
      this.message = '';
      this.error = false;

      if (this.password !== this.confirmPassword) {
        this.error = true;
        this.message = 'Passwords do not match.';
        return;
      }

      if (!this.password || this.password.length < 6) {
        this.error = true;
        this.message = 'Password must be at least 6 characters.';
        return;
      }

      this.loading = true;
      try {
        const payload = { password: this.password };
        if (this.token) payload.token = this.token;
        if (this.email) payload.email = this.email;

        const res = await axios.post('/api/auth/reset-password', payload);

        if (res.data && res.data.ok) {
          this.message = 'Password reset successful! Redirecting to login...';
          this.error = false;
          sessionStorage.removeItem('reset_email');
          sessionStorage.removeItem('reset_token');
          setTimeout(() => {
            this.$emit('switchView', 'Login');
          }, 900);
        } else {
          this.error = true;
          this.message = res.data.message || 'Failed to reset password.';
        }
      } catch (err) {
        console.error('resetPassword error', err);
        this.error = true;
        this.message = (err.response && err.response.data && err.response.data.message) || 'Error resetting password. Token may be invalid or expired.';
      } finally {
        this.loading = false;
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

.brand-name {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
}

.logo {
  width: 80px;
  height: auto;
}

.auth-right {
  flex: 1.5;
  padding: 40px;
}

.input-group {
  position: relative;
  margin-bottom: 20px;
}

.input-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #aaa;
  z-index: 10;
}

.input-field {
  padding-left: 40px;
  height: 50px;
  border-radius: 25px;
  border: 1px solid #ddd;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.input-field:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.btn-modern {
  height: 50px;
  border-radius: 25px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.btn-modern:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
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