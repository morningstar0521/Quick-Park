<template>
  <div class="user-reports-container">
    <div class="top-bar">
      <button class="btn btn-back" @click="$emit('switchView', 'UserDashboard')">
        <i class="fas fa-arrow-left"></i> Back to Dashboard
      </button>
      <div class="top-bar-actions">
        <button class="btn btn-download" @click="downloadCSV">
          <i class="fas fa-file-csv"></i> Download CSV
        </button>
        <button class="btn btn-download" @click="downloadPDF">
          <i class="fas fa-file-pdf"></i> Download PDF
        </button>
      </div>
    </div>

    <div class="dashboard-content">
      <div class="reports-header">
        <h2 class="section-title">
          <i class="fas fa-chart-bar"></i> Your Parking Reports
        </h2>
        <p class="section-subtitle">Comprehensive insights into your parking history and spending patterns</p>
      </div>

      <div class="summary-cards">
        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-parking"></i>
          </div>
          <div class="card-content">
            <h3>{{ userStats.totalBookings }}</h3>
            <p>Total Bookings</p>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-rupee-sign"></i>
          </div>
          <div class="card-content">
            <h3>₹{{ userStats.totalSpent.toFixed(0) }}</h3>
            <p>Total Spent</p>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="card-content">
            <h3>{{ userStats.totalHours.toFixed(1) }}</h3>
            <p>Total Hours</p>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-star"></i>
          </div>
          <div class="card-content">
            <h3>{{ userStats.favoriteSpot }}</h3>
            <p>Favorite Spot</p>
          </div>
        </div>
      </div>

      <div class="charts-section">
        <div class="chart-container">
          <h3 class="chart-title">
            <i class="fas fa-chart-bar"></i> Bookings per Spot
          </h3>
          <canvas ref="bookingsChart" width="400" height="200"></canvas>
        </div>

        <div class="chart-container">
          <h3 class="chart-title">
            <i class="fas fa-chart-pie"></i> Spending Distribution
          </h3>
          <canvas ref="spendingChart" width="400" height="200"></canvas>
        </div>

        <div class="chart-container full-width">
          <h3 class="chart-title">
            <i class="fas fa-chart-line"></i> Spending Trend Over Time
          </h3>
          <canvas ref="trendChart" width="800" height="200"></canvas>
        </div>
      </div>

      <div class="recent-bookings">
        <h3 class="table-title">
          <i class="fas fa-history"></i> Recent Bookings
        </h3>
        <div class="table-container">
          <table class="bookings-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Location</th>
                <th>Spot</th>
                <th>Duration</th>
                <th>Cost</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="booking in recentBookings" :key="booking.id">
                <td>{{ formatDate(booking.start_time) }}</td>
                <td>{{ booking.lot_name }}</td>
                <td>#{{ booking.spot_number }}</td>
                <td>{{ booking.duration_hours }}h</td>
                <td>₹{{ booking.total_cost }}</td>
                <td>
                  <span class="status-badge" :class="booking.status.toLowerCase()">
                    {{ booking.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: "UserReports",
  props: {
    userDetails: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      userStats: {
        totalBookings: 0,
        totalSpent: 0,
        totalHours: 0,
        favoriteSpot: 'N/A'
      },
      bookingsData: [],
      recentBookings: [],
      charts: {}
    };
  },
  mounted() {
    this.$nextTick(() => {
      this.initializeEmptyCharts();
      this.fetchUserReports();
    });
  },
  methods: {
    initializeEmptyCharts() {
      if (this.$refs.bookingsChart) {
        const ctx = this.$refs.bookingsChart.getContext('2d');
        if (ctx) {
          this.charts.bookings = new Chart(ctx, {
            type: 'bar',
            data: { labels: [], datasets: [{ data: [] }] },
            options: { responsive: true, maintainAspectRatio: false }
          });
        }
      }
      
      if (this.$refs.spendingChart) {
        const ctx = this.$refs.spendingChart.getContext('2d');
        if (ctx) {
          this.charts.spending = new Chart(ctx, {
            type: 'pie',
            data: { labels: [], datasets: [{ data: [] }] },
            options: { responsive: true, maintainAspectRatio: false }
          });
        }
      }
      
      if (this.$refs.trendChart) {
        const ctx = this.$refs.trendChart.getContext('2d');
        if (ctx) {
          this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: { labels: [], datasets: [{ data: [] }] },
            options: { responsive: true, maintainAspectRatio: false }
          });
        }
      }
    },
    async fetchUserReports() {
      try {
        const response = await this.$axios.get("http://127.0.0.1:5000/api/user/reports");
        if (response.data.ok) {
          this.userStats = response.data.stats;
          this.bookingsData = response.data.bookings || [];
          this.recentBookings = response.data.recent_bookings || [];
          setTimeout(() => {
            this.renderCharts();
          }, 500);
        }
      } catch (err) {
        console.error("Error fetching user reports:", err);
      }
    },

    async renderCharts() {
      Object.values(this.charts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
          chart.destroy();
        }
      });
      this.charts = {};

      try {
        if (this.$refs.bookingsChart) await this.renderBookingsChart();
        if (this.$refs.spendingChart) await this.renderSpendingChart();
        if (this.$refs.trendChart) await this.renderTrendChart();
      } catch (err) {
        console.error("Error rendering charts:", err);
      }
    },

    renderBookingsChart() {
      if (!this.$refs.bookingsChart) {
        console.warn("Bookings chart element not found");
        return;
      }
      
      const canvas = this.$refs.bookingsChart;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        console.warn("Could not get 2D context for bookings chart");
        return;
      }
      
      const rect = canvas.parentElement.getBoundingClientRect();
      canvas.width = rect.width || 400;
      canvas.height = 300;
      const spotBookings = {};
      this.bookingsData.forEach(booking => {
        const spotKey = `${booking.lot_name} - Spot #${booking.spot_number}`;
        spotBookings[spotKey] = (spotBookings[spotKey] || 0) + 1;
      });

      const labels = Object.keys(spotBookings);
      const data = Object.values(spotBookings);
      const backgroundColors = this.generateColors(labels.length);
      const borderColors = backgroundColors.map(color => color.replace('0.8', '1'));
    
      this.charts.bookings = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Number of Bookings',
            data: data,
            backgroundColor: backgroundColors,
            borderColor: borderColors,

            borderWidth: 2,
            borderRadius: 8,
            borderSkipped: false,
          }]
        },
        options: {
          responsive: false,
          maintainAspectRatio: false,
          animation: false,
          plugins: {
            legend: {
              display: true,
              labels: {
                color: '#ffffff',
                font: {
                  weight: 'bold',
                  size: 13
                },
                padding: 15,
                usePointStyle: true
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1,
                color: '#ffffff',
                font: {
                  weight: 'bold',
                  size: 12
                }
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)',
                lineWidth: 1
              }
            },
            x: {
              ticks: {
                color: '#ffffff',
                font: {
                  weight: 'bold',
                  size: 12
                }
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.05)',
                drawBorder: true
              }
            }
          }
        }
      });
    },

    renderSpendingChart() {
      if (!this.$refs.spendingChart) {
        console.warn("Spending chart element not found");
        return;
      }
      
      const canvas = this.$refs.spendingChart;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        console.warn("Could not get 2D context for spending chart");
        return;
      }
      
      const rect = canvas.parentElement.getBoundingClientRect();
      canvas.width = rect.width || 400;
      canvas.height = 300;
      const spotSpending = {};
      this.bookingsData.forEach(booking => {
        const spotKey = `${booking.lot_name} - Spot #${booking.spot_number}`;
        spotSpending[spotKey] = (spotSpending[spotKey] || 0) + booking.total_cost;
      });

      const labels = Object.keys(spotSpending);
      const data = Object.values(spotSpending);
      const colors = this.generateColors(labels.length);

      this.charts.spending = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: colors,
            borderWidth: 2,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: false,
          maintainAspectRatio: false,
          animation: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: '#ffffff',
                font: {
                  weight: 'bold',
                  size: 12
                },
                padding: 20,
                usePointStyle: true
              }
            }
          }
        }
      });
    },

    renderTrendChart() {
      if (!this.$refs.trendChart) {
        console.warn("Trend chart element not found");
        return;
      }
      
      const canvas = this.$refs.trendChart;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        console.warn("Could not get 2D context for trend chart");
        return;
      }
      
      const rect = canvas.parentElement.getBoundingClientRect();
      canvas.width = rect.width || 800;
      canvas.height = 300;
      const dailySpending = {};
      this.bookingsData.forEach(booking => {
        const date = new Date(booking.start_time).toISOString().split('T')[0];
        dailySpending[date] = (dailySpending[date] || 0) + booking.total_cost;
      });

      const sortedDates = Object.keys(dailySpending).sort();
      const labels = sortedDates.map(date => new Date(date).toLocaleDateString());
      const data = sortedDates.map(date => dailySpending[date]);

      this.charts.trend = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Daily Spending (₹)',
            data: data,
            borderColor: 'rgba(102, 126, 234, 1)',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: 'rgba(102, 126, 234, 1)',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 6
          }]
        },
        options: {
          responsive: false,
          maintainAspectRatio: false,
          animation: false,
          plugins: {
            legend: {
              display: true,
              labels: {
                color: '#ffffff',
                font: {
                  weight: 'bold',
                  size: 13
                },
                padding: 15,
                usePointStyle: true
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return '₹' + value;
                },
                color: '#ffffff',
                font: {
                  weight: 'bold',
                  size: 12
                }
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)',
                lineWidth: 1
              }
            },
            x: {
              ticks: {
                color: '#ffffff',
                font: {
                  weight: 'bold',
                  size: 12
                }
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.05)',
                drawBorder: true
              }
            }
          }
        }
      });
    },

    generateColors(count) {
      const colors = [
        'rgba(102, 126, 234, 0.8)',
        'rgba(118, 75, 162, 0.8)',
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)'
      ];
      
      const result = [];
      for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
      }
      return result;
    },

    async downloadCSV() {
      try {
        const response = await this.$axios.get("http://127.0.0.1:5000/api/user/reports/csv", {
          responseType: 'blob'
        });
        
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `user_parking_report_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (err) {
        console.error("Error downloading CSV:", err);
        alert("Failed to download CSV file");
      }
    },

    async downloadPDF() {
      try {
        const response = await this.$axios.get("http://127.0.0.1:5000/api/user/reports/pdf", {
          responseType: 'blob'
        });
        
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `user_parking_report_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (err) {
        console.error("Error downloading PDF:", err);
        alert("Failed to download PDF file");
      }
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString();
    },

    logout(redirect = false) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (redirect) {
        window.location.href = '/';
      }
    }
  }
};
</script>

