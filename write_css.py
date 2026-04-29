import os

css = r'''/* Modern Voting System Styles - Enhanced UX */
:root {
  --primary: #2563eb;
  --primary-dark: #1d4ed8;
  --success: #10b981;
  --success-dark: #059669;
  --danger: #ef4444;
  --warning: #f59e0b;
  --dark: #1f2937;
  --light: #f9fafb;
  --border: #e5e7eb;
  --shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
  --shadow-lg: 0 25px 50px -12px rgba(0,0,0,0.25);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.6;
  color: var(--dark);
  background: linear-gradient(135deg, var(--light) 0%, #f0f2f5 100%);
  min-height: 100vh;
}

/* Enhanced Button Styles */
.btn-voter-view {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.45);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-voter-view:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 28px 0 rgba(37, 99, 235, 0.55);
  color: white;
}

.btn-back-dashboard {
  background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
  color: white;
  border: 1px solid rgba(148, 163, 184, 0.25);
  box-shadow: 0 4px 14px 0 rgba(30, 41, 59, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-back-dashboard:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 28px 0 rgba(30, 41, 59, 0.5);
  color: white;
  border-color: rgba(148, 163, 184, 0.4);
}

.btn-bulk-upload {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 14px 0 rgba(245, 158, 11, 0.45);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: pulse-glow 3s ease-in-out infinite;
}

.btn-bulk-upload:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 28px 0 rgba(245, 158, 11, 0.6);
  color: white;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 4px 14px 0 rgba(245, 158, 11, 0.45); }
  50% { box-shadow: 0 4px 22px 0 rgba(245, 158, 11, 0.7); }
}

/* Navbar */
.navbar {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  box-shadow: var(--shadow);
  border-radius: 0 0 24px 24px;
  padding: 1rem 0;
  position: relative;
  z-index: 1030;
}

.navbar-brand {
  font-weight: 800;
  font-size: 1.75rem;
  color: var(--primary-dark) !important;
}

/* Cards */
.card {
  background: white;
  border-radius: 20px;
  box-shadow: var(--shadow);
  border: none;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
}

.card-header {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  padding: 1.75rem 2rem;
  border: none;
  position: relative;
  overflow: hidden;
}

.card-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.1) 50%, transparent 100%);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  position: relative;
  z-index: 1;
}

/* Buttons */
.btn {
  border-radius: 16px;
  padding: 0.875rem 2rem;
  font-weight: 600;
  border: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.5s;
}

.btn:hover::before {
  left: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white;
  box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px 0 rgba(37, 99, 235, 0.4);
}

.btn-success {
  background: linear-gradient(135deg, var(--success) 0%, var(--success-dark) 100%);
  color: white;
}

.btn-outline-primary {
  color: var(--primary);
  border: 2px solid var(--primary);
  background: transparent;
}

.btn-outline-primary:hover {
  background: var(--primary);
  color: white;
  transform: translateY(-2px);
}

/* Forms */
.form-control {
  border-radius: 16px;
  border: 2px solid var(--border);
  padding: 1rem 1.25rem;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15);
  background: white;
  transform: translateY(-1px);
}

.form-label {
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--dark);
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Alerts */
.alert {
  border-radius: 16px;
  border: none;
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow);
}

.alert-info {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border: 1px solid rgba(255,255,255,0.2);
}

/* Election Cards */
.election-card, .candidate-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.election-card:hover, .candidate-card:hover {
  transform: translateY(-6px) scale(1.02);
}

.candidate-photo, .candidate-placeholder {
  height: 220px;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.candidate-card:hover .candidate-photo {
  transform: scale(1.05);
}

.candidate-placeholder {
  background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Progress Bars */
.progress {
  height: 16px;
  border-radius: 12px;
  background: rgba(0,0,0,0.1);
  overflow: hidden;
}

.progress-bar {
  position: relative;
  border-radius: 12px;
  transition: width 1s ease;
}

.progress-bar::after {
  content: attr(aria-valuetext) '%';
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-weight: 600;
  color: rgba(255,255,255,0.95);
  font-size: 0.875rem;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, rgba(37,99,235,0.1) 0%, rgba(16,185,129,0.1) 100%);
  border-radius: 32px;
  padding: 5rem 3rem;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.3);
}

.hero-section h1 {
  background: linear-gradient(135deg, var(--primary), var(--success));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Stats Cards */
.stats-card {
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 24px;
}

/* Admin Election Mobile Cards */
.admin-election-card {
  background: white;
  border-radius: 16px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  padding: 1.25rem;
  margin-bottom: 1rem;
  transition: all 0.2s ease;
}

.admin-election-card:last-child {
  margin-bottom: 0;
}

.admin-election-card .election-title {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--dark);
  line-height: 1.3;
}

.admin-election-card .election-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 0.25rem 0.5rem;
  margin-bottom: 0.5rem;
}

.admin-election-card .election-meta-label {
  font-weight: 600;
  font-size: 0.8rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  min-width: 70px;
  flex-shrink: 0;
}

.admin-election-card .election-meta-value {
  font-size: 0.9rem;
  color: var(--dark);
  flex: 1;
}

.admin-election-card .election-actions {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border);
}

.admin-election-card .election-actions .btn {
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  border-radius: 12px;
}

.admin-election-card .election-actions .dropdown-toggle {
  justify-content: center;
}

/* Table action buttons compact */
.table .btn-sm {
  padding: 0.375rem 0.625rem;
  font-size: 0.8rem;
  border-radius: 10px;
}

/* ============================================
   DROPDOWN OVERLAP / Z-INDEX FIXES
   ============================================ */

/* 1. Raise dropdown containers above surrounding cards.
   Cards establish implicit stacking contexts via animations
   and transforms. A positioned .dropdown with z-index creates
   a higher context so the menu can overlap adjacent cards. */
.dropdown {
  position: relative;
  z-index: 100;
}

/* 2. Ensure the dropdown menu itself renders at the top
   of its local stacking context. */
.dropdown-menu {
  position: absolute;
  z-index: 1050 !important;
  box-shadow: var(--shadow-lg);
}

/* 3. Dynamically allow dropdown menus to escape overflow:hidden on .card
   only when a dropdown is actually open, avoiding side effects on hover transforms. */
.card:has(.dropdown-menu.show) {
  overflow: visible;
  z-index: 102;
}

/* 3b. Unclip card headers when dropdowns are open. */
.card-header:has(.dropdown),
.card-header:has(.btn-group) {
  overflow: visible;
}

/* 3c. Fix mobile admin election card stacking so open export dropdowns
   rise above the card below them. */
.admin-election-card:has(.dropdown-menu.show) {
  position: relative;
  z-index: 102;
  overflow: visible;
}

/* 4. Unclip table-responsive when a dropdown is open (all breakpoints). */
.table-responsive:has(.dropdown-menu.show) {
  overflow: visible !important;
}

/* 5. Navbar profile dropdown reinforcement so it always
   sits above page content and cards. */
.navbar-nav .dropdown {
  z-index: 200;
}

.navbar-nav .dropdown-menu {
  z-index: 1050 !important;
}

/* 6. Keep form selects behaving correctly inside positioned containers */
.position-relative .form-select,
.position-relative select {
  z-index: 1;
}

.form-select {
  position: relative;
  z-index: 2;
}

/* Navbar dropdown alignment and overlap fixes */
.navbar-nav .dropdown-menu {
  margin-top: 0.5rem;
  border-radius: 16px;
  border: none;
  box-shadow: var(--shadow-lg);
  min-width: 220px;
  padding: 0.5rem 0;
}

.navbar-nav .nav-link {
  white-space: nowrap;
  font-weight: 500;
}

.navbar-nav .dropdown-toggle::after {
  vertical-align: middle;
  margin-left: 0.5rem;
}

.dropdown-item-text strong {
  display: block;
  margin-top: 0.25rem;
}

.dropdown-item {
  border-radius: 8px;
  margin: 0.125rem 0.5rem;
  padding: 0.5rem 1rem;
  width: auto;
}

.dropdown-item:hover {
  background-color: rgba(37, 99, 235, 0.08);
}

.dropdown-item form {
  display: block;
}

.dropdown-item button {
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  padding: 0;
}

/* Ensure navbar doesn't wrap and stays aligned */
@media (max-width: 991px) {
  .navbar-collapse {
    padding-top: 1rem;
  }

  .navbar-nav .dropdown-menu {
    box-shadow: none;
    border: 1px solid var(--border);
    margin-top: 0.25rem;
  }
}

/* Tweak navbar toggler for cleaner look */
.navbar-toggler {
  border-radius: 12px;
  padding: 0.5rem;
}

.navbar-toggler:focus {
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25);
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card {
  animation: fadeInUp 0.6s ease forwards;
}

/* Loading */
.loading {
  position: relative;
}

.loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 40px;
  height: 40px;
  margin: -20px 0 0 -20px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .btn-lg {
    padding: 0.75rem 1.25rem;
    font-size: 1rem;
  }
  
  .card {
    margin-bottom: 1.25rem;
    border-radius: 16px;
  }
  
  .card-header {
    padding: 1.25rem 1.5rem;
  }
  
  .hero-section {
    padding: 2.5rem 1.25rem;
  }

  .card-title {
    font-size: 1.25rem;
  }

  .table-responsive {
    border-radius: 12px;
    border: 1px solid var(--border);
  }

  .table-responsive .table {
    margin-bottom: 0;
  }
}

/* Mobile-specific admin election styles */
@media (max-width: 767.98px) {
  .admin-election-card {
    padding: 1rem;
  }

  .admin-election-card .election-title {
    font-size: 1rem;
  }

  .admin-election-card .election-actions .btn,
  .admin-election-card .election-actions .dropdown-toggle {
    font-size: 0.8rem;
    padding: 0.4rem 0.5rem;
  }

  .btn {
    padding: 0.625rem 1.25rem;
  }

  /* Ensure header buttons don't overflow */
  .w-100.w-md-auto {
    width: 100% !important;
  }
}

@media (min-width: 768px) {
  .w-md-auto {
    width: auto !important;
  }
}
'''

with open('static/polls/css/modern.css', 'w', encoding='utf-8') as f:
    f.write(css)

print('CSS written successfully')
