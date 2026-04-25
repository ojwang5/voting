# Voting System Enhancement Tasks

## Task 1: Make Scheduled Elections Accessible to Registered Voters
- [x] Add `election_detail` view in `polls/views.py` (already exists as `detail`)
- [x] Add URL route for election detail (already exists)
- [x] Create `templates/polls/election_detail.html` (already exists as `detail.html`)
- [x] Update `templates/polls/dashboard.html` with "View Details" link for upcoming elections

## Task 2: Limit Election Admin Privileges
- [x] Update decorators in `polls/views_admin.py` (ADMIN → view-only for elections, positions, candidates)
- [x] Update `templates/polls/admin_dashboard.html` (hide create buttons for ADMIN)
- [x] Update `templates/polls/admin_elections.html` (hide create/edit/delete for ADMIN)
- [x] Update `templates/polls/admin_candidates.html` (hide create/edit/delete for ADMIN)
- [x] Update `templates/polls/admin_positions.html` (make viewable for ADMIN)

## Task 3: Remove Force Number Range Functionality
- [x] Remove range from `polls/models.py` (already removed)
- [x] Remove range from `polls/forms.py` (already removed)
- [x] Generate and apply migration (no migration needed - already in sync)

## Task 4: Bulk Voter Registration (CSV & Excel)
- [x] Add `openpyxl` to `requirements.txt`
- [x] Create `BulkVoterUploadForm` in `polls/forms.py` (already exists)
- [x] Add `bulk_register_voters` view in `polls/views_admin.py` (already exists)
- [x] Add URL route in `polls/urls.py` (already exists)
- [x] Create `templates/polls/bulk_register_voters.html`
- [x] Update `templates/polls/admin_voters.html` with bulk upload button
- [x] Update `templates/polls/admin_dashboard.html` with bulk upload link

## Final Steps
- [x] Run migrations (up to date - no changes needed)
- [x] Install new requirements (openpyxl installed)
- [x] Test all functionality (syntax checks passed on all key files)