<style scoped>
.user-reports-container {
  background-image: url('@/assets/user-bg.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  min-height: 100vh;
  position: relative;
}

.user-reports-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.55);
  z-index: 1;
  backdrop-filter: blur(2px);
}

.dashboard-content {
  padding: 2rem;
  position: relative;
  z-index: 2;
  max-width: 1400px;
  margin: 0 auto;
}
.top-bar {
  position: relative;
  z-index: 3;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.25), rgba(52, 152, 219, 0.1));
  padding: 1.2rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  margin-bottom: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.btn-back {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1.5px solid rgba(255, 255, 255, 0.2);
  padding: 0.8rem 1.5rem;
  border-radius: 10px;
  font-weight: 700;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(52, 152, 219, 0.2);
}

.btn-download {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.4), rgba(52, 152, 219, 0.2));
  color: #3498db;
  border: 1.5px solid rgba(52, 152, 219, 0.6);
  padding: 0.8rem 1.5rem;
  border-radius: 10px;
  font-weight: 700;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-download:hover {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.6), rgba(52, 152, 219, 0.4));
  border-color: rgba(52, 152, 219, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(52, 152, 219, 0.3);
  color: white;
}

.btn-profile {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  border: none;
  padding: 0.8rem 1.2rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 44px;
  height: 44px;
}

