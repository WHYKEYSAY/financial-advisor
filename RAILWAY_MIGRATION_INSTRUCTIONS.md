# Railway Database Migration Instructions

## ⚠️ IMPORTANT: VCM Migration Required

The VCM (Virtual Credit Manager) feature requires database schema changes. You need to manually run the migration on Railway.

## Steps to Run Migration

### Option 1: Via Railway CLI (Recommended)

```bash
# Install Railway CLI (if not already installed)
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Run the migration
railway run alembic upgrade head
```

### Option 2: Via Railway Dashboard

1. Go to https://railway.app/dashboard
2. Select your `financial-advisor-production-e0a9` project
3. Click on the backend service
4. Go to the **"Settings"** tab
5. Scroll down to **"Custom Start Command"** or **"Deploy Logs"**
6. Open a shell/terminal in the service
7. Run: `alembic upgrade head`

### Option 3: Add Migration to Dockerfile

Update `_monorepo/backend/Dockerfile` to run migrations on startup:

```dockerfile
# Before CMD, add:
RUN alembic upgrade head

# Or modify the CMD:
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

## Verify Migration Was Applied

After running the migration, verify it worked:

```bash
# Via Railway CLI
railway run alembic current

# You should see: abc123def456 (head)
```

## What This Migration Does

The migration `abc123def456_add_vcm_fields_to_cards.py` adds three columns to the `cards` table:

- `current_balance` (Numeric): Current balance on the card
- `vcm_enabled` (Boolean): Whether card is enrolled in VCM
- `vcm_priority` (Integer): Priority order for spending allocation

## Troubleshooting

### If migration fails with "relation already exists"

The columns might already exist. Check with:

```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_name='cards' 
AND column_name IN ('current_balance', 'vcm_enabled', 'vcm_priority');
```

If they exist, mark the migration as complete:

```bash
alembic stamp head
```

### If you see 500 errors from `/vcm/overview`

1. Check Railway logs for the actual error
2. Verify the migration ran successfully
3. Ensure the columns exist in the database
4. Test the endpoint with: `curl https://financial-advisor-production-e0a9.up.railway.app/vcm/overview`

## Current Status

- ✅ Migration file created: `abc123def456_add_vcm_fields_to_cards.py`
- ✅ Pushed to GitHub (commit: a4cf915)
- ⏳ Awaiting manual migration execution on Railway
- ⏳ VCM endpoints will work after migration is applied

## Next Steps

1. Run the migration on Railway using one of the methods above
2. Verify VCM page loads without errors: https://financial-advisor-rust.vercel.app/en/vcm
3. Add some test credit cards via the API
4. Test the allocation calculator
