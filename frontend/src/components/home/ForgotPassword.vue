<template>
  <div class="auth-page d-flex justify-content-center align-items-center">
    <div class="overlay"></div>

    <div class="auth-box d-flex shadow-lg rounded">
      
      <div class="auth-left text-center p-4 d-flex flex-column justify-content-center align-items-center">
        <img src="@/assets/logo.png" alt="Quick Park Logo" class="logo mb-3" />
        <h2 class="brand-name">Quick Park</h2>
        <p class="text-white fw-light">Don't worry, we'll help you get back in.</p>
      </div>

      <div class="auth-right flex-fill p-5 d-flex flex-column justify-content-center">
        <h4 class="mb-4 fw-bold text-center">Forgot Password</h4>
        <form v-if="step === 'email'" @submit.prevent="sendOtp">
          <p class="text-muted text-center mb-4">Enter your email address to receive a 6-digit OTP.</p>
          <div v-if="message" class="mb-3">
            <div :class="`alert ${error ? 'alert-danger' : 'alert-success'}`">{{ message }}</div>
          </div>
          <div class="mb-3 input-group">
            <span class="input-icon"><i class="fas fa-envelope"></i></span>
            <input type="email" v-model="email" class="form-control modern-input input-field" placeholder="Email" :disabled="loading" />
          </div>
          <button type="submit" class="btn btn-primary w-100 btn-lg btn-modern mt-3" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Send OTP
          </button>
        </form>

        <form v-else-if="step === 'verify'" @submit.prevent="verifyOtp">
          <p class="text-muted text-center mb-2">We've sent a 6-digit OTP to <b>{{ email }}</b>.</p>
          <p class="text-muted text-center mb-3">Enter the code below to verify and reset your password.</p>
          <div v-if="message" class="mb-3">
            <div :class="`alert ${error ? 'alert-danger' : 'alert-success'}`">{{ message }}</div>
          </div>
          <div class="mb-3 input-group">
            <span class="input-icon"><i class="fas fa-key"></i></span>
            <input type="text" v-model="otp" maxlength="6" class="form-control modern-input input-field" placeholder="Enter 6-digit OTP" :disabled="loading" />
          </div>
          <div class="d-flex gap-2">
            <button type="submit" class="btn btn-primary flex-fill btn-lg btn-modern" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Verify OTP
            </button>
            <button type="button" class="btn btn-outline-secondary flex-fill btn-lg" @click="resendOtp" :disabled="loading || resendDisabled">
              <span v-if="resendLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              <span v-if="resendDisabled">Resend ({{ resendTimer }})</span>
              <span v-else>Resend OTP</span>
            </button>
          </div>
          <p class="mt-3 text-center"><a href="#" @click.prevent="backToEmail">Edit Email</a></p>
        </form>
        <p class="mt-4 text-center text-muted">
          Remembered your password? 
          <a href="#" class="text-primary text-decoration-none fw-bold" @click="$emit('switchView','Login')">Login</a>
        </p>
        <p class="text-center text-muted">
          Need an account? 
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
    return {
      step: 'email', // 'email' or 'verify'
      email: '',
      otp: '',
      loading: false,
      resendLoading: false,
      resendDisabled: false,
      resendTimer: 0,
      message: '',
      error: false
    };
  },
  methods: {
    validateEmail(email) {
      const re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\\.,;:\s@\"]+\.)+[^<>()[\]\\.,;:\s@\"]{2,})$/i;
      return re.test(String(email).toLowerCase());
    },

    async sendOtp() {
      this.message = '';
      this.error = false;

      if (!this.email || !this.validateEmail(this.email)) {
        this.error = true;
        this.message = 'Please enter a valid email address.';
        return;
      }

      this.loading = true;
      try {
        const res = await axios.post('/api/auth/send-otp', { email: this.email });

        if (res.data && res.data.ok && res.data.userExists) {
          // Email exists - show success message and move to verify step
          this.message = res.data.message || 'OTP sent successfully. Check your inbox.';
          this.error = false;
          this.step = 'verify';
          // Persist email so ResetPassword can read it
          sessionStorage.setItem('reset_email', this.email);
          // Start resend timer
          this.startResendTimer();
        } else if (!res.data.userExists || res.status === 404) {
          // Email does not exist - show error and stay on email step
          this.error = true;
          this.message = res.data.message || 'This email does not exist. Please register first.';
          this.step = 'email'; // Keep on email step
        } else {
          this.error = true;
          this.message = res.data.message || 'Failed to send OTP.';
        }
      } catch (err) {
        console.error('sendOtp error', err);
        
        // Check if it's a 404 error (user not found)
        if (err.response && err.response.status === 404) {
          this.error = true;
          this.message = (err.response.data && err.response.data.message) || 'This email does not exist in our database. Please register first.';
          this.step = 'email'; // Keep on email step
        } else {
          this.error = true;
          this.message = (err.response && err.response.data && err.response.data.message) || 'Error sending OTP. Please try again.';
        }
      } finally {
        this.loading = false;
      }
    },

    async verifyOtp() {
      this.message = '';
      this.error = false;

      if (!this.otp || String(this.otp).trim().length !== 6) {
        this.error = true;
        this.message = 'Please enter the 6-digit OTP.';
        return;
      }

      this.loading = true;
      try {
        const res = await axios.post('/api/auth/verify-otp', { email: this.email, otp: this.otp });
        if (res.data && res.data.ok) {
          // Backend may issue a reset token for a secure reset endpoint
          if (res.data.resetToken) {
            sessionStorage.setItem('reset_token', res.data.resetToken);
          }
          // Ensure email is persisted
          sessionStorage.setItem('reset_email', this.email);
          // Clear sensitive local fields
          this.otp = '';
          this.message = 'OTP verified. Redirecting to reset password...';
          // Emit to parent to switch to ResetPassword view
          setTimeout(() => {
            this.$emit('switchView', 'ResetPassword');
          }, 700);
        } else {
          this.error = true;
          this.message = res.data.message || 'Invalid or expired OTP.';
        }
      } catch (err) {
        console.error('verifyOtp error', err);
        this.error = true;
        this.message = (err.response && err.response.data && err.response.data.message) || 'Error verifying OTP.';
      } finally {
        this.loading = false;
      }
    },

    async resendOtp() {
      if (this.resendDisabled) return;
      this.resendLoading = true;
      try {
        const res = await axios.post('/api/auth/send-otp', { email: this.email });
        if (res.data && res.data.ok) {
          this.message = 'OTP resent. Please check your inbox.';
          this.error = false;
          this.startResendTimer();
        } else {
          this.error = true;
          this.message = res.data.message || 'Failed to resend OTP.';
        }
      } catch (err) {
        console.error('resendOtp error', err);
        this.error = true;
        this.message = (err.response && err.response.data && err.response.data.message) || 'Error resending OTP.';
      } finally {
        this.resendLoading = false;
      }
    },

    backToEmail() {
      this.step = 'email';
      this.otp = '';
      this.message = '';
      this.error = false;
    },

    startResendTimer() {
      // disable resend for 30 seconds
      this.resendDisabled = true;
      this.resendTimer = 30;
      const interval = setInterval(() => {
        this.resendTimer -= 1;
        if (this.resendTimer <= 0) {
          clearInterval(interval);
          this.resendDisabled = false;
        }
      }, 1000);
    }
  },
};
</script>
<style scoped>

/* All styles are the same as Login/Register, so you can share them. */
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