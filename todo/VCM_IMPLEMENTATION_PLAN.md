# Virtual Credit Manager (VCM) Implementation Plan

**Feature**: Credit Build & Virtual Credit Card Aggregation  
**Goal**: Allow users to combine multiple credit cards into one virtual card with optimized utilization (10-30% per card)

---

## 🎯 Core Concept

Users can:
1. Link multiple physical credit cards to the system
2. View their total combined credit limit (Virtual Credit Card)
3. Get recommendations on how to distribute spending across cards
4. Maintain healthy 10-30% utilization on each card (credit building)
5. Prioritize spending on high-limit cards first

---

## 📋 Implementation Checklist

### **Phase 1: Backend Foundation** (Est. 2-3 hours)

#### 1.1 Database Migration
- [ ] Add new fields to `Card` model:
  - `current_balance` (Numeric) - Current amount owed
  - `available_credit` (Numeric) - Calculated: credit_limit - current_balance
  - `utilization_rate` (Float) - Calculated: (current_balance / credit_limit) * 100
  - `vcm_enabled` (Boolean) - Whether card is enrolled in VCM
  - `vcm_priority` (Integer) - Priority order for spending allocation

#### 1.2 Create VCM Schemas
- [ ] Create `app/schemas/vcm.py`:
  - `CardEnrollRequest` - Enroll card in VCM
  - `VirtualCreditResponse` - Show total virtual credit
  - `AllocationRequest` - Request spending allocation
  - `AllocationResponse` - Recommended payment distribution
  - `CardUtilizationResponse` - Per-card utilization stats

#### 1.3 Create VCM Service
- [ ] Create `app/services/vcm_service.py`:
  - `calculate_total_virtual_credit()` - Sum all enrolled cards
  - `calculate_optimal_allocation()` - Distribute amount across cards (10-30% rule)
  - `get_card_priorities()` - Sort cards by limit (high to low)
  - `simulate_allocation()` - Preview allocation without saving
  - `check_utilization_health()` - Validate if allocation is safe

#### 1.4 Create VCM API
- [ ] Create `app/api/vcm.py`:
  - `POST /vcm/cards/enroll` - Enroll card in VCM
  - `POST /vcm/cards/unenroll` - Remove card from VCM
  - `GET /vcm/status` - Get virtual credit summary
  - `POST /vcm/allocate` - Get spending allocation recommendation
  - `GET /vcm/cards` - List all VCM-enrolled cards with utilization

---

### **Phase 2: Backend Logic** (Est. 3-4 hours)

#### 2.1 Allocation Algorithm (`calculate_optimal_allocation()`)
- [ ] Input: Total purchase amount, list of enrolled cards
- [ ] Logic:
  1. Sort cards by credit limit (descending) - prioritize high-limit cards
  2. For each card, calculate max safe allocation (30% utilization target)
  3. Allocate to cards until amount is fully distributed
  4. Ensure no card exceeds 30% utilization after allocation
  5. If amount too large, return warning (requires more credit)
- [ ] Output: Dictionary of `{card_id: amount_to_charge, ...}`

#### 2.2 Utilization Health Check
- [ ] For each enrolled card:
  - Calculate current utilization: `(current_balance / credit_limit) * 100`
  - Flag cards with >30% utilization as "high"
  - Flag cards with >70% utilization as "critical"
- [ ] Suggest balance transfers if cards are over-utilized

#### 2.3 Transaction Syncing
- [ ] Update card balances automatically when new transactions are uploaded
- [ ] Recalculate utilization rates after each statement parse
- [ ] Store historical utilization in `meta_data` JSON field (for trends)

---

### **Phase 3: Frontend UI** (Est. 4-5 hours)

#### 3.1 Create VCM Page (`frontend/app/[locale]/vcm/page.tsx`)
- [ ] Page structure:
  - **Section 1**: Virtual Credit Card Overview
    - Display total virtual credit limit (sum of all cards)
    - Display total available credit
    - Display average utilization across all cards
  - **Section 2**: Enrolled Cards List
    - Table showing each card: issuer, limit, balance, utilization, status
    - Color-coded utilization (green <30%, yellow 30-70%, red >70%)
    - Button to enroll/unenroll cards
  - **Section 3**: Spending Allocator Tool
    - Input: "I want to spend $X"
    - Button: "Show Optimal Allocation"
    - Output: Breakdown showing how to split $X across cards

#### 3.2 Create VCM Components
- [ ] `components/vcm/virtual-credit-card.tsx`:
  - Visual card showing total virtual credit
  - Progress bar for total utilization
- [ ] `components/vcm/card-list.tsx`:
  - Table of enrolled cards with utilization bars
  - Enroll/unenroll toggle buttons
- [ ] `components/vcm/allocation-calculator.tsx`:
  - Input field for purchase amount
  - "Calculate" button
  - Results table showing per-card allocation
  - Visual representation (pie chart or bars)

