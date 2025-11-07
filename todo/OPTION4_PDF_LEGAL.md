# Option 4: PDF Upload & Legal Pages

**Goal**: Add PDF statement parsing + Privacy Policy & Terms of Service  
**Time Estimate**: 1-2 days  
**Priority**: Medium - Compliance & UX Completion

---

## 📋 Implementation Checklist

### **Part A: PDF Statement Upload** (Est. 6-8 hours)

#### A1. Backend - PDF Parser Setup (Est. 2-3 hours)

##### A1.1 Install Dependencies
- [ ] Add to `backend/requirements.txt`:
  ```
  PyMuPDF==1.23.8      # PDF text extraction
  pdfplumber==0.10.3   # Alternative PDF parser
  ```

##### A1.2 Create PDF Parser Service (`app/services/pdf_parser.py`)
- [ ] `extract_text_from_pdf(file_path)` - Extract raw text
- [ ] `parse_credit_card_statement(text)` - Identify statement type
- [ ] `extract_transactions_from_text(text)` - Parse transaction data
- [ ] Bank-specific parsers:
  - `parse_rbc_pdf(text)` - RBC statement format
  - `parse_cibc_pdf(text)` - CIBC statement format
  - `parse_mbna_pdf(text)` - MBNA statement format
  - `parse_generic_pdf(text)` - Fallback for unknown formats

##### A1.3 PDF Parsing Logic
- [ ] Identify institution by keywords:
  ```python
  if "Royal Bank of Canada" in text:
      return parse_rbc_pdf(text)
  elif "CIBC" in text:
      return parse_cibc_pdf(text)
  ```
- [ ] Extract account info (last 4 digits, statement period)
- [ ] Extract transactions using regex patterns:
  - Date: `\d{2}/\d{2}/\d{4}` or `\d{4}-\d{2}-\d{2}`
  - Amount: `\$?\d+\.\d{2}` or `\d+,\d{3}\.\d{2}`
  - Merchant: Text before amount
- [ ] Handle multi-page statements
- [ ] Handle different date formats

##### A1.4 Update File Upload API
- [ ] Modify `app/api/files.py`:
  - Accept `application/pdf` MIME type
  - Call `pdf_parser.parse_statement()` if PDF
  - Store extracted transactions same as CSV
- [ ] Add PDF validation:
  - Max file size: 10MB
  - Must contain parseable text (not scanned image)
  - Must contain transaction data

##### A1.5 Error Handling
- [ ] If PDF is scanned image → Return error: "Please upload text-based PDF or use OCR"
- [ ] If format unrecognized → Suggest manual CSV export
- [ ] Log parsing errors for future improvements

---

#### A2. Frontend - PDF Upload Support (Est. 2-3 hours)

##### A2.1 Update Upload Page (`app/[locale]/upload/page.tsx`)
- [ ] Update accepted file types: `accept=".pdf,.csv"`
- [ ] Update file validation to allow PDF
- [ ] Show PDF icon for PDF files in upload list
- [ ] Update upload instructions:
  ```
  "Upload your bank statement (PDF or CSV format)"
  "Supported: RBC, CIBC, MBNA, PC Financial, Tangerine"
  ```

##### A2.2 Update Translation Keys
- [ ] Modify `locales/en.json`:
  ```json
  "upload": {
    "subtitle": "Accepted formats: PDF, CSV",
    "supportedFormats": "Supported: PDF, CSV",
    "pdfNote": "PDF must be text-based (not scanned)",
    "messages": {
      "pdfParseError": "Unable to parse PDF. Please export as CSV or contact support."
    }
  }
  ```

##### A2.3 Add PDF-Specific Errors
- [ ] Handle parse failure: Show user-friendly message
- [ ] Suggest alternatives: "Try exporting as CSV from online banking"
- [ ] Link to help doc: "How to export statements"

---

#### A3. Testing PDF Parser (Est. 2 hours)

##### A3.1 Collect Sample PDFs
- [ ] Download sample statements from:
  - RBC credit card
  - CIBC credit card
  - MBNA credit card
  - PC Financial
  - Tangerine

##### A3.2 Create Test Cases
- [ ] Test PDF with 5 transactions
- [ ] Test PDF with 50+ transactions
- [ ] Test multi-page PDF
- [ ] Test scanned PDF (should fail gracefully)
- [ ] Test corrupt PDF
- [ ] Test non-statement PDF

