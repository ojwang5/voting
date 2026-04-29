# UI Improvements TODO

## Task: Improve voter view button, back to dashboard button, bulk upload button, backgrounds on superadmin

### Step 1: CSS - Add new button & background classes ✅
- [x] Add `.btn-voter-view` (primary blue gradient, white text, shadow, hover lift)
- [x] Add `.btn-back-dashboard` (dark slate gradient, white text, shadow, hover lift)
- [x] Add `.btn-bulk-upload` (vibrant warning gradient, white text, glow animation)
- [x] Add `.admin-body` background (deep slate/navy radial gradient with dark theme overrides)

### Step 2: Base Template ✅
- [x] Add `{% block body_class %}{% endblock %}` to `<body>` tag in `base.html`

### Step 3: Update Admin Templates (17 total) ✅
- [x] `admin_dashboard.html` - voter view btn → btn-voter-view, bulk upload → btn-bulk-upload, admin-body
- [x] `admin_voters.html` - back btn → btn-back-dashboard, bulk upload → btn-bulk-upload, admin-body
- [x] `admin_elections.html` - back btn → btn-back-dashboard, admin-body
- [x] `admin_candidates.html` - back btn → btn-back-dashboard, admin-body
- [x] `admin_positions.html` - back btn → btn-back-dashboard, admin-body
- [x] `audit_log.html` - back btn → btn-back-dashboard, admin-body
- [x] `bulk_register_voters.html` - back btn → btn-back-dashboard, admin-body
- [x] `register_voter.html` - back btn → btn-back-dashboard, admin-body
- [x] `register_candidate.html` - back btn → btn-back-dashboard, admin-body
- [x] `voter_credentials.html` - view voters → btn-voter-view, back → btn-back-dashboard, admin-body
- [x] `admin_change_password.html` - back btn → btn-back-dashboard, admin-body
- [x] `admin_election_voters.html` - back btn → btn-back-dashboard, admin-body
- [x] `admin_voter_elections.html` - back btn → btn-back-dashboard, admin-body
- [x] `admin_position_edit.html` - cancel btn → btn-back-dashboard, admin-body
- [x] `edit_voter.html` - cancel btn → btn-back-dashboard, admin-body
- [x] `edit_candidate.html` - cancel btn → btn-back-dashboard, admin-body
- [x] `create_election.html` - cancel btn → btn-back-dashboard, admin-body

### Step 4: Test ✅
- [x] All admin templates verified to have `admin-body`
- [x] Voter-facing pages (index, vote, results, dashboard, detail, view_candidate) left with light theme

