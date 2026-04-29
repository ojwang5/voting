# TODO: Allow Superadmin to Change or Reset Voter/User Password

## Steps

- [x] Step 1: Add `AdminChangePasswordForm` to `polls/forms.py`
- [x] Step 2: Add `admin_change_voter_password` view to `polls/views_admin.py` (superadmin only)
- [x] Step 3: Add URL route in `polls/urls.py`
- [x] Step 4: Create `templates/polls/admin_change_password.html`
- [x] Step 5: Update `templates/polls/admin_voters.html` with Change Password button for superadmins
- [x] Step 6: Run Django check and verify

## Summary of Changes

### New Form: `AdminChangePasswordForm` (polls/forms.py)
- Fields: `new_password`, `confirm_password`, `force_change` (checkbox, default true)
- Validates password match, minimum 8 characters
- Clean Bootstrap widget styling

### New View: `admin_change_voter_password` (polls/views_admin.py)
- **SuperAdmin only** (`@user_passes_test(is_superadmin)`)
- GET: renders form with voter details
- POST: sets custom password, toggles `must_change_password` based on checkbox
- Writes audit log entry with `ACTION_VOTER_RESET_PASSWORD`
- Redirects back to `admin_voters` on success

### New Template: `admin_change_password.html` (templates/polls/)
- Clean Bootstrap card layout with voter info banner
- Shows non-field errors inline
- Back button to voters list

### Updated Voters Table (templates/polls/admin_voters.html)
- Added **Change Password** button (`bi-key-fill`, dark outline) visible **only to superadmins**
- Placed between Edit and Reset Password buttons
- Keeps existing Reset Password for admins who just need a quick auto-generated password

### URL Route (polls/urls.py)
- `admin/voters/<int:voter_id>/change-password/` → `admin_change_voter_password`