##### A3.3 Validate Extracted Data
- [ ] Verify all transactions extracted
- [ ] Verify dates parsed correctly
- [ ] Verify amounts match statement
- [ ] Verify merchant names extracted

---

### **Part B: Legal Pages** (Est. 4-6 hours)

#### B1. Privacy Policy Page (Est. 2-3 hours)

##### B1.1 Write Privacy Policy Content
- [ ] Create `docs/privacy_policy_en.md`:
  ```markdown
  # Privacy Policy
  
  Last Updated: [Date]
  
  ## Information We Collect
  - Email address (for account creation)
  - Financial statements (uploaded by you)
  - Transaction data (parsed from statements)
  - Usage analytics (page views, feature usage)
  
  ## How We Use Your Information
  - Categorize transactions
  - Generate spending insights
  - Recommend credit cards
  - Improve our service
  
  ## Data Storage & Security
  - All data encrypted at rest (AES-256)
  - Stored on secure servers (Railway/AWS)
  - Regular security audits
  
  ## Third-Party Services
  - OpenAI: Transaction categorization (anonymized data)
  - Stripe: Payment processing
  - Vercel: Website hosting
  
  ## Your Rights
  - Access your data
  - Delete your account
  - Export your data
  - Opt out of analytics
  
  ## Contact
  support@creditsphere.com
  ```
- [ ] Create Chinese version: `docs/privacy_policy_zh.md`

##### B1.2 Create Privacy Page Component
- [ ] Create `app/[locale]/privacy/page.tsx`:
  ```tsx
  import { useTranslations } from 'next-intl';
  
  export default function PrivacyPage() {
    const t = useTranslations('legal.privacy');
    
    return (
      <div className="max-w-4xl mx-auto py-12 px-4">
        <h1>{t('title')}</h1>
        <div className="prose dark:prose-invert">
          {/* Render markdown content */}
        </div>
      </div>
    );
  }
  ```

##### B1.3 Add Translation Keys
- [ ] Add to `locales/en.json`:
  ```json
  "legal": {
    "privacy": {
      "title": "Privacy Policy",
      "lastUpdated": "Last Updated",
      "sections": {
        "collection": "Information We Collect",
        "usage": "How We Use Your Information",
        "storage": "Data Storage & Security",
        "thirdParty": "Third-Party Services",
        "rights": "Your Rights",
        "contact": "Contact Us"
      }
    }
  }
  ```

---

#### B2. Terms of Service Page (Est. 2-3 hours)

##### B2.1 Write Terms of Service Content
- [ ] Create `docs/terms_of_service_en.md`:
  ```markdown
  # Terms of Service
  
  Last Updated: [Date]
  
  ## Acceptance of Terms
  By using CreditSphere, you agree to these terms.
  
  ## Service Description
  - Transaction categorization
  - Spending analytics
  - Credit card recommendations
  - Virtual Credit Manager (paid tiers)
  
  ## User Responsibilities
  - Provide accurate information
  - Secure your account credentials
  - Do not share your account
  - Comply with credit card issuer terms
  
  ## Disclaimers
  - Recommendations are informational only
  - Not financial advice
  - Credit approval not guaranteed
  - We are not liable for credit decisions
  
  ## Intellectual Property
  - All content is ©2025 CreditSphere
  - User data remains user's property
  
  ## Termination
  - You can cancel anytime
  - We may terminate for violations
  
  ## Limitation of Liability
  - Service provided "as is"
  - No warranties expressed or implied
  
  ## Governing Law
  - Laws of Ontario, Canada
  
  ## Contact
  legal@creditsphere.com
  ```
- [ ] Create Chinese version: `docs/terms_of_service_zh.md`

##### B2.2 Create Terms Page Component
- [ ] Create `app/[locale]/terms/page.tsx`:
  ```tsx
  import { useTranslations } from 'next-intl';
  
  export default function TermsPage() {
    const t = useTranslations('legal.terms');
    
    return (
      <div className="max-w-4xl mx-auto py-12 px-4">
        <h1>{t('title')}</h1>
        <div className="prose dark:prose-invert">
          {/* Render markdown content */}
        </div>
      </div>
    );
  }
  ```

