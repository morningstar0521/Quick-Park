<template>
  <div class="user-profile">
    <nav class="user-navbar">
      <div class="navbar-content">
        <div class="navbar-brand">
          <span>Quick Park</span>
        </div>
        <div class="navbar-menu">
          <a class="nav-item" @click="$emit('switchView','UserDashboard')">
            <i class="fas fa-home me-2"></i>Dashboard
          </a>
          <a class="nav-item" @click="$emit('switchView','BookParking')">
            <i class="fas fa-car me-2"></i>Book Parking
          </a>
          <a class="nav-item" @click="$emit('switchView','UserBookingHistory')">
            <i class="fas fa-history me-2"></i>History
          </a>
          <a class="nav-item" @click="$emit('switchView','UserReports')">
            <i class="fas fa-chart-bar me-2"></i>Reports
          </a>
        </div>
        <div class="navbar-user">
          <span class="user-name"><i class="fas fa-user-circle me-2"></i>{{ userDetails.full_name || 'User' }}</span>
          <button class="btn-logout" @click="logout">
            <i class="fas fa-sign-out-alt me-1"></i>Logout
          </button>
        </div>
      </div>
    </nav>
    <div class="profile-wrapper">
      <div class="overlay"></div>
      
      <div class="profile-main">
        <div v-if="!isEditingProfile" class="profile-view-container">
          <div class="profile-card">
            <div class="profile-card-header">
              <img :src="avatarUrl" alt="User Avatar" class="profile-avatar">
              <div class="profile-header-info">
                <h3 class="profile-full-name">{{ userDetails.full_name || 'User' }}</h3>
                <p class="profile-user-email">{{ userDetails.email }}</p>
                <span class="profile-status-badge">
                  <i class="fas fa-check-circle me-1"></i>Active Member
                </span>
              </div>
            </div>

            <div class="profile-card-body">
              <div class="info-group">
                <h4 class="info-group-title">
                  <i class="fas fa-user-circle me-2"></i>Personal Information
                </h4>
                <div class="info-row">
                  <div class="info-col">
                    <span class="info-label"><i class="fas fa-user"></i> Full Name</span>
                    <span class="info-value">{{ userDetails.full_name || 'Not provided' }}</span>
                  </div>
                  <div class="info-col">
                    <span class="info-label"><i class="fas fa-envelope"></i> Email Address</span>
                    <span class="info-value">{{ userDetails.email }}</span>
                  </div>
                </div>
              </div>
              <div class="info-group">
                <h4 class="info-group-title">
                  <i class="fas fa-map-marker-alt me-2"></i>Location Information
                </h4>
                <div class="info-row">
                  <div class="info-col full-width">
                    <span class="info-label"><i class="fas fa-home"></i> Address</span>
                    <span class="info-value">{{ userDetails.address || 'Not provided' }}</span>
                  </div>
                </div>
              </div>
              <div class="info-group">
                <h4 class="info-group-title">
                  <i class="fas fa-info-circle me-2"></i>Account Information
                </h4>
                <div class="info-row">
                  <div class="info-col">
                    <span class="info-label"><i class="fas fa-calendar-alt"></i> Member Since</span>
                    <span class="info-value">{{ formatDate(userDetails.created_at) }}</span>
                  </div>
                  <div class="info-col">
                    <span class="info-label"><i class="fas fa-id-badge"></i> User ID</span>
                    <span class="info-value">{{ userDetails.id || 'N/A' }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="profile-card-footer">
              <button class="btn-primary" @click="editProfile">
                <i class="fas fa-edit me-2"></i>Edit Profile
              </button>
              <button class="btn-secondary" @click="goBack">
                <i class="fas fa-arrow-left me-2"></i>Back
              </button>
            </div>
          </div>
        </div>
        <div v-else class="profile-edit-container">
          <div class="profile-edit-card">
            <div class="edit-card-header">
              <h3>Update Your Information</h3>
              <p>Modify your profile details and select a new avatar</p>
            </div>
            <div class="avatar-editor-section">
              <div class="avatar-display">
                <img :src="avatarUrl" :alt="selectedAvatarStyle" class="avatar-large">
                <button class="btn-avatar-edit" @click="showAvatarSelector = !showAvatarSelector" :class="{ active: showAvatarSelector }">
                  <i class="fas fa-camera"></i>
                </button>
              </div>
              <div v-if="showAvatarSelector" class="avatar-gallery">
                <h5 class="gallery-title">Select Your Car Avatar</h5>
                <div class="car-avatars-grid">
                  <div
                    v-for="car in luxuryCarAvatars"
                    :key="car.value"
                    class="avatar-item"
                    :class="{ selected: selectedAvatarStyle === car.value }"
                    @click="selectLuxuryCarAvatar(car)"
                  >
                    <img :src="car.image" :alt="car.name" class="avatar-car-image">
                    <div class="avatar-item-info">
                      <span class="car-name">{{ car.name }}</span>
                      <span class="car-desc">{{ car.description }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-fields-section">
              <div class="form-field">
                <label for="fullName" class="field-label">
                  <i class="fas fa-user me-2"></i>Full Name
                </label>
                <input
                  id="fullName"
                  v-model="editDetails.full_name"
                  type="text"
                  class="field-input"
                  placeholder="Enter your full name"
                />
              </div>
              <div class="form-field">
                <label class="field-label">
                  <i class="fas fa-envelope me-2"></i>Email Address
                </label>
                <input
                  :value="userDetails.email"
                  type="email"
                  class="field-input"
                  disabled
                  placeholder="Email (read-only)"
                />
                <p class="field-note">Email cannot be changed</p>
              </div>
              <div class="form-field full-width">
                <label for="address" class="field-label">
                  <i class="fas fa-home me-2"></i>Address
                </label>
                <textarea
                  id="address"
                  v-model="editDetails.address"
                  class="field-textarea"
                  placeholder="Enter your address"
                ></textarea>
              </div>
            </div>
            <div class="edit-card-footer">
              <button class="btn-save" @click="saveProfile">
                <i class="fas fa-check me-2"></i>Save Changes
              </button>
              <button class="btn-cancel" @click="cancelEdit">
                <i class="fas fa-times me-2"></i>Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "UserProfile",
  props: {
    userDetails: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      isEditingProfile: false,
      editDetails: {},
      avatarUrl: 'https://images.pexels.com/photos/3764984/pexels-photo-3764984.jpeg',
      showAvatarSelector: false,
      selectedAvatarStyle: 'luxury-sedan',
      selectedAvatarForSave: null,
      luxuryCarAvatars: [
        { 
          name: 'Luxury Sedan', 
          value: 'luxury-sedan', 
          image: 'https://images.pexels.com/photos/3764984/pexels-photo-3764984.jpeg',
          description: 'Elegant luxury sedan'
        },
        { 
          name: 'Premium Coupe', 
          value: 'premium-coupe', 
          image: 'https://images.unsplash.com/photo-1614200179396-2bdb77ebf81b?fm=jpg&q=60&w=3000&ixlib=rb-4.0.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bHV4dXJ5JTIwY2FyfGVufDB8fDB8fHww',
          description: 'High-end sports coupe'
        },
        { 
          name: 'BMW i7', 
          value: 'bmw-i7', 
          image: 'https://www.goodwood.com/globalassets/.road--racing/road/news/2020/6-june/list-dan-trent-luxury-cars-2020/bmw-i7-2600.jpg?rxy=0.5,0.5',
          description: 'Luxury electric sedan'
        },
        { 
          name: 'Exotic Sports', 
          value: 'exotic-sports', 
          image: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRUCgFKHRCHJDFSwroFljHUbVESoFajXdMnPg&s',
          description: 'Exotic sports car'
        },
        { 
          name: 'Modern Luxury', 
          value: 'modern-luxury', 
          image: 'https://imgc.ap7am.com/bimg/cr-2024081866c184b878237.jpg',
          description: 'Contemporary luxury vehicle'
        }
      ]
    };
  },
  mounted() {
    if (this.userDetails && this.userDetails.avatar_url) {
      this.avatarUrl = this.userDetails.avatar_url;
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    editProfile() {
      this.isEditingProfile = true;
      this.editDetails = { ...this.userDetails };
      this.selectedAvatarForSave = this.avatarUrl;
    },
    selectLuxuryCarAvatar(car) {
      this.selectedAvatarStyle = car.value;
      this.avatarUrl = car.image;
      this.selectedAvatarForSave = car.image;
      this.showAvatarSelector = false;
    },
    async saveProfile() {
      try {
        const payload = {
          full_name: this.editDetails.full_name,
          address: this.editDetails.address,
          avatar_url: this.selectedAvatarForSave || this.avatarUrl
        };
        
        const res = await this.$axios.put(
          "http://127.0.0.1:5000/api/user/profile",
          payload
        );

        if (res.data.ok) {
          Object.assign(this.userDetails, res.data.user);
          if (res.data.user.avatar_url) {
            this.avatarUrl = res.data.user.avatar_url;
          }
          this.isEditingProfile = false;
          alert("Profile updated successfully!");
        } else {
          alert(`Profile update failed: ${res.data.message}`);
        }
      } catch (err) {
        console.error("Error updating profile:", err);
        if (err.response && err.response.status === 401) {
          this.logout(true);
        } else {
          alert("Failed to update profile. Please try again.");
        }
      }
    },
    cancelEdit() {
      this.isEditingProfile = false;
      this.editDetails = {};
      this.selectedAvatarForSave = null;
      if (this.userDetails.avatar_url) {
        this.avatarUrl = this.userDetails.avatar_url;
      }
    },
    goBack() {
      this.$emit('switchView', 'UserDashboard');
    },
    logout() {
      localStorage.removeItem('accessToken');
      this.$emit('switchView', 'Home');
    }
  }
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.user-profile {
  position: relative;
  min-height: 100vh;
  background: url("@/assets/user-bg.jpg") no-repeat center center;
  background-size: cover;
  background-attachment: fixed;
  display: flex;
  flex-direction: column;
}

.user-navbar {
  background: linear-gradient(135deg, #1a252f 0%, #2c3e50 50%, #3498db 100%);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  padding: 16px 0;
  position: relative;
  z-index: 100;
  border-bottom: 1px solid rgba(52, 152, 219, 0.2);
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 30px;
  width: 100%;
}

.navbar-brand {
  display: flex;
  align-items: center;
  font-size: 1.6rem;
  font-weight: 800;
  color: white;
  text-decoration: none;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  letter-spacing: -0.5px;
}

.navbar-menu {
  display: flex;
  gap: 35px;
  align-items: center;
  flex: 1;
  margin-left: 60px;
}

.nav-item {
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 10px 14px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  font-size: 0.95rem;
  position: relative;
}

.nav-item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: #ffffff;
  transition: width 0.3s ease;
  border-radius: 1px;
}

.nav-item:hover::after,
.nav-item.active::after {
  width: 100%;
}

.nav-item:hover,
.nav-item.active {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.15);
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-left: auto;
}

.user-name {
  color: white;
  font-weight: 600;
  display: flex;
  align-items: center;
  font-size: 0.95rem;
}

.btn-logout {
  background: linear-gradient(135deg, #dc3545, #c82333);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-logout:hover {
  background: linear-gradient(135deg, #c82333, #bd2130);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(220, 53, 69, 0.4);
}
.profile-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 40px 20px;
  overflow-y: auto;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.55);
  z-index: 1;
  backdrop-filter: blur(2px);
}

.profile-main {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
}

.profile-view-container,
.profile-edit-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
}
.profile-card,
.profile-edit-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.profile-card:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.15);
}
.profile-card-header {
  padding: 40px;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(155, 89, 182, 0.1));
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 30px;
}

