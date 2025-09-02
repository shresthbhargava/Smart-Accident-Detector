document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const loginPage = document.getElementById('loginPage');
  const dashboard = document.getElementById('dashboard');
  const loginForm = document.getElementById('loginForm');
  const themeToggleBtn = document.querySelector('.theme-toggle');
  const body = document.body;
  const refreshBtn = document.getElementById('refreshBtn');
  const fleetRefreshBtn = document.querySelector('.fleet-status-section .refresh-btn');
  const logoutBtn = document.getElementById('logoutBtn');

  // Load saved theme or default to dark
  const savedTheme = localStorage.getItem('skywatch-theme');
  body.setAttribute('data-theme', savedTheme || 'dark');
  setThemeIcon();

  // Theme toggle event
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const currentTheme = body.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      body.setAttribute('data-theme', newTheme);
      localStorage.setItem('skywatch-theme', newTheme);
      setThemeIcon();
    });
  }

  function setThemeIcon() {
    if (!themeToggleBtn) return;
    themeToggleBtn.textContent = body.getAttribute('data-theme') === 'dark' ? '☀️' : '🌙';
  }

  // Login functionality
  if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      if (email && password) {
        showLoading();
        setTimeout(() => {
          loginPage.classList.add('d-none');
          dashboard.classList.remove('d-none');
          initializeDashboard();
        }, 1500);
      }
    });
  }

  // Google login simulation
  const googleBtn = document.querySelector('.google-btn');
  if (googleBtn) {
    googleBtn.addEventListener('click', function() {
      showLoading();
      setTimeout(() => {
        loginPage.classList.add('d-none');
        dashboard.classList.remove('d-none');
        initializeDashboard();
      }, 1500);
    });
  }

  // Logout functionality
  if(logoutBtn) {
    logoutBtn.addEventListener('click', function(e) {
      e.preventDefault();
      dashboard.classList.add('d-none');
      loginPage.classList.remove('d-none');
      // Reset login form
      if (loginForm) {
        loginForm.reset();
      }
    });
  }

  // Show loading state
  function showLoading() {
    const submitBtn = document.querySelector('.signin-btn');
    if (!submitBtn) return;
    const originalText = submitBtn.textContent;
    submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Signing in...`;
    submitBtn.disabled = true;
    setTimeout(() => {
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    }, 1500);
  }

  // Initialize dashboard
  function initializeDashboard() {
    updateSystemStats();
    updateLiveFeed();
    updateAlerts();
    updateDroneFleet();

    setInterval(updateSystemStats, 5000);
    setInterval(updateLiveFeed, 3000);
    setInterval(updateAlerts, 10000);
    setInterval(updateDroneFleet, 7000);
  }

  // Update system statistics
  function updateSystemStats() {
    const activeDrones = Math.floor(Math.random() * 5) + 1;
    const alertsToday = Math.floor(Math.random() * 10);
    const detectionRate = Math.floor(Math.random() * 30) + 70;

    const statValues = document.querySelectorAll('.stat-value');
    if (statValues.length >= 4) {
      statValues[0].textContent = activeDrones;
      statValues[1].textContent = alertsToday;
      statValues[2].textContent = detectionRate + '%';
      statValues[3].textContent = 'ONLINE';
    }
  }

  // Update live feed
  function updateLiveFeed() {
    const feedContent = document.querySelector('.live-feed .card-content .live-feed-box');
    if (!feedContent) return;
    const isConnected = Math.random() > 0.3;
    feedContent.innerHTML = isConnected
      ? `<div class="detected-object-box"><p>Object Detected</p><small>Confidence: ${Math.floor(Math.random() * 20) + 80}%</small></div>`
      : `<p>Live feed is currently disconnected.</p>`;
  }

  // Update alerts
  function updateAlerts() {
    const alertsSection = document.getElementById('recentAlerts');
    if (!alertsSection) return;
    
    // Static alerts for demonstration, can be randomized
    const alerts = [
      { text: "System Update Available", status: "resolved", time: "10:43:39 PM" },
      { text: "Connection Lost", status: "resolved", time: "10:03:47 PM" },
      { text: "Critical Anomaly Detected", status: "critical", time: "10:10:58 PM" },
      { text: "Drone Battery Low (Drone 1)", status: "warning", time: "9:55:01 PM" },
      { text: "Unauthorized Access Attempt", status: "critical", time: "9:30:15 PM" }
    ];

    const randomAlerts = alerts.sort(() => 0.5 - Math.random()).slice(0, Math.floor(Math.random() * 3) + 1);

    let alertsHtml = '';
    randomAlerts.forEach(alert => {
      alertsHtml += `
        <div class="alert-row">
          <span class="alert-icon">⚠️</span>
          <span class="alert-text">${alert.text}</span>
          <span class="alert-badge ${alert.status}">${alert.status.toUpperCase()}</span>
          <span class="alert-time">${alert.time}</span>
        </div>
      `;
    });
    alertsSection.innerHTML = alertsHtml || '<p>No recent alerts.</p>';
  }

  // Update drone fleet with random statuses
  function updateDroneFleet() {
    const fleetSection = document.getElementById('droneFleet');
    if (!fleetSection) return;

    const statuses = ["online", "offline", "warning"];
    const statusLabels = {
      "online": "ONLINE",
      "offline": "OFFLINE",
      "warning": "WARNING"
    };

    const droneCount = Math.floor(Math.random() * 5) + 1;
    let fleetHtml = '';
    for (let i = 1; i <= droneCount; i++) {
      const status = statuses[Math.floor(Math.random() * statuses.length)];
      fleetHtml += `
        <div class="drone-card">
          <div class="drone-info">
            <span class="drone-name">Drone ${i}</span>
            <span class="drone-status ${status}">${statusLabels[status]}</span>
          </div>
          <div class="drone-actions">
            <button>Details</button>
          </div>
        </div>
      `;
    }
    fleetSection.innerHTML = fleetHtml || '<p>No drones available.</p>';
  }

  // Footer Refresh button
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      refreshBtn.textContent = 'Refreshing...';
      refreshBtn.disabled = true;
      setTimeout(() => {
        refreshBtn.textContent = 'Refresh';
        refreshBtn.disabled = false;
        updateSystemStats();
        updateLiveFeed();
        updateAlerts();
        updateDroneFleet();
      }, 1000);
    });
  }

  // Fleet Refresh button
  if (fleetRefreshBtn) {
    fleetRefreshBtn.addEventListener('click', () => {
      fleetRefreshBtn.innerHTML = '<span>🔄</span> <span class="ms-1">Refreshing...</span>';
      setTimeout(() => {
        updateDroneFleet();
        fleetRefreshBtn.innerHTML = '<span>🔄</span> <span class="ms-1">Refresh</span>';
      }, 1000);
    });
  }
});