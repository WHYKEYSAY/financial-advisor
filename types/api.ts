// Auth Types
export interface User {
  id: number;
  email: string;
  name?: string;
  locale?: string;
  tier?: 'analyst' | 'optimizer' | 'autopilot';
  created_at?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export type MeResponse = User;

// File Types
export interface UploadResult {
  id: number;
  user_id: number;
  source_type: string;
  file_path: string;
  parsed: boolean;
  period_start?: string;
  period_end?: string;
  created_at: string;
}

export interface StatementFile {
  id: number;
  source_type: string;
  file_path: string;
  parsed: boolean;
  period_start?: string;
  period_end?: string;
  status?: 'processing' | 'ready' | 'failed';
  created_at: string;
}

// Transaction Types
export interface Transaction {
  id: number;
  date: string;
  amount: number;
  currency?: string;
  category: string;
  subcategory?: string;
  merchant_name: string;
  raw_merchant?: string;
  tags?: string[];
  confidence?: number;
}

export interface TransactionsResponse {
  transactions: Transaction[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface CategoryBreakdown {
  category: string;
  total: number;
  count: number;
  percentage: number;
}

export interface BreakdownResponse {
  categories: CategoryBreakdown[];
  start_date: string;
  end_date: string;
}

export interface TransactionStats {
  total_transactions: number;
  total_spent: number;
  average_transaction: number;
  top_merchant?: string;
  top_category?: string;
  date_range?: {
    start: string;
    end: string;
  };
}

// VCM (Virtual Credit Manager) Types
export type HealthStatus = 'optimal' | 'underutilized' | 'elevated' | 'high';

export interface CardSummary {
  card_id: number;
  issuer: string;
  product: string;
  credit_limit: number;
  current_balance: number;
  utilization_rate: number;
  health_status: HealthStatus;
  last4?: string | null;
}

export interface CreditOverview {
  total_credit_limit: number;
  total_used: number;
  overall_utilization: number;
  health_status: HealthStatus;
  cards_summary: CardSummary[];
}

// Account Types
export interface Account {
  institution: string;
  account_type: string;
  statement_count: number;
  transaction_count: number;
  first_statement?: string | null;
  last_statement?: string | null;
}

export interface AccountsListResponse {
  accounts: Account[];
  total: number;
}

export interface AccountSummary {
  total_accounts: number;
  active_cards: number;
}

// Error Types
export interface ErrorResponse {
  detail: string | Record<string, any>;
  message?: string;
  code?: string;
  errors?: Record<string, string[]>;
}

// Quota Types
export interface QuotaStatus {
  tier: string;
  ai_calls_limit: number;
  ai_calls_used: number;
  ai_calls_remaining: number;
  files_parsed: number;
  period_start: string;
  period_end: string;
  reset_in_days: number;
}

// Credit Card Recommendation Types
export interface CardRecommendation {
  nav: number;
  annual_rewards: number;
  welcome_bonus_amortized: number;
  annual_fee: number;
  card_id: number;
  issuer: string;
  product_name: string;
  card_network?: string;
  min_income?: number;
  min_household_income?: number;
  apply_url?: string | null;
  rewards?: unknown;
  image_url?: string | null;
}

// Account Types
export type AccountType = 'credit_card' | 'checking' | 'savings' | string;

export interface Account {
  institution: string;
  account_type: AccountType;
  statement_count: number;
  transaction_count: number;
  first_statement: string | null;
  last_statement: string | null;
}

export interface AccountListResponse {
  accounts: Account[];
  total: number;
}

export interface AccountSummaryAccount {
  institution: string;
  total_spent: number;
  total_payments: number;
  net_balance: number;
  transaction_count: number;
}

export interface AccountSummaryCheckingSavings {
  institution: string;
  account_type: AccountType;
  total_withdrawals: number;
  total_deposits: number;
  net_flow: number;
  transaction_count: number;
}

export interface AccountSummaryResponse {
  date_range: {
    start: string;
    end: string;
  };
  credit_cards: {
    accounts: AccountSummaryAccount[];
    total_spent: number;
    total_payments: number;
    net_balance: number;
  };
  checking_savings: {
    accounts: AccountSummaryCheckingSavings[];
    total_withdrawals: number;
    total_deposits: number;
    net_flow: number;
  };
}

// Upload Types
export type UploadStatus = 'idle' | 'queued' | 'uploading' | 'success' | 'error';

export interface UploadItem {
  id: string;
  file: File;
  progress: number;
  status: UploadStatus;
  error?: string;
  response?: any;
}

export interface FileUploadResponse {
  statement_id: number;
  filename: string;
  size_bytes: number;
  source_type: string;
  message: string;
}
