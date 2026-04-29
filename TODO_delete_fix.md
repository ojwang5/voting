# TODO: Fix Delete Module Under Voter Management & Add Delete Election Positions

## Step 1: Fix Voter Delete Button (admin_voters.html)
- [x] Replace GET `<a>` tag with POST `<form>` for voter delete
- [x] Add CSRF token
- [x] Keep styling and confirmation dialog

## Step 2: Add Election Position Delete View (views_admin.py)
- [x] Add `delete_election_position()` view
- [x] Restrict to superadmins
- [x] Safety check: block if candidates exist for that position in election
- [x] Audit log on success

## Step 3: Add URL Route (urls.py)
- [x] Add path for `delete_election_position`

## Step 4: Add Election Position Delete UI (admin_elections.html)
- [x] Desktop table view: add delete button per position badge
- [x] Mobile card view: add delete button per position badge
- [x] Only show for superadmins
- [x] POST form with CSRF and confirmation

## Step 5: Testing
- [ ] Verify voter delete works
- [ ] Verify election position delete respects safety check
- [ ] Verify UI renders correctly