#### 3.3 Add Translation Keys
- [ ] Add to `locales/en.json`:
  ```json
  "vcm": {
    "title": "Virtual Credit Manager",
    "subtitle": "Optimize your credit card spending",
    "virtualCard": {
      "totalLimit": "Total Virtual Credit",
      "available": "Available Credit",
      "utilization": "Average Utilization"
    },
    "cards": {
      "enrolled": "Enrolled Cards",
      "issuer": "Issuer",
      "limit": "Limit",
      "balance": "Balance",
      "utilization": "Utilization",
      "status": "Status",
      "enroll": "Enroll",
      "unenroll": "Unenroll"
    },
    "allocator": {
      "title": "Spending Allocator",
      "inputLabel": "I want to spend",
      "calculate": "Calculate Optimal Allocation",
      "results": "Recommended Allocation",
      "card": "Card",
      "amount": "Amount to Charge",
      "newUtilization": "New Utilization"
    },
    "health": {
      "healthy": "Healthy",
      "warning": "High Utilization",
      "critical": "Critical"
    }
  }
  ```
- [ ] Add Chinese translations to `locales/zh.json`

#### 3.4 Navigation Updates
- [ ] Add VCM link to navigation (`components/navigation.tsx`)
- [ ] Add VCM icon (e.g., credit card stack icon)
- [ ] Gate access for Autopilot tier only (if implementing pricing)

---

### **Phase 4: Advanced Features** (Optional - Est. 2-3 hours)

#### 4.1 Autopilot Mode
- [ ] Create `POST /vcm/autopilot/enable` endpoint
- [ ] Store user preference: `auto_allocate = true`
- [ ] When user makes a purchase (future Plaid integration):
  - Automatically split payment across cards
  - Send payment instructions to each card issuer

#### 4.2 Credit Building Insights
- [ ] Show historical utilization chart (last 6 months)
- [ ] Show credit score impact simulation
- [ ] Provide tips: "Keep utilization below 30% to improve credit score"

#### 4.3 Balance Transfer Suggestions
- [ ] Detect over-utilized cards (>70%)
- [ ] Suggest transferring balance to under-utilized cards
- [ ] Calculate potential interest savings

---

## 🗂️ File Structure

```
_monorepo/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── vcm.py                    # NEW
│   │   ├── schemas/
│   │   │   └── vcm.py                    # NEW
│   │   ├── services/
│   │   │   └── vcm_service.py            # NEW
│   │   └── models/
│   │       └── models.py                 # MODIFY (add fields to Card)
│   └── alembic/
│       └── versions/
│           └── XXX_add_vcm_fields.py     # NEW MIGRATION
│
└── frontend/
    ├── app/
    │   └── [locale]/
    │       └── vcm/
    │           └── page.tsx              # NEW
    ├── components/
    │   └── vcm/
    │       ├── virtual-credit-card.tsx   # NEW
    │       ├── card-list.tsx             # NEW
    │       └── allocation-calculator.tsx # NEW
    └── locales/
        ├── en.json                       # MODIFY
        └── zh.json                       # MODIFY
```

---

## 🧪 Testing Checklist

### Backend Tests
- [ ] Test allocation algorithm with 2 cards
- [ ] Test allocation algorithm with 5+ cards
- [ ] Test edge case: amount > total available credit
- [ ] Test edge case: all cards at 30% utilization
- [ ] Test utilization calculation accuracy

### Frontend Tests
- [ ] Test VCM page loads with no cards enrolled
- [ ] Test enrolling/unenrolling cards
- [ ] Test allocation calculator with valid amount
- [ ] Test allocation calculator with amount too large
- [ ] Test responsive design (mobile)

---

## 📊 Success Metrics

### MVP Complete When:
- [ ] User can enroll at least 2 credit cards
- [ ] User can view total virtual credit limit
- [ ] User can input purchase amount and see allocation
- [ ] Allocation follows 10-30% utilization rule
- [ ] High-limit cards are prioritized
- [ ] Frontend displays utilization with color coding
- [ ] All translations complete (EN/CN)

---

## 🚀 Deployment Steps

1. **Database Migration**:
   ```bash
   # Generate migration
   cd _monorepo/backend
   alembic revision --autogenerate -m "Add VCM fields to Card model"
   
   # Apply migration locally
   alembic upgrade head
   
   # Apply to production (Railway)
   # Run via Railway console or push to trigger auto-migration
   ```

2. **Backend Deployment**:
   - Push to GitHub
   - Railway auto-deploys backend

3. **Frontend Deployment**:
   - Push to GitHub
   - Vercel auto-deploys frontend

4. **Verify**:
   - Test `/vcm` page loads
   - Test API endpoints via Swagger docs (`/docs`)
   - Test end-to-end flow

---

## 💡 Business Value

### User Benefits:
1. **Credit Building**: Automatically maintain healthy utilization ratios
2. **Convenience**: One "virtual" card replaces juggling multiple cards
3. **Optimization**: Always use the best card for credit health
4. **Education**: Learn optimal credit card management

### Competitive Advantage:
- **Unique Feature**: No other personal finance app offers virtual credit aggregation
- **Premium Tier Justification**: Strong reason for users to upgrade to Autopilot ($29.99/mo)
- **Retention**: High switching cost once users enroll multiple cards

---

## 📝 Notes

- **Security**: All card data is stored encrypted (use `encrypted_access_token` pattern from Account model)
- **Compliance**: VCM is advisory only - we don't actually charge cards (requires Plaid for that)
- **Phase 1 MVP**: Manual allocation recommendations only
- **Phase 2 Future**: Full autopilot with Plaid integration

---

**Estimated Total Time**: 12-15 hours for MVP (Phase 1-3)  
**Priority**: High - Core differentiator feature  
**Status**: Ready to implement