.btn-profile:hover {
  background: linear-gradient(135deg, #2980b9, #1f618d);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(52, 152, 219, 0.4);
}

.top-bar-actions {
  display: flex;
  gap: 1rem;
}

.reports-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-title {
  color: white;
  font-size: 2.5rem;
  font-weight: 800;
  margin: 1rem 0;
  text-shadow: 0 3px 8px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.section-title i {
  color: #3498db;
  font-size: 2rem;
}

.section-subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
  margin-bottom: 0;
  font-weight: 500;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.8rem;
  margin-bottom: 3rem;
}

.summary-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.06));
  backdrop-filter: blur(20px);
  border: 1.5px solid rgba(255, 255, 255, 0.15);
  padding: 2rem;
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.summary-card:hover {
  transform: translateY(-5px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.08));
  border-color: rgba(255, 255, 255, 0.25);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
}

.card-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.4), rgba(46, 204, 113, 0.2));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3498db;
  font-size: 1.8rem;
  flex-shrink: 0;
  border: 1.5px solid rgba(52, 152, 219, 0.3);
}

.card-content h3 {
  font-size: 1.8rem;
  font-weight: 900;
  color: white;
  margin: 0;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.card-content p {
  color: rgba(255, 255, 255, 0.7);
  margin: 4px 0 0 0;
  font-weight: 600;
  font-size: 0.95rem;
  letter-spacing: 0.3px;
}

.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 3rem;
}

