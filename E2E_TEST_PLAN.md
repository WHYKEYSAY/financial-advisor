# CreditSphere Production E2E Test Plan

Owner: QA Team  
Version: 1.0  
Date: 2025-11-06

## 1. Test Environments
- Frontend (Prod): https://financial-advisor-rust.vercel.app
- Backend (Prod): https://financial-advisor-production-e0a9.up.railway.app
- Frontend env var in Vercel: NEXT_PUBLIC_BACKEND_URL=https://financial-advisor-production-e0a9.up.railway.app

## 2. Scope and Objectives
- Validate end-to-end user flow in production with real endpoints
- Cover authentication, file upload, dashboard data, and navigation
- Confirm critical KPIs render correctly on dashboard
- Identify production-only issues and provide workarounds

Out of scope:
- Performance and load testing
- Accessibility audit
- Browser matrix beyond Chrome latest

## 3. Test Data
- Create a unique test user for each run to avoid collisions:
  - Email pattern: qa+e2e_{timestamp}@example.com
  - Password pattern: Test1234!{random}
- Test PDF: 1 to 2 pages, size under 1 MB

## 4. Manual Test Cases

### 4.1 Authentication Flow
Preconditions:
- Frontend and backend are reachable
- Clear browser storage before starting

Steps:
1. Navigate to the frontend root URL
2. Open Sign Up or Create Account
3. Enter a new email using the pattern above
4. Enter a strong password using the pattern above
5. Submit registration
6. Attempt to log in with the newly created credentials
7. Open DevTools and check Application storage for the auth token presence
8. Click Logout or use the profile menu to sign out

Expected:
- Registration succeeds and shows a success state or redirects to a logged-in area
- Login succeeds and lands on a post-login page such as dashboard or home
- Token storage is visible in Application storage or cookies
- Logout clears auth token and returns to a public page

Validation checkpoints and screenshots:
- Post-registration success screen
- Application storage view showing token or auth state
- Post-login landing page
- Post-logout public page

Negative checks:
- Invalid email format is rejected with a clear validation message
- Weak passwords are rejected with a clear validation message

### 4.2 File Upload
Steps:
1. Navigate to the upload page at path /upload
2. Drag and drop a valid PDF or select a file via the file picker
3. Observe upload progress indicator and status
4. Wait for parsing to complete and any import confirmation to appear

Expected:
- Upload starts and shows progress
- Parsing completes without errors
- A success message indicates transactions or data imported

Validation checkpoints and screenshots:
- Upload progress visible
- Parsing complete state
- Success or imported summary state

Notes and known behaviors:
- If server is cold, first upload may take longer
- Large files can be throttled by platform limits; prefer a small PDF for verification

### 4.3 Dashboard Features
Steps:
1. Navigate to /dashboard
2. Verify account overview cards render with numbers and units
3. Verify credit health card renders with score or health status
4. Verify utilization progress bars show non-empty values or zero states
5. Verify health status badges reflect correct state
6. Expand an individual card to view details if supported

Expected:
- No console errors on dashboard route
- KPI values render with consistent formatting
- Progress bars show correct proportions for utilization
- Badges reflect expected health status
- Expand and collapse works as designed

Validation checkpoints and screenshots:
- Top row overview cards
- Credit health card
- Utilization progress bars
- Expanded card details

Data setup note:
- If the new user has no data, upload a sample PDF first to seed dashboard values

### 4.4 Navigation and Routing
Steps:
1. Use the site header or sidebar to navigate to Home, Upload, Dashboard, and Settings if present
2. Refresh each page directly by typing the path in the address bar
3. Attempt an unknown path to verify 404 handling

Expected:
- Nav links route without full page reloads
- Direct deep links resolve correctly in production
- Unknown paths render a friendly not found page

Validation checkpoints and screenshots:
- Active nav item state per page
- Working deep link reload on dashboard and upload
- 404 page for unknown route

## 5. Expected Results Summary
- All critical flows above complete without blocking errors
- Dashboard renders at least one set of cards or zero-state placeholders
- Console shows no red errors during normal navigation

## 6. Known Issues and Workarounds
- React minified error 418 seen in console in some builds
  - Likely caused by using uppercase HTML tag names in JSX
  - Workaround: use lowercase html and body in App Router layout
- File upload size or timeout on first request
  - Workaround: test with a small PDF, then retry larger files after warmup
- CORS or cookie SameSite issues during auth
  - Workaround: prefer token based auth in SPA

## 7. Logs and Monitoring
- Browser DevTools console for front end errors
- Network tab for API status codes
- Backend health at /health should return HTTP 200 with {"status":"ok"}

## 8. Exit Criteria
- All tests in section 4 pass
- No Sev1 defects open
- Sev2 defects have documented workarounds
