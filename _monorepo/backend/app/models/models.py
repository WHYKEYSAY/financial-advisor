"""
Database models for CreditSphere
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, 
    JSON, ForeignKey, Text, Date, Index, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.db import Base


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    locale = Column(String(10), default="en")
    tier = Column(String(20), default="analyst")  # analyst, optimizer, autopilot
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    cards = relationship("Card", back_populates="user", cascade="all, delete-orphan")
    statements = relationship("Statement", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    quota = relationship("Quota", back_populates="user", uselist=False, cascade="all, delete-orphan")
    payment_plans = relationship("PaymentPlan", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    """Refresh token for JWT authentication"""
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    __table_args__ = (
        Index("idx_refresh_token_user_active", "user_id", "revoked"),
    )


class Account(Base):
    """Linked bank account"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    institution = Column(String(100), nullable=False)
    account_type = Column(String(50))  # checking, savings, credit
    mask = Column(String(10))  # Last 4 digits
    external_id = Column(String(255))  # Plaid account ID
    encrypted_access_token = Column(Text)  # Encrypted Plaid access token
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")


class Card(Base):
    """Credit card"""
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    issuer = Column(String(100), nullable=False)
    product = Column(String(100), nullable=False)
    last4 = Column(String(4))
    credit_limit = Column(Numeric(10, 2))
    apr = Column(Float)
    statement_day = Column(Integer)  # Day of month
    due_day = Column(Integer)  # Day of month
    is_active = Column(Boolean, default=True)
    
    # VCM (Virtual Credit Manager) fields
    current_balance = Column(Numeric(10, 2), default=0)  # Current amount owed
    vcm_enabled = Column(Boolean, default=False)  # Enrolled in VCM
    vcm_priority = Column(Integer)  # Priority order for spending allocation (lower = higher priority)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cards")
    transactions = relationship("Transaction", back_populates="card")


class Statement(Base):
    """Uploaded financial statement"""
    __tablename__ = "statements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String(20), nullable=False)  # pdf, csv, image
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    parsed = Column(Boolean, default=False)
    
    # Statement metadata
    institution = Column(String(100))  # CIBC, RBC, MBNA, PC Financial
    account_type = Column(String(50))  # credit_card, checking, savings
    account_number = Column(String(50))  # Last 4 digits or masked number
    
    period_start = Column(Date)
    period_end = Column(Date)
    transaction_count = Column(Integer, default=0)
    parse_error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    parsed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="statements")
    transactions = relationship("Transaction", back_populates="statement")
    
    __table_args__ = (
        Index("idx_statement_user_parsed", "user_id", "parsed"),
    )


class Merchant(Base):
    """Normalized merchant names"""
    __tablename__ = "merchants"
    
    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(200), unique=True, nullable=False, index=True)
    aliases = Column(JSON)  # List of known aliases
    category = Column(String(50))  # Default category
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="merchant")


class Transaction(Base):
    """Financial transaction"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    statement_id = Column(Integer, ForeignKey("statements.id", ondelete="SET NULL"), index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"))
    card_id = Column(Integer, ForeignKey("cards.id", ondelete="SET NULL"))
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="SET NULL"), index=True)
    
    date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="CAD")
    
    raw_merchant = Column(String(500))
    category = Column(String(50), index=True)
    subcategory = Column(String(50))
    
    tags = Column(JSON)  # List of tag IDs
    meta_data = Column(JSON)  # Additional data (renamed from metadata to avoid SQLAlchemy conflict)
    
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    statement = relationship("Statement", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    card = relationship("Card", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
    
    __table_args__ = (
        Index("idx_transaction_user_date", "user_id", "date"),
        Index("idx_transaction_user_category", "user_id", "category"),
    )


class Tag(Base):
    """User-defined tags"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(7))  # Hex color code
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tags")
    
    __table_args__ = (
        Index("idx_tag_user_name", "user_id", "name", unique=True),
    )


class RewardRule(Base):
    """Credit card reward rules"""
    __tablename__ = "reward_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    issuer = Column(String(100), nullable=False, index=True)
    product = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    multiplier = Column(Float, default=1.0)
    rate = Column(Float)  # Percentage or points per dollar
    reward_type = Column(String(20))  # points, cashback
    cap_monthly = Column(Numeric(10, 2))
    cap_annual = Column(Numeric(10, 2))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_reward_issuer_product", "issuer", "product"),
    )


class Subscription(Base):
    """Stripe subscription"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    stripe_customer_id = Column(String(100), unique=True)
    stripe_subscription_id = Column(String(100), unique=True)
    tier = Column(String(20), nullable=False)  # analyst, optimizer, autopilot
    status = Column(String(20), nullable=False)  # active, canceled, past_due
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscription")


class Quota(Base):
    """User quota tracking"""
    __tablename__ = "quotas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Statement-based quota (primary)
    statements_parsed = Column(Integer, default=0)
    statements_limit = Column(Integer, nullable=False)  # 5 for analyst, 50 for optimizer, unlimited for autopilot
    
    # AI-based quota (fallback for unknown merchants)
    ai_calls_used = Column(Integer, default=0)
    ai_calls_limit = Column(Integer, nullable=False)
    
    files_parsed = Column(Integer, default=0)  # Legacy, kept for compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="quota")


class CreditCard(Base):
    """Credit card products database (for recommendations)"""
    __tablename__ = "credit_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    issuer = Column(String(100), nullable=False, index=True)  # MBNA, RBC, PC Financial, etc.
    product_name = Column(String(200), nullable=False)  # World Elite Mastercard, Avion Visa, etc.
    card_network = Column(String(50))  # Mastercard, Visa, Amex
    
    # Costs
    annual_fee = Column(Numeric(10, 2), nullable=False, default=0)
    foreign_transaction_fee = Column(Float)  # Percentage
    
    # Rewards structure (JSON)
    # Format: {"groceries": {"rate": 3.0, "type": "points"}, "gas": {"rate": 2.0, "type": "cashback"}, ...}
    rewards = Column(JSON, nullable=False)
    
    # Welcome bonus
    welcome_bonus = Column(JSON)  # {"value": 350, "condition": "Spend $3000 in 3 months", "type": "points"}
    
    # Benefits
    insurance_benefits = Column(JSON)  # List: ["travel_medical", "car_rental", "mobile_device"]
    other_perks = Column(JSON)  # List: ["lounge_access", "concierge", ...]
    
    # Eligibility
    min_income = Column(Integer)  # Minimum personal income
    min_household_income = Column(Integer)  # Minimum household income
    
    # Additional info
    apply_url = Column(String(500))  # Application link
    image_url = Column(String(500))  # Card image URL
    description = Column(Text)  # Short description
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_creditcard_issuer_product", "issuer", "product_name", unique=True),
        Index("idx_creditcard_active", "is_active"),
    )


class PaymentPlan(Base):
    """Automated payment plan (VCM)"""
    __tablename__ = "payment_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan = Column(JSON, nullable=False)  # Payment distribution details
    run_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="pending")  # pending, executed, failed, canceled
    executed_at = Column(DateTime(timezone=True))
    error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payment_plans")
    
    __table_args__ = (
        Index("idx_payment_plan_run_at", "run_at", "status"),
    )