##### B2.3 Add Translation Keys
- [ ] Add to `locales/en.json`:
  ```json
  "legal": {
    "terms": {
      "title": "Terms of Service",
      "lastUpdated": "Last Updated",
      "sections": {
        "acceptance": "Acceptance of Terms",
        "service": "Service Description",
        "responsibilities": "User Responsibilities",
        "disclaimers": "Disclaimers",
        "ip": "Intellectual Property",
        "termination": "Termination",
        "liability": "Limitation of Liability",
        "law": "Governing Law",
        "contact": "Contact Us"
      }
    }
  }
  ```

---

#### B3. Update Footer & Navigation (Est. 1 hour)

##### B3.1 Update Footer Component
- [ ] Modify `components/footer.tsx` (or homepage footer):
  ```tsx
  <footer>
    <Link href={`/${locale}/privacy`}>Privacy Policy</Link>
    <Link href={`/${locale}/terms`}>Terms of Service</Link>
    <Link href={`/${locale}/contact`}>Contact</Link>
  </footer>
  ```

##### B3.2 Update Homepage Links
- [ ] Replace "Coming Soon" text with actual links
- [ ] Test navigation from homepage to legal pages

---

### **Part C: Testing & Deployment** (Est. 2 hours)

#### C1. Test PDF Upload
- [ ] Upload PDF statement
- [ ] Verify transactions extracted
- [ ] Check error handling for bad PDFs
- [ ] Test with different banks

#### C2. Test Legal Pages
- [ ] Verify Privacy page loads
- [ ] Verify Terms page loads
- [ ] Test footer links work
- [ ] Test responsive design
- [ ] Test translations (EN/CN)

#### C3. Deploy
- [ ] Push to GitHub
- [ ] Railway auto-deploys backend
- [ ] Vercel auto-deploys frontend
- [ ] Verify production works

---

## 🗂️ File Structure

```
_monorepo/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   └── pdf_parser.py            # NEW
│   │   └── api/
│   │       └── files.py                 # MODIFY (add PDF support)
│   └── requirements.txt                 # MODIFY
│
├── frontend/
│   ├── app/
│   │   └── [locale]/
│   │       ├── privacy/
│   │       │   └── page.tsx             # NEW
│   │       ├── terms/
│   │       │   └── page.tsx             # NEW
│   │       └── upload/
│   │           └── page.tsx             # MODIFY
│   ├── locales/
│   │   ├── en.json                      # MODIFY
│   │   └── zh.json                      # MODIFY
│   └── components/
│       └── footer.tsx                   # MODIFY
│
└── docs/
    ├── privacy_policy_en.md             # NEW
    ├── privacy_policy_zh.md             # NEW
    ├── terms_of_service_en.md           # NEW
    └── terms_of_service_zh.md           # NEW
```

---

## 🔐 Legal Compliance Notes

### Privacy Policy Must Include:
- [ ] Data collection practices
- [ ] Data usage purposes
- [ ] Data retention policy
- [ ] User rights (access, deletion, export)
- [ ] Third-party disclosure
- [ ] Security measures
- [ ] Cookie policy (if applicable)
- [ ] Contact information

### Terms of Service Must Include:
- [ ] Service description
- [ ] User obligations
- [ ] Disclaimers (not financial advice)
- [ ] Limitation of liability
- [ ] Intellectual property rights
- [ ] Termination conditions
- [ ] Governing law
- [ ] Dispute resolution

### GDPR Considerations (if EU users):
- [ ] Right to be forgotten
- [ ] Data portability
- [ ] Consent mechanisms
- [ ] Data breach notification

---

## 📊 Success Metrics

### Part A Complete When:
- [ ] PDF files upload successfully
- [ ] Transactions extracted from PDF
- [ ] At least 3 banks supported
- [ ] Error messages user-friendly
- [ ] No 404 on upload page

### Part B Complete When:
- [ ] Privacy page accessible
- [ ] Terms page accessible
- [ ] Footer links work
- [ ] Content complete (EN/CN)
- [ ] Mobile responsive

---

## 🚀 Quick Wins

### Day 1:
- Write legal content (3 hours)
- Create legal pages (2 hours)
- Update footer links (1 hour)

### Day 2:
- Implement PDF parser (4 hours)
- Test with sample PDFs (2 hours)
- Deploy to production (1 hour)

---

**Priority**: Medium  
**Compliance Impact**: High  
**User Experience**: Improved  
**Time Estimate**: 1-2 days  
**Status**: Ready to implement
