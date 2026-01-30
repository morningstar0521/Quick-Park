<template>
  <div class="parking-lot-form-container">
    <div class="form-card">
      <h3 class="form-title">{{ isEditing ? 'Edit Parking Lot' : 'Add New Parking Lot' }}</h3>
      <p class="form-subtitle">
        {{ isEditing ? 'Update the details for this existing facility.' : 'Enter the complete information for the new parking facility.' }}
      </p>

      <form @submit.prevent="submitForm">
        
        <div class="row mb-3">
          <div :class="['col-md-6', {'col-md-12': !isEditing}]">
            <label for="lotName" class="form-label">Lot Name</label>
            <input type="text" class="form-control" id="lotName" v-model="form.name" required>
          </div>
          <div class="col-md-6" v-if="isEditing">
            <label for="lotId" class="form-label">Lot ID</label>
            <input type="text" class="form-control" id="lotId" :value="form.id" disabled>
          </div>
        </div>

        <div class="row mb-3">
          <div class="col-md-6">
            <label for="address" class="form-label">Address (Street & Place)</label>
            <input type="text" class="form-control" id="address" v-model="form.address" required>
          </div>
          <div class="col-md-3">
            <label for="city" class="form-label">City</label>
            <input type="text" class="form-control" id="city" v-model="form.city" required>
          </div>
          <div class="col-md-3">
            <label for="pincode" class="form-label">Pincode/Zip Code</label>
            <input type="text" class="form-control" id="pincode" v-model="form.pincode" pattern="\d{4,9}" title="Pincode must be 4-9 digits" required>
          </div>
        </div>

        <div class="row mb-4">
          <div class="col-md-4">
            <label for="parkingType" class="form-label">Parking Type</label>
            <select class="form-select" id="parkingType" v-model="form.parkingType" required>
              <option value="" disabled>Select Type</option>
              <option value="Mall">Mall / Shopping Complex</option>
              <option value="Commercial">Commercial Building / Office</option>
              <option value="Residential">Residential Complex / Apartment</option>
              <option value="Public">Public / Street Parking</option>
              <option value="Event">Event Venue / Stadium</option>
            </select>
          </div>
          
          <div class="col-md-4">
            <label for="totalSpots" class="form-label">Total Spots</label>
            <input type="number" class="form-control" id="totalSpots" v-model.number="form.totalSpots" min="1" required>
          </div>
          <div class="col-md-4">
            <label for="ratePerHour" class="form-label">Rate / Hour (₹)</label> 
            <input type="number" class="form-control" id="ratePerHour" v-model.number="form.ratePerHour" min="0" step="0.01" required>
          </div>
        </div>
        
        <div class="row mb-4">
          <div class="col-md-4">
            <label for="status" class="form-label">Status</label>
            <select class="form-select" id="status" v-model="form.status" required>
              <option value="Active">Active</option>
              <option value="Maintenance">Maintenance</option>
              <option value="Deactivated">Deactivated</option>
            </select>
            <small v-if="isEditing && form.status !== initialLot.status && form.status !== 'Active'" class="warning-text">
              ⚠️ Status can only be changed to {{ form.status }} if all parking spots are empty.
            </small>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn btn-secondary-custom me-3" @click="$emit('cancel')">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary-custom">
            <i class="fas fa-save me-2"></i> {{ isEditing ? 'Save Changes' : 'Create Lot' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ParkingLotForm',
  inject: ["emitter"], 
  props: {
    initialLot: {
      type: Object,
      default: () => ({
        id: null,
        name: '', 
        address: '', 
        city: '', 
        pincode: '', 
        parkingType: '', 
        totalSpots: 0, 
        ratePerHour: 0.00, 
        status: 'Active',
      }),
    },
  },
  data() {
    return {
      form: { 
        ...this.initialLot,
      }, 
      isEditing: !!this.initialLot.id,
    };
  },
  methods: {
    async submitForm() {
      try {
        const payload = {
          id: this.form.id,
          name: this.form.name,
          address: this.form.address,
          city: this.form.city,
          pincode: String(this.form.pincode).trim(),
          parkingType: this.form.parkingType,
          totalSpots: Number(this.form.totalSpots),
          ratePerHour: Number(this.form.ratePerHour),
          status: this.form.status,
        };

        let response;
        if (this.isEditing) {
          response = await this.$axios.put(
            `http://127.0.0.1:5000/api/parking-lots/${this.form.id}`,
            payload
          );
        } else {
          response = await this.$axios.post(
            "http://127.0.0.1:5000/api/parking-lots",
            payload
          );
        }
        this.emitter.emit("parkingLotAdded");
        this.$emit('lot-saved'); 
        this.$emit('switchView', 'ManageParkingLots');

      } catch (err) {
        console.error("Error saving parking lot:", err);
        const errorMsg = err.response?.data?.message || "Failed to save parking lot. Please check server status.";
        alert(errorMsg);
        if (err.response?.status === 401 || err.response?.status === 403) {
            this.$emit('switchView', 'Home'); 
        }
      }
    },
  },
};
</script>

<style scoped>
.parking-lot-form-container {
  width: 100%;
  max-width: 900px; 
  margin: 0 auto;
  padding: 20px;
}
.form-card {
  background: rgba(255, 255, 255, 0.1); 
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
  text-align: left;
}
.form-title {
  font-weight: bold;
  color: #00d4ff; 
  font-size: 1.8rem;
  margin-bottom: 5px;
  text-shadow: 0 0 8px rgba(0,212,255,0.5);
}
.form-subtitle {
  color: #b0b0b0;
  margin-bottom: 25px;
}
.form-label {
  color: #e0e0e0;
  font-weight: 500;
  margin-bottom: 5px;
  display: block;
}
.form-control,
.form-select {
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.3); 
  color: #fff;
  padding: 10px 15px;
  transition: all 0.3s ease;
}
.form-control:focus,
.form-select:focus {
  background-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 0 0.25rem rgba(0, 212, 255, 0.5); 
  border-color: #00d4ff;
  color: #fff;
}
.form-select option {
  background-color: #212529; 
  color: #fff;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 30px;
}
.btn-primary-custom {
  background: #00d4ff; 
  color: #111;
  border: none;
  border-radius: 25px;
  font-weight: bold;
  padding: 10px 25px;
  transition: all 0.3s ease;
}
.btn-primary-custom:hover {
  background: #00a0cc;
  transform: translateY(-2px);
}
.btn-secondary-custom {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  font-weight: bold;
  padding: 10px 25px;
  transition: all 0.3s ease;
}
.btn-secondary-custom:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}
.warning-text {
  color: #ffa500;
  font-weight: 600;
  margin-top: 5px;
  display: block;
}
</style>