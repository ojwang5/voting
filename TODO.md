# TODO

- [x] Fix syntax error in Django migration file `polls/migrations/0002_alter_candidate_options_remove_election_position_and_more.py` by removing unresolved git merge conflict markers.
- [x] Fix syntax error in Django migration file `polls/migrations/0001_initial.py` by removing unresolved git merge conflict markers.
- [x] Database schema fixed: removed orphaned `is_active` column from `polls_election` table that existed outside Django migrations (was causing `NOT NULL constraint failed` on election creation). Model uses `@property is_active` instead.
- [x] Admin voter registration now processes election checkboxes and auto-assigns voters to eligible elections.
- [x] Registration template now receives `upcoming_elections` context variable.
- [x] Email configuration fixed: uses SendGrid SMTP via `SENDGRID_API_KEY` environment variable.
- [x] Procfile added: single gunicorn worker with threads (fixes OOM SIGKILL on Render free tier).
- [x] render.yaml added: explicit deployment config with environment variables.

## Email Setup for Production (SendGrid on Render.com)

The system uses SendGrid SMTP when `SENDGRID_API_KEY` is set in the environment.

### Step 1: Create a SendGrid account & API key
1. Go to https://signup.sendgrid.com and create a free account
2. Free tier: **100 emails/day forever** — plenty for a voting system
3. Go to **Settings > API Keys > Create API Key**
4. Choose **Full Access**, name it "VotingHub Production", click **Create & View**
5. Copy the key (it starts with `SG.`)

### Step 2: Verify a Sender
SendGrid requires you to verify the "from" email address before you can send:
1. Go to **Settings > Sender Authentication**
2. Click **Verify a Single Sender**
3. Enter: **Name** = `VotingHub System`, **Email** = `ojwangsamuel1@gmail.com`
4. Check the verification email from SendGrid and click the link

### Step 3: Set environment variables on Render.com
In your Render dashboard → your service → **Environment**, add:

| Variable | Value |
|---|---|
| `SENDGRID_API_KEY` | `SG.xxxxx...` (your full API key from Step 1) |
| `DEFAULT_FROM_EMAIL` | `ojwangsamuel1@gmail.com` (must match Step 2) |

### Step 4: Redeploy
Push your code to Render (or trigger a manual deploy). Emails will now send.

### Troubleshooting
- Emails go to spam? Add SPF/DKIM records (Sender Authentication > Domain Authentication)
- "401 Unauthorized" in logs? Your API key is wrong or expired
- "403 Sender not verified"? The email in `DEFAULT_FROM_EMAIL` isn't verified in SendGrid

### Local Development
No setup needed — without `SENDGRID_API_KEY`, emails print to your terminal console.

