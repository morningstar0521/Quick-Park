<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-card">
      <h3 class="modal-title">Occupied Parking Spot Details</h3>
      <p class="modal-subtitle">Current status and occupant information.</p>

      <div class="detail-grid">
        <div class="detail-row">
          <label>Spot ID:</label>
          <span class="detail-value text-info">{{ spot.spot_id }}</span>
        </div>

        <div class="detail-row">
          <label>Customer Name:</label>
          <span class="detail-value">{{ spot.customer_name }}</span>
        </div>

        <div class="detail-row">
          <label>Customer ID:</label>
          <span class="detail-value text-secondary">{{ spot.user_id }}</span>
        </div>

        <div class="detail-row">
          <label>Vehicle Number:</label>
          <span class="detail-value">{{ spot.vehicle_number }}</span>
        </div>
        
        <div class="detail-row">
          <label>Lot Name:</label>
          <span class="detail-value">{{ spot.lot_name }}</span>
        </div>

        <div class="detail-row">
          <label>Start Time:</label>
          <span class="detail-value">{{ formatDateTime(spot.start_time) }}</span>
        </div>
        
        <div class="detail-row">
          <label>Current Duration:</label>
          <span class="detail-value text-info">{{ spot.duration_hours ? spot.duration_hours.toFixed(2) + ' hours' : 'N/A' }}</span>
        </div>
        
        <div class="detail-row">
          <label>Rate per Hour:</label>
          <span class="detail-value">₹{{ spot.rate_per_hour }}/hour</span>
        </div>

        <div class="detail-row">
          <label>Current Cost:</label>
          <span class="detail-value text-success">₹{{ spot.spot_revenue ? spot.spot_revenue.toFixed(2) : '0.00' }}</span>
        </div>
        
      </div>

      <div class="modal-actions">
        <button class="btn btn-secondary-custom" @click="$emit('close')">Close</button>
        </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SpotDetailsModal',
  props: {
    spot: {
      type: Object,
      required: true,
      default: () => ({
        spot_id: 0,
        customer_name: 'N/A',
        user_id: 'N/A',
        vehicle_number: 'N/A',
        lot_name: 'N/A',
        start_time: 'N/A',
        estimated_end_time: 'N/A',
        estimated_cost: 0.00,
      })
    }
  },
  methods: {
    formatDateTime(dateTimeString) {
      if (!dateTimeString || dateTimeString === 'N/A') return 'N/A';
      return new Date(dateTimeString).toLocaleString('en-IN', {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
    }
  }
};
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7); 
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-card {
  width: 90%;
  max-width: 500px;
  padding: 30px;
  border-radius: 20px;
  text-align: left;
  background: rgba(255, 255, 255, 0.15); 
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  color: #fff;
  animation: modal-in 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.modal-title {
  font-weight: bold;
  font-size: 1.8rem;
  color: #00d4ff; 
  margin-bottom: 5px;
  border-bottom: 2px solid rgba(0, 212, 255, 0.5);
  padding-bottom: 10px;
}

.modal-subtitle {
  color: #b0b0b0;
  margin-bottom: 25px;
  font-size: 0.9rem;
}
.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.2);
  padding-bottom: 8px;
}

.detail-row label {
  font-weight: 500;
  color: #e0e0e0;
  font-size: 1rem;
}

.detail-value {
  font-weight: bold;
  font-size: 1.1rem;
  text-shadow: 0 0 5px rgba(0, 212, 255, 0.3);
}

.detail-value.text-secondary {
    color: #aaa !important;
}
.detail-value.text-warning {
    color: #ffc107 !important;
}
.detail-value.text-success {
    color: #28a745 !important;
}
.detail-value.text-info {
    color: #00d4ff !important;
}
.modal-actions {
  text-align: right;
}

.btn-secondary-custom {
  margin-top: 15px;
  border-radius: 25px;
  font-weight: bold;
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}
.btn-secondary-custom:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}
@keyframes modal-in {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
</style>