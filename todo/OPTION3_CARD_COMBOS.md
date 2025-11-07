# Option 3: Credit Card Combo Recommendation System

**Goal**: Recommend optimal credit card combinations based on spending patterns  
**Time Estimate**: 2 days  
**Priority**: Medium-High - User Value Enhancement

---

## 🎯 Core Concept

Instead of recommending single cards, recommend **combinations** that maximize rewards:
- **Example 1**: RBC ION+ (5% on groceries) → Transfer to RBC Avion (buy flights)
- **Example 2**: MBNA World Elite (rent via CHEXY) + Tangerine Cash Back (gas/groceries)
- **Example 3**: Amex Cobalt (food delivery 5x) + PC Optimum (groceries 3%)

---

## 📋 Implementation Checklist

### **Phase 1: Database - Combo Strategies** (Est. 2-3 hours)

#### 1.1 Create CardCombo Model
- [ ] Add to `app/models/models.py`:
  ```python
  class CardCombo(Base):
      __tablename__ = "card_combos"
      
      id = Column(Integer, primary_key=True)
      name = Column(String(200), nullable=False)  # "RBC Points Maximizer"
      description = Column(Text)  # How the combo works
      
      # Cards in combo (list of card IDs)
      card_ids = Column(JSON, nullable=False)  # [1, 5, 12]
      
      # Target categories (which spending this combo optimizes)
      optimized_categories = Column(JSON)  # ["groceries", "gas", "travel"]
      
      # Strategy explanation
      strategy = Column(JSON)  # {
          # "groceries": {"use_card_id": 1, "rate": "5%"},
          # "gas": {"use_card_id": 5, "rate": "3%"},
          # "travel": {"action": "transfer_points", "from": 1, "to": 12}
      # }
      
      # Requirements
      min_income = Column(Integer)  # Minimum income to qualify
      min_monthly_spend = Column(Integer)  # Minimum spend to make combo worthwhile
      annual_fees_total = Column(Numeric(10, 2))  # Sum of all card fees
      
      # Estimated value
      estimated_annual_value = Column(Numeric(10, 2))  # Expected rewards per year
      
      # Metadata
      difficulty = Column(String(20))  # "easy", "medium", "complex"
      tags = Column(JSON)  # ["points_transfer", "cashback", "travel"]
      is_active = Column(Boolean, default=True)
      created_at = Column(DateTime(timezone=True), server_default=func.now())
  ```

#### 1.2 Create Migration
- [ ] Generate Alembic migration:
  ```bash
  cd _monorepo/backend
  alembic revision --autogenerate -m "Add CardCombo model"
  alembic upgrade head
  ```

#### 1.3 Seed Combo Data
- [ ] Create `backend/app/data/card_combos.yaml`:
  ```yaml
  combos:
    - name: "RBC Points Maximizer"
      description: "Earn 5% on groceries with ION+, transfer to Avion for 25% travel bonus"
      card_ids: [1, 2]  # ION+ and Avion card IDs
      optimized_categories: ["groceries", "travel"]
      strategy:
        groceries:
          use_card: "RBC ION+"
          rate: "5%"
          note: "Earn points on groceries"
        travel:
          action: "Transfer ION+ points to Avion (1:1 ratio)"
          bonus: "Redeem Avion points for flights at 25% premium"
      min_income: 60000
      min_monthly_spend: 500
      annual_fees_total: 120.00
      estimated_annual_value: 850.00
      difficulty: "medium"
      tags: ["points_transfer", "travel", "groceries"]
    
    - name: "Rent Optimizer"
      description: "Pay rent via CHEXY with MBNA World Elite for cash back"
      card_ids: [5]
      optimized_categories: ["rent", "recurring_bills"]
      strategy:
        rent:
          use_card: "MBNA World Elite Mastercard"
          rate: "2% cash back"
          method: "Pay via CHEXY.ca (3rd party service)"
      min_income: 80000
      min_monthly_spend: 1500
      annual_fees_total: 0.00
      estimated_annual_value: 360.00
      difficulty: "easy"
      tags: ["cashback", "rent"]
    
    # Add 5-10 more combos...
  ```
