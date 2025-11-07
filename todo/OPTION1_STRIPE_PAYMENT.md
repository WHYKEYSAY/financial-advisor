# Option 1: Stripe Payment & Subscription System

**Goal**: Implement paid subscriptions for The Optimizer ($9.99/mo) and The Autopilot ($29.99/mo)  
**Time Estimate**: 2-3 days  
**Priority**: High - Revenue Generation

---

## 📋 Implementation Checklist

### **Phase 1: Stripe Setup** (Est. 1 hour)

- [ ] Create Stripe account (https://stripe.com)
- [ ] Get API keys (Test + Production)
- [ ] Create products in Stripe Dashboard:
  - **The Analyst** - Free tier (no Stripe product needed)
  - **The Optimizer** - $9.99/month - `price_optimizer_monthly`
  - **The Autopilot** - $29.99/month - `price_autopilot_monthly`
- [ ] Configure webhook endpoint URL: `https://your-backend.railway.app/stripe/webhook`
- [ ] Get webhook signing secret
- [ ] Add to Railway environment variables:
  - `STRIPE_SECRET_KEY`
  - `STRIPE_PUBLISHABLE_KEY`
  - `STRIPE_WEBHOOK_SECRET`
  - `STRIPE_PRICE_OPTIMIZER` (price ID)
  - `STRIPE_PRICE_AUTOPILOT` (price ID)

---

### **Phase 2: Backend - Stripe Integration** (Est. 4-6 hours)

#### 2.1 Install Dependencies
- [ ] Add to `backend/requirements.txt`:
  ```
  stripe==7.10.0
  ```

#### 2.2 Create Stripe Schemas (`app/schemas/stripe.py`)
- [ ] `CheckoutSessionRequest` - Create checkout session
- [ ] `CheckoutSessionResponse` - Return session URL
- [ ] `PortalSessionRequest` - Customer portal access
- [ ] `PortalSessionResponse` - Portal URL
- [ ] `SubscriptionStatusResponse` - Current subscription info
- [ ] `WebhookEvent` - Stripe webhook payload

#### 2.3 Create Stripe Service (`app/services/stripe_service.py`)
- [ ] `create_checkout_session(user_id, tier)` - Generate checkout URL
- [ ] `create_portal_session(user_id)` - Generate customer portal URL
- [ ] `get_subscription_status(user_id)` - Fetch current subscription
- [ ] `handle_webhook_event(event)` - Process Stripe webhooks
- [ ] Webhook handlers:
  - `checkout.session.completed` - Create subscription
  - `customer.subscription.updated` - Update subscription
  - `customer.subscription.deleted` - Cancel subscription
  - `invoice.payment_succeeded` - Log payment
  - `invoice.payment_failed` - Handle failed payment

#### 2.4 Create Stripe API (`app/api/stripe.py`)
- [ ] `POST /stripe/create-checkout-session` - Start subscription flow
- [ ] `POST /stripe/create-portal-session` - Manage subscription
- [ ] `POST /stripe/webhook` - Receive Stripe events (no auth)
- [ ] `GET /stripe/subscription-status` - Check current tier

#### 2.5 Update User Tier Logic
- [ ] After successful payment, update `user.tier` in database
- [ ] Update `subscription` table with Stripe data
- [ ] Reset quota limits based on new tier

---

### **Phase 3: Backend - Access Control** (Est. 2-3 hours)

#### 3.1 Create Tier Permissions (`app/core/permissions.py`)
- [ ] Define tier capabilities:
  ```python
  TIER_LIMITS = {
      "analyst": {
          "statements_per_month": 5,
          "ai_calls_per_month": 20,
          "features": ["upload_csv", "view_transactions", "basic_charts"]
      },
      "optimizer": {
          "statements_per_month": 50,
          "ai_calls_per_month": 200,
          "features": ["upload_csv", "upload_pdf", "view_transactions", 
                       "advanced_charts", "recommendations", "quarterly_reports"]
      },
      "autopilot": {
          "statements_per_month": -1,  # unlimited
          "ai_calls_per_month": -1,    # unlimited
          "features": ["all"]  # full access including VCM
      }
  }
  ```

#### 3.2 Create Access Control Decorators
- [ ] `@require_tier("optimizer")` - Protect optimizer+ endpoints
- [ ] `@require_tier("autopilot")` - Protect autopilot-only endpoints
- [ ] `@check_quota("statements")` - Verify statement upload quota
- [ ] `@check_quota("ai_calls")` - Verify AI usage quota

#### 3.3 Apply Access Control
- [ ] Protect `/recommendations` endpoint - require "optimizer" tier
- [ ] Protect `/vcm/*` endpoints - require "autopilot" tier (future)
- [ ] Protect `/files/upload` - check statement quota
- [ ] Protect AI categorization - check AI quota

---

### **Phase 4: Frontend - Subscription UI** (Est. 4-5 hours)

#### 4.1 Update Pricing Page (`app/[locale]/pricing/page.tsx`)
- [ ] Add "Subscribe" buttons to each tier card
- [ ] Button states:
  - Free tier: "Current Plan" (if user is analyst)
  - Optimizer: "Upgrade to Optimizer" or "Current Plan"
  - Autopilot: "Upgrade to Autopilot" or "Current Plan"
- [ ] On click: Call `POST /stripe/create-checkout-session`
- [ ] Redirect user to Stripe Checkout
- [ ] Show loading state during redirect

#### 4.2 Create Subscription Management Component (`components/subscription-status.tsx`)
- [ ] Display current tier badge
- [ ] Show subscription status (active, canceled, past_due)
- [ ] Show next billing date
- [ ] Show usage stats (statements used / limit)
- [ ] "Manage Subscription" button → Opens Stripe Customer Portal

#### 4.3 Create Upgrade Prompts (`components/upgrade-prompt.tsx`)
- [ ] Show when user hits quota limit
- [ ] Show when accessing locked features
- [ ] Modal with upgrade CTA
- [ ] Example: "You've used all 5 statements this month. Upgrade to Optimizer for 50/month!"

#### 4.4 Add to Navigation
- [ ] Show tier badge next to user email
- [ ] Add "Subscription" link in dropdown menu
- [ ] Link to `/account/subscription` page

#### 4.5 Create Account/Subscription Page (`app/[locale]/account/subscription/page.tsx`)
- [ ] Show current plan details
- [ ] Show billing history (from backend)
- [ ] "Upgrade" or "Manage" button
- [ ] Cancel subscription button (opens portal)

#### 4.6 Add Feature Locks
- [ ] Lock `/recommendations` page if tier < "optimizer"
- [ ] Lock `/vcm` page if tier < "autopilot"
- [ ] Show upgrade prompt instead of content

---

### **Phase 5: Frontend - Stripe Integration** (Est. 2 hours)

#### 5.1 Create Stripe API Client (`lib/stripe-client.ts`)
- [ ] `createCheckoutSession(tier)` - Get Stripe checkout URL
- [ ] `createPortalSession()` - Get customer portal URL
- [ ] `getSubscriptionStatus()` - Fetch current subscription

#### 5.2 Add Translation Keys
- [ ] Add to `locales/en.json`:
  ```json
  "subscription": {
    "title": "Subscription",
    "currentPlan": "Current Plan",
    "status": {
      "active": "Active",
      "canceled": "Canceled",
      "past_due": "Payment Failed"
    },
    "nextBilling": "Next billing date",
    "usage": "Usage",
    "manage": "Manage Subscription",
    "upgrade": "Upgrade Plan",
    "cancel": "Cancel Subscription",
    "quota": {
      "statements": "Statements uploaded",
      "ai_calls": "AI analyses used"
    },
    "locked": {
      "title": "Upgrade Required",
      "message": "This feature is available for {tier}+ subscribers",
      "cta": "Upgrade Now"
    }
  }
  ```
- [ ] Add Chinese translations

---

### **Phase 6: Testing** (Est. 2-3 hours)

#### 6.1 Backend Tests
- [ ] Test checkout session creation
- [ ] Test webhook handlers (use Stripe CLI)
- [ ] Test tier verification logic
- [ ] Test quota enforcement

#### 6.2 Frontend Tests
- [ ] Test upgrade flow (full checkout)
- [ ] Test customer portal access
- [ ] Test feature locks work correctly
- [ ] Test upgrade prompts display

#### 6.3 End-to-End Tests
- [ ] Subscribe to Optimizer tier
- [ ] Verify tier updated in database
- [ ] Verify recommendations page unlocked
- [ ] Access customer portal
- [ ] Cancel subscription
- [ ] Verify access downgraded

---

## 🗂️ File Structure

```
_monorepo/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── stripe.py                    # NEW
│   │   ├── schemas/
│   │   │   └── stripe.py                    # NEW
│   │   ├── services/
│   │   │   └── stripe_service.py            # NEW
│   │   ├── core/
│   │   │   └── permissions.py               # NEW
│   │   └── models/
│   │       └── models.py                    # MODIFY (add billing fields)
│   └── requirements.txt                     # MODIFY
│
└── frontend/
    ├── app/
    │   └── [locale]/
    │       ├── pricing/
    │       │   └── page.tsx                 # MODIFY
    │       └── account/
    │           └── subscription/
    │               └── page.tsx             # NEW
    ├── components/
    │   ├── subscription-status.tsx          # NEW
    │   └── upgrade-prompt.tsx               # NEW
    ├── lib/
    │   └── stripe-client.ts                 # NEW
    └── locales/
        ├── en.json                          # MODIFY
        └── zh.json                          # MODIFY
```

---

## 🔐 Security Considerations

- [ ] **Never expose secret keys** - Use environment variables
- [ ] **Verify webhook signatures** - Prevent fake events
- [ ] **Use HTTPS only** - Stripe requires SSL
- [ ] **Validate user ownership** - Users can only manage their own subscriptions
- [ ] **Handle failed payments gracefully** - Grace period before downgrade

---

## 🚀 Deployment Checklist

### Railway (Backend)
- [ ] Add Stripe environment variables
- [ ] Deploy backend with Stripe integration
- [ ] Configure webhook URL in Stripe Dashboard
- [ ] Test webhook delivery (Stripe Dashboard → Developers → Webhooks)

### Vercel (Frontend)
- [ ] Add Stripe publishable key to environment variables
- [ ] Deploy frontend with subscription UI
- [ ] Test checkout flow end-to-end
- [ ] Verify customer portal works

---

## 💰 Pricing Strategy

### Tier Comparison
| Feature | Analyst (Free) | Optimizer ($9.99/mo) | Autopilot ($29.99/mo) |
|---------|----------------|----------------------|------------------------|
| CSV Upload | ✅ | ✅ | ✅ |
| PDF Upload | ❌ | ✅ | ✅ |
| Statements/month | 5 | 50 | Unlimited |
| AI Categorization | 20/month | 200/month | Unlimited |
| Transaction View | ✅ | ✅ | ✅ |
| Dashboard Charts | Basic | Advanced | Advanced |
| Credit Card Recommendations | ❌ | ✅ | ✅ |
| Quarterly Reports | ❌ | ✅ | ✅ |
| Virtual Credit Manager | ❌ | ❌ | ✅ |
| Priority Support | ❌ | ❌ | ✅ |

---

## 📊 Success Metrics

### MVP Complete When:
- [ ] Users can subscribe to paid tiers
- [ ] Payment successfully processes via Stripe
- [ ] User tier updates in database
- [ ] Feature access controlled by tier
- [ ] Users can manage subscriptions (cancel/upgrade)
- [ ] Quota limits enforced
- [ ] Webhook events handled correctly

---

## 🐛 Known Edge Cases

1. **User subscribes then immediately cancels**:
   - Solution: Keep tier active until end of billing period

2. **Payment fails mid-subscription**:
   - Solution: Grace period (7 days), then downgrade to free

3. **User upgrades mid-billing cycle**:
   - Solution: Stripe handles prorated charges automatically

4. **User hits quota limit during trial**:
   - Solution: Show upgrade prompt immediately

---

## 💡 Business Value

### Revenue Potential:
- 100 users × $9.99 = $999/month
- 20 users × $29.99 = $600/month
- **Total**: ~$1,600/month MRR

### Conversion Strategy:
1. Free tier users hit quota → See upgrade prompt
2. Show value: "Unlock 45 more statements for $9.99/mo"
3. One-click checkout via Stripe
4. Immediate feature unlock

---

**Priority**: High  
**Revenue Impact**: Direct  
**Time Estimate**: 2-3 days  
**Status**: Ready to implement
