<template>
  <div class="receipt-container">
    <div class="top-bar">
      <button class="btn btn-back" @click="goBack">
        <i class="fas fa-arrow-left"></i> Back to Dashboard
      </button>
      <div class="top-bar-actions">
        <button class="btn btn-download" @click="downloadPDF">
          <i class="fas fa-download"></i> Download as PDF
        </button>
      </div>
    </div>

    <div class="receipt-content" id="receipt-content">
      <div class="receipt-header">
        <div class="receipt-divider">═══════════════════════════════════════</div>
        <h1 class="receipt-title">🧾 QUICK PARK - PARKING RECEIPT 🧾</h1>
        <div class="receipt-divider">═══════════════════════════════════════</div>
      </div>

      <div class="receipt-body">
        <div class="receipt-section">
          <h3 class="section-title">📋 BOOKING DETAILS:</h3>
          <div class="detail-row">
            <span class="detail-label">• Booking ID:</span>
            <span class="detail-value">{{ receipt.booking_id }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">• Customer:</span>
            <span class="detail-value">{{ receipt.customer_name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">• Customer ID:</span>
            <span class="detail-value">{{ receipt.customer_id }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">• Vehicle:</span>
            <span class="detail-value">{{ receipt.vehicle_number }}</span>
          </div>
        </div>

        <div class="receipt-section">
          <h3 class="section-title">📍 LOCATION DETAILS:</h3>
          <div class="detail-row">
            <span class="detail-label">• Location:</span>
            <span class="detail-value">{{ receipt.lot_name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">• Spot Number:</span>
            <span class="detail-value">#{{ receipt.spot_id }}</span>
          </div>
        </div>

        <div class="receipt-section">
          <h3 class="section-title">⏰ TIME DETAILS:</h3>
          <div class="detail-row">
            <span class="detail-label">• Start Time:</span>
            <span class="detail-value">{{ formatDateTime(receipt.start_time) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">• End Time:</span>
            <span class="detail-value">{{ receipt.end_time ? formatDateTime(receipt.end_time) : 'N/A' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">• Total Duration:</span>
            <span class="detail-value">{{ receipt.duration_hours ? receipt.duration_hours.toFixed(2) + ' hours (' + Math.round(receipt.duration_hours * 60) + ' minutes)' : 'N/A' }}</span>
          </div>
          <div class="detail-row" v-if="receipt.end_time">
            <span class="detail-label">• Hours Charged:</span>
            <span class="detail-value">{{ Math.ceil(receipt.duration_hours || 0) }} hours (rounded up)</span>
          </div>
        </div>

        <div class="receipt-section">
          <h3 class="section-title">💰 PAYMENT DETAILS:</h3>
          <div class="detail-row">
            <span class="detail-label">• Rate:</span>
            <span class="detail-value">₹{{ receipt.rate_per_hour }}/hour</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">• Total Amount:</span>
            <span class="detail-value amount-highlight">₹{{ receipt.amount_paid ? receipt.amount_paid.toFixed(2) : '0.00' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">• Status:</span>
            <span class="detail-value status-badge" :class="{ 'active': receipt.status === 'Active', 'completed': receipt.status === 'Completed' }">
              {{ receipt.status }}
            </span>
          </div>
        </div>
      </div>

      <div class="receipt-footer">
        <div class="receipt-divider">═══════════════════════════════════════</div>
        <p class="thank-you">Thank you for using Quick Park! 🚗</p>
        <div class="receipt-divider">═══════════════════════════════════════</div>
      </div>
    </div>
  </div>
</template>

<script>
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

export default {
  name: 'ReceiptView',
  data() {
    return {
      receipt: {
        booking_id: '',
        customer_name: '',
        customer_id: '',
        vehicle_number: '',
        lot_name: '',
        spot_id: '',
        start_time: '',
        end_time: '',
        duration_hours: 0,
        rate_per_hour: 0,
        amount_paid: 0,
        status: ''
      }
    };
  },
  created() {
    this.loadReceiptData();
  },
  methods: {
    async loadReceiptData() {
      try {
        const bookingId = this.$route.query.bookingId;
        if (!bookingId) {
          alert('No booking ID provided');
          this.goBack();
          return;
        }

        const token = localStorage.getItem('accessToken');
        const response = await this.$axios.get(`http://127.0.0.1:5000/api/user/bookings/${bookingId}/receipt`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.data.ok) {
          this.receipt = response.data.receipt;
        } else {
          alert(`Error loading receipt: ${response.data.message}`);
          this.goBack();
        }
      } catch (err) {
        console.error("Error loading receipt:", err);
        alert("Failed to load receipt data");
        this.goBack();
      }
    },

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
    },

    async downloadPDF() {
      try {
        const element = document.getElementById('receipt-content');
        const clone = element.cloneNode(true);
        document.body.appendChild(clone);
        clone.style.background = '#ffffff';
        clone.style.color = '#000000';
        clone.style.width = element.offsetWidth + 'px';
        clone.style.padding = '20px';
        clone.style.position = 'absolute';
        clone.style.left = '-9999px';
        const textElements = clone.querySelectorAll('*');
        textElements.forEach(el => {
          el.style.color = '#000000';
          el.style.backgroundColor = 'transparent';
          el.style.textShadow = 'none';
          el.style.boxShadow = 'none';
        });
        const canvas = await html2canvas(clone, {
          scale: 2,
          useCORS: true,
          allowTaint: true,
          backgroundColor: '#ffffff',
          logging: true,
          imageTimeout: 0,
          removeContainer: false,
          foreignObjectRendering: false
        });
        
        document.body.removeChild(clone);

        const imgData = canvas.toDataURL('image/png', 1.0);
        const pdf = new jsPDF('p', 'mm', 'a4');
        
        const imgWidth = 210; 
        const pageHeight = 295; 
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        let heightLeft = imgHeight;

        let position = 0;

        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;

        while (heightLeft >= 0) {
          position = heightLeft - imgHeight;
          pdf.addPage();
          pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
          heightLeft -= pageHeight;
        }

        const fileName = `QuickPark_Receipt_${this.receipt.booking_id}_${new Date().toISOString().split('T')[0]}.pdf`;
        pdf.save(fileName);
      } catch (err) {
        console.error("Error generating PDF:", err);
        alert("Failed to generate PDF. Please try again.");
      }
    },

    goBack() {
      window.close();
    }
  }
};
</script>

<style scoped>
.receipt-container {
  background-image: url('@/assets/user-bg.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  min-height: 100vh;
  position: relative;
}

.receipt-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.receipt-content {
  background: white;
  margin: 2rem auto;
  padding: 3rem;
  max-width: 800px;
  border-radius: 15px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
  font-family: 'Courier New', monospace;
  position: relative;
  z-index: 2;
}

.top-bar {
  position: relative;
  z-index: 3;
  background: rgba(0, 0, 0, 0.8);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(10px);
}

.btn-back {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 0.8rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.btn-download {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-download:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
}

.top-bar-actions {
  display: flex;
  gap: 1rem;
}

.receipt-header {
  text-align: center;
  margin-bottom: 2rem;
}

.receipt-title {
  font-size: 1.8rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.receipt-divider {
  font-size: 1.2rem;
  color: #6c757d;
  margin: 1rem 0;
}

.receipt-body {
  margin: 2rem 0;
}

.receipt-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 0.5rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  padding: 0.25rem 0;
}

.detail-label {
  font-weight: 500;
  color: #495057;
}

.detail-value {
  font-weight: 600;
  color: #2c3e50;
}

.amount-highlight {
  color: #28a745;
  font-size: 1.1rem;
  font-weight: bold;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.completed {
  background: #cce5ff;
  color: #004085;
}

.receipt-footer {
  text-align: center;
  margin-top: 2rem;
}

.thank-you {
  font-size: 1.1rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 1rem 0;
}

/* Button Styles */
.btn-success-custom {
  background: linear-gradient(135deg, #51cf66, #40c057);
  border: none;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-success-custom:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(81, 207, 102, 0.3);
}

@media (max-width: 768px) {
  .receipt-content {
    margin: 1rem;
    padding: 2rem;
  }
  
  .receipt-title {
    font-size: 1.4rem;
  }
  
  .detail-row {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .detail-label {
    font-weight: 600;
  }
}
</style>