- [ ] Create seeding script `backend/app/scripts/seed_combos.py`

---

### **Phase 2: Backend - Combo Recommendation Logic** (Est. 3-4 hours)

#### 2.1 Create Combo Schemas (`app/schemas/combos.py`)
- [ ] `CardComboResponse` - Full combo details
- [ ] `ComboRecommendationRequest` - User spending data
- [ ] `ComboRecommendationResponse` - List of recommended combos with scores

#### 2.2 Create Combo Service (`app/services/combo_service.py`)
- [ ] `get_all_combos()` - Fetch all active combos
- [ ] `get_combo_by_id(combo_id)` - Get specific combo
- [ ] `recommend_combos(user_id, spending_data)` - Recommend best combos
- [ ] `calculate_combo_value(combo, user_spending)` - Estimate annual value
- [ ] `check_combo_eligibility(combo, user_income)` - Verify user qualifies

#### 2.3 Recommendation Algorithm (`recommend_combos()`)
- [ ] Input: User's spending breakdown by category
- [ ] Logic:
  1. Fetch all active combos
  2. For each combo:
     - Check if user qualifies (income, spend thresholds)
     - Calculate potential value based on user's spending
     - Compute ROI: `(value - fees) / fees`
  3. Rank combos by:
     - Highest estimated value
     - Best ROI
     - Lowest difficulty (if tied)
  4. Return top 5 combos
- [ ] Output: List of combos with personalized value estimates

#### 2.4 Create Combo API (`app/api/combos.py`)
- [ ] `GET /combos` - List all combos
- [ ] `GET /combos/{id}` - Get specific combo details
- [ ] `POST /combos/recommend` - Get personalized recommendations
- [ ] `GET /combos/category/{category}` - Combos optimized for specific category

---

### **Phase 3: Frontend - Combo UI** (Est. 4-5 hours)

#### 3.1 Update Recommendations Page (`app/[locale]/recommendations/page.tsx`)
- [ ] Add new section: "Recommended Card Combinations"
- [ ] Show top 3 combos above single card recommendations
- [ ] Each combo card shows:
  - Combo name and description
  - Cards included (with logos)
  - Strategy summary
  - Estimated annual value
  - Annual fees
  - Net benefit (value - fees)
  - Difficulty badge
  - "Learn More" button

#### 3.2 Create Combo Detail Modal (`components/combos/combo-detail-modal.tsx`)
- [ ] Display full combo strategy
- [ ] Step-by-step guide:
  - "1. Apply for RBC ION+"
  - "2. Use for all grocery purchases"
  - "3. Transfer points to Avion quarterly"
  - "4. Redeem for flights at 25% bonus"
- [ ] Show cards involved with links to apply
- [ ] Display requirements (income, spend)
- [ ] Show estimated value calculation
- [ ] "Apply Now" CTA buttons

#### 3.3 Create Combo Card Component (`components/combos/combo-card.tsx`)
- [ ] Visual card layout
- [ ] Display combo name, cards, value
- [ ] Color-coded difficulty badge
- [ ] Expandable details section
- [ ] Share button (future)

#### 3.4 Add to Dashboard
- [ ] Show "Recommended Combo" widget
- [ ] Display top 1 combo based on user's spending
- [ ] "View All Combos" link to recommendations page

#### 3.5 Add Translation Keys
- [ ] Add to `locales/en.json`:
  ```json
  "combos": {
    "title": "Recommended Card Combinations",
    "subtitle": "Maximize rewards by using multiple cards strategically",
    "estimatedValue": "Estimated Annual Value",
    "annualFees": "Total Annual Fees",
    "netBenefit": "Net Benefit",
    "difficulty": {
      "easy": "Easy",
      "medium": "Medium",
      "complex": "Advanced"
    },
    "strategy": "Strategy",
    "requirements": "Requirements",
    "minIncome": "Minimum Income",
    "minSpend": "Recommended Monthly Spend",
    "cardsNeeded": "Cards Needed",
    "howItWorks": "How It Works",
    "applyNow": "Apply for Cards",
    "learnMore": "Learn More",
    "personalizedFor": "Based on your spending patterns"
  }
  ```
- [ ] Add Chinese translations