.chart-container {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.06));
  backdrop-filter: blur(20px);
  border: 1.5px solid rgba(255, 255, 255, 0.15);
  padding: 2rem;
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.chart-container:hover {
  transform: translateY(-3px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.08));
  border-color: rgba(255, 255, 255, 0.25);
}

.chart-container.full-width {
  grid-column: 1 / -1;
}

.chart-title {
  color: white;
  font-size: 1.3rem;
  font-weight: 800;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.chart-title i {
  color: #3498db;
  font-size: 1.2rem;
}

.chart-container canvas {
  max-height: 300px;
}

.download-section {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.06));
  backdrop-filter: blur(20px);
  border: 1.5px solid rgba(255, 255, 255, 0.15);
  padding: 2rem;
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  margin-bottom: 3rem;
  text-align: center;
}

.download-title {
  color: white;
  font-size: 1.3rem;
  font-weight: 800;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.download-title i {
  color: #3498db;
}

.download-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.recent-bookings {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.06));
  backdrop-filter: blur(20px);
  border: 1.5px solid rgba(255, 255, 255, 0.15);
  padding: 2rem;
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.table-title {
  color: white;
  font-size: 1.3rem;
  font-weight: 800;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.table-title i {
  color: #3498db;
}

.table-container {
  overflow-x: auto;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
}

.bookings-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.bookings-table th,
.bookings-table td {
  padding: 1.2rem;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

.bookings-table th {
  background: rgba(52, 152, 219, 0.2);
  font-weight: 800;
  color: #3498db;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  font-size: 0.85rem;
}

.bookings-table tr:hover {
  background: rgba(52, 152, 219, 0.1);
}

.bookings-table td {
  font-weight: 500;
}

.status-badge {
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-block;
}

.status-badge.completed {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.3), rgba(46, 204, 113, 0.15));
  color: #2ecc71;
  border: 1px solid rgba(46, 204, 113, 0.4);
}

.status-badge.active {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.3), rgba(52, 152, 219, 0.15));
  color: #3498db;
  border: 1px solid rgba(52, 152, 219, 0.4);
}

.status-badge.cancelled {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.3), rgba(220, 53, 69, 0.15));
  color: #dc3545;
  border: 1px solid rgba(220, 53, 69, 0.4);
}

@media (max-width: 1024px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .download-buttons {
    flex-direction: column;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }

  .section-title {
    font-size: 2rem;
  }

  .dashboard-content {
    padding: 1rem;
  }

  .top-bar {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .top-bar-actions {
    flex-direction: column;
  }

  .btn-back,
  .btn-download {
    width: 100%;
    justify-content: center;
  }
}
</style>