# Fix "Vote Now" Button Issue

## Problem
When voters click "Vote Now", they cannot proceed to vote. The dashboard incorrectly treats partially-voted elections as fully voted, hiding the voting button.

## Steps
- [x] 1. Analyze codebase and identify root cause
- [x] 2. Update `polls/views.py` `dashboard()` to compute `fully_voted_elections`
- [x] 3. Update `templates/polls/dashboard.html` button logic for partial/fully voted states
- [x] 4. Verify the fix handles all voting states correctly