---

### **Phase 4: Combo Examples Database** (Est. 2-3 hours)

#### 4.1 Create 10 Real-World Combos
1. **RBC Points Maximizer** (ION+ → Avion)
2. **Rent Optimizer** (MBNA World Elite via CHEXY)
3. **Grocery King** (PC Optimum + Tangerine)
4. **Travel Hacker** (Amex Cobalt + Aeroplan)
5. **Gas Saver** (Triangle World Elite + Canadian Tire)
6. **Dining Pro** (Amex Cobalt + Scotiabank Gold)
7. **Amazon Maximizer** (Amazon Visa + Tangerine)
8. **Student Combo** (Tangerine + BMO SPC)
9. **Cashback Champion** (SimplyCash + Rogers)
10. **Points Transfer Master** (Multiple RBC cards)

#### 4.2 Document Each Combo
- [ ] Write clear strategy descriptions
- [ ] Calculate realistic value estimates
- [ ] Define eligibility requirements
- [ ] Create step-by-step guides
- [ ] Add disclaimers (fees, terms)

---

### **Phase 5: Testing** (Est. 2 hours)

#### 5.1 Backend Tests
- [ ] Test combo recommendation algorithm
- [ ] Test value calculation with sample spending
- [ ] Test eligibility filtering
- [ ] Test API endpoints

#### 5.2 Frontend Tests
- [ ] Test combo cards display correctly
- [ ] Test modal opens with full details
- [ ] Test responsive design
- [ ] Test translations

#### 5.3 End-to-End
- [ ] Upload transactions
- [ ] View recommendations page
- [ ] Verify combos match spending patterns
- [ ] Open combo detail modal
- [ ] Verify value calculations

---

## 🗂️ File Structure

```
_monorepo/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── combos.py                    # NEW
│   │   ├── schemas/
│   │   │   └── combos.py                    # NEW
│   │   ├── services/
│   │   │   └── combo_service.py             # NEW
│   │   ├── models/
│   │   │   └── models.py                    # MODIFY (add CardCombo)
│   │   ├── data/
│   │   │   └── card_combos.yaml             # NEW
│   │   └── scripts/
│   │       └── seed_combos.py               # NEW
│   └── alembic/
│       └── versions/
│           └── XXX_add_card_combo.py        # NEW MIGRATION
│
└── frontend/
    ├── app/
    │   └── [locale]/
    │       └── recommendations/
    │           └── page.tsx                 # MODIFY
    ├── components/
    │   └── combos/
    │       ├── combo-card.tsx               # NEW
    │       └── combo-detail-modal.tsx       # NEW
    └── locales/
        ├── en.json                          # MODIFY
        └── zh.json                          # MODIFY
```

---

## 💡 Business Value

### User Benefits:
1. **Higher Rewards**: 2-3x more value than single cards
2. **Education**: Learn advanced credit card strategies
3. **Personalization**: Recommendations based on actual spending
4. **Simplicity**: Complex strategies made easy to understand

### Marketing Angle:
- Blog posts: "Top 10 Credit Card Combos in Canada"
- YouTube videos: "How I earn $2,000/year with 2 cards"
- Social media: Share combo success stories
- SEO: Rank for "best credit card combination Canada"

### Competitive Advantage:
- **Unique**: No other app offers combo recommendations
- **Viral Potential**: Users share profitable combos
- **Content Marketing**: Each combo = blog post opportunity

---

## 📊 Success Metrics

### MVP Complete When:
- [ ] 10 combos seeded in database
- [ ] Combo recommendation algorithm working
- [ ] Recommendations page shows combos
- [ ] Combo detail modal functional
- [ ] Value calculations accurate
- [ ] Translations complete

---

## 🚀 Quick Wins

### Phase 1 MVP (Day 1):
- Create CardCombo model
- Seed 3 simple combos
- Build basic recommendation endpoint

### Phase 2 Polish (Day 2):
- Add 7 more combos
- Build frontend UI
- Test end-to-end

---

**Priority**: Medium-High  
**User Impact**: High  
**Marketing Value**: Very High  
**Time Estimate**: 2 days  
**Status**: Ready to implement