.profile-avatar {
  width: 140px;
  height: 140px;
  border-radius: 12px;
  object-fit: cover;
  border: 3px solid rgba(52, 152, 219, 0.5);
  box-shadow: 0 12px 32px rgba(52, 152, 219, 0.2);
  flex-shrink: 0;
}

.profile-header-info {
  flex: 1;
}

.profile-full-name {
  font-size: 28px;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 8px 0;
}

.profile-user-email {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 12px 0;
}

.profile-status-badge {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.2), rgba(39, 174, 96, 0.2));
  border: 1px solid rgba(46, 204, 113, 0.5);
  border-radius: 8px;
  color: #2ecc71;
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.profile-card-body {
  padding: 40px;
}

.info-group {
  margin-bottom: 30px;
}

.info-group:last-child {
  margin-bottom: 0;
}

.info-group-title {
  font-size: 15px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-group-title i {
  color: #3498db;
  font-size: 16px;
}

.info-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
}

.info-col {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-col.full-width {
  grid-column: 1 / -1;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-label i {
  color: #3498db;
  font-size: 15px;
}

.info-value {
  font-size: 16px;
  font-weight: 500;
  color: #ffffff;
  word-break: break-word;
}
.profile-card-footer {
  padding: 25px 40px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary {
  padding: 12px 28px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 180px;
  justify-content: center;
}

.btn-primary {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #2980b9, #1f618d);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(52, 152, 219, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
}
.profile-edit-card {
  padding: 0;
}

.edit-card-header {
  padding: 40px;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(155, 89, 182, 0.1));
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.edit-card-header h3 {
  font-size: 28px;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 8px 0;
}

.edit-card-header p {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}
.avatar-editor-section {
  padding: 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.avatar-display {
  position: relative;
  width: 160px;
  height: 160px;
  margin: 0 auto 30px;
}

.avatar-large {
  width: 100%;
  height: 100%;
  border-radius: 12px;
  object-fit: cover;
  border: 3px solid rgba(52, 152, 219, 0.5);
  box-shadow: 0 12px 32px rgba(52, 152, 219, 0.2);
}

.btn-avatar-edit {
  position: absolute;
  bottom: -10px;
  right: -10px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3498db, #2980b9);
  border: 3px solid rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(52, 152, 219, 0.4);
}

.btn-avatar-edit:hover,
.btn-avatar-edit.active {
  transform: scale(1.1);
  box-shadow: 0 12px 28px rgba(52, 152, 219, 0.5);
}

.avatar-gallery {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 25px;
}

.gallery-title {
  font-size: 15px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 20px 0;
  text-align: center;
}

.car-avatars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 15px;
}

.avatar-item {
  cursor: pointer;
  border-radius: 10px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
  padding: 12px;
  transition: all 0.3s ease;
  text-align: center;
  overflow: hidden;
}

.avatar-item:hover {
  border-color: rgba(52, 152, 219, 0.5);
  background: rgba(52, 152, 219, 0.1);
}

.avatar-item.selected {
  border-color: #3498db;
  background: rgba(52, 152, 219, 0.2);
  box-shadow: 0 0 20px rgba(52, 152, 219, 0.3);
}

.avatar-car-image {
  width: 100%;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 10px;
}

.avatar-item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.car-name {
  font-size: 13px;
  font-weight: 700;
  color: #ffffff;
}

.car-desc {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}
.form-fields-section {
  padding: 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.form-field {
  margin-bottom: 25px;
}

.form-field.full-width {
  grid-column: 1 / -1;
}

.form-field:last-child {
  margin-bottom: 0;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

.field-label i {
  color: #3498db;
  font-size: 15px;
}

.field-input,
.field-textarea {
  width: 100%;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: #ffffff;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.3s ease;
}

.field-input::placeholder,
.field-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.field-input:focus,
.field-textarea:focus {
  border-color: #3498db;
  background: rgba(52, 152, 219, 0.1);
  outline: none;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.field-input:disabled {
  background: rgba(0, 0, 0, 0.2);
  color: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
}

.field-textarea {
  resize: vertical;
  min-height: 120px;
}

.field-note {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 6px 0 0 0;
}
.edit-card-footer {
  padding: 25px 40px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.btn-save,
.btn-cancel {
  padding: 12px 28px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 180px;
  justify-content: center;
}

.btn-save {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
}

.btn-save:hover:not(:disabled) {
  background: linear-gradient(135deg, #27ae60, #229954);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(46, 204, 113, 0.4);
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
}
@media (max-width: 768px) {
  .navbar-menu {
    gap: 20px;
    margin-left: 30px;
  }

  .navbar-content {
    padding: 0 15px;
    flex-wrap: wrap;
  }

  .profile-card-header,
  .edit-card-header,
  .avatar-editor-section,
  .form-fields-section {
    padding: 25px;
  }

  .profile-avatar {
    width: 100px;
    height: 100px;
  }

  .avatar-large {
    width: 120px;
    height: 120px;
  }

  .profile-full-name {
    font-size: 22px;
  }

  .info-row {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .profile-card-footer,
  .edit-card-footer {
    flex-direction: column;
    padding: 20px 25px;
  }

  .btn-primary,
  .btn-secondary,
  .btn-save,
  .btn-cancel {
    width: 100%;
    min-width: auto;
  }

  .car-avatars-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .avatar-display {
    width: 120px;
    height: 120px;
  }

  .btn-avatar-edit {
    width: 48px;
    height: 48px;
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .profile-wrapper {
    padding: 20px 10px;
  }

  .navbar-brand {
    font-size: 1.3rem;
  }

  .navbar-menu {
    gap: 15px;
    margin-left: 15px;
    font-size: 0.85rem;
  }

  .profile-full-name {
    font-size: 20px;
  }

  .car-avatars-grid {
    grid-template-columns: 1fr;
  }

  .edit-card-header h3 {
    font-size: 22px;
  }
}
</style>
