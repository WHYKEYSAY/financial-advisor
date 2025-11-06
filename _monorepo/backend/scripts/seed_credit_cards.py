"""
Seed script to populate Canadian credit cards database
Run: docker exec creditsphere-backend python scripts/seed_credit_cards.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.models.models import CreditCard
from loguru import logger


def seed_credit_cards():
    """Initialize credit cards database with popular Canadian cards"""
    
    db = SessionLocal()
    
    try:
        # Check if already seeded
        existing_count = db.query(CreditCard).count()
        if existing_count > 0:
            logger.info(f"Database already contains {existing_count} credit cards. Skipping seed.")
            return
        
        cards = [
            # MBNA Cards
            {
                "issuer": "MBNA",
                "product_name": "Rewards World Elite Mastercard",
                "card_network": "Mastercard",
                "annual_fee": 89.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "groceries": {"rate": 5.0, "type": "points"},
                    "gas": {"rate": 5.0, "type": "points"},
                    "dining": {"rate": 5.0, "type": "points"},
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 20000,
                    "condition": "Spend $1000 in first 3 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "car_rental", "mobile_device"],
                "other_perks": [],
                "min_income": 80000,
                "min_household_income": 150000,
                "description": "5% cash back on groceries, gas and dining. Perfect for everyday spending.",
                "apply_url": "https://www.mbna.ca/credit-cards/rewards/",
                "is_active": True
            },
            
            # RBC Cards
            {
                "issuer": "RBC",
                "product_name": "Avion Visa Infinite",
                "card_network": "Visa",
                "annual_fee": 120.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "travel": {"rate": 1.25, "type": "points"},
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 35000,
                    "condition": "Spend $5000 in first 6 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental", "mobile_device"],
                "other_perks": ["lounge_access", "concierge"],
                "min_income": 60000,
                "min_household_income": 100000,
                "description": "Best for travel rewards with RBC Avion points. Great welcome bonus.",
                "apply_url": "https://www.rbcroyalbank.com/credit-cards/travel-credit-cards/avion-visa-infinite/",
                "is_active": True
            },
            {
                "issuer": "RBC",
                "product_name": "ION+ Visa",
                "card_network": "Visa",
                "annual_fee": 0.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "default": {"rate": 1.0, "type": "cashback"}
                },
                "welcome_bonus": {
                    "value": 100,
                    "condition": "Spend $1000 in first 3 months",
                    "type": "cashback"
                },
                "insurance_benefits": [],
                "other_perks": [],
                "min_income": 12000,
                "min_household_income": 12000,
                "description": "No annual fee. Simple 1% cash back on everything. Great starter card.",
                "apply_url": "https://www.rbcroyalbank.com/credit-cards/cash-back-credit-cards/rbc-ion-plus-visa/",
                "is_active": True
            },
            
            # PC Financial
            {
                "issuer": "PC Financial",
                "product_name": "World Elite Mastercard",
                "card_network": "Mastercard",
                "annual_fee": 0.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "groceries": {"rate": 30.0, "type": "points"},  # 30 PC points per $1 at Loblaws
                    "shoppers": {"rate": 30.0, "type": "points"},
                    "esso": {"rate": 30.0, "type": "points"},
                    "default": {"rate": 10.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 20000,
                    "condition": "Spend $1000 in first 3 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "car_rental", "mobile_device"],
                "other_perks": [],
                "min_income": 80000,
                "min_household_income": 150000,
                "description": "Best for PC Optimum members. 3% back at Loblaws, Shoppers, Esso. No annual fee!",
                "apply_url": "https://www.pcfinancial.ca/en/credit-cards/pc-money-account/pc-mastercard/",
                "is_active": True
            },
            
            # Tangerine
            {
                "issuer": "Tangerine",
                "product_name": "Money-Back Credit Card",
                "card_network": "Mastercard",
                "annual_fee": 0.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "custom_category_1": {"rate": 2.0, "type": "cashback"},
                    "custom_category_2": {"rate": 2.0, "type": "cashback"},
                    "custom_category_3": {"rate": 2.0, "type": "cashback"},
                    "default": {"rate": 0.5, "type": "cashback"}
                },
                "welcome_bonus": {
                    "value": 100,
                    "condition": "Spend $1000 in first 3 months",
                    "type": "cashback"
                },
                "insurance_benefits": [],
                "other_perks": [],
                "min_income": 0,
                "min_household_income": 0,
                "description": "Choose 3 categories for 2% cash back. No annual fee. Easy to get.",
                "apply_url": "https://www.tangerine.ca/en/products/spending/creditcard",
                "is_active": True
            },
            
            # Scotiabank
            {
                "issuer": "Scotiabank",
                "product_name": "Momentum Visa Infinite",
                "card_network": "Visa",
                "annual_fee": 120.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "groceries": {"rate": 4.0, "type": "cashback"},
                    "gas": {"rate": 4.0, "type": "cashback"},
                    "recurring": {"rate": 4.0, "type": "cashback"},
                    "pharmacy": {"rate": 2.0, "type": "cashback"},
                    "default": {"rate": 1.0, "type": "cashback"}
                },
                "welcome_bonus": {
                    "value": 150,
                    "condition": "Spend $3000 in first 3 months",
                    "type": "cashback"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental"],
                "other_perks": [],
                "min_income": 60000,
                "min_household_income": 100000,
                "description": "4% back on groceries, gas, and recurring bills. Great for families.",
                "apply_url": "https://www.scotiabank.com/ca/en/personal/credit-cards/visa/momentum-infinite.html",
                "is_active": True
            },
            {
                "issuer": "Scotiabank",
                "product_name": "Momentum No-Fee Visa",
                "card_network": "Visa",
                "annual_fee": 0.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "groceries": {"rate": 2.0, "type": "cashback"},
                    "gas": {"rate": 2.0, "type": "cashback"},
                    "recurring": {"rate": 2.0, "type": "cashback"},
                    "default": {"rate": 1.0, "type": "cashback"}
                },
                "welcome_bonus": {
                    "value": 100,
                    "condition": "Spend $1000 in first 3 months",
                    "type": "cashback"
                },
                "insurance_benefits": [],
                "other_perks": [],
                "min_income": 0,
                "min_household_income": 0,
                "description": "No annual fee version of Momentum. 2% back on groceries, gas, bills.",
                "apply_url": "https://www.scotiabank.com/ca/en/personal/credit-cards/visa/momentum-no-fee.html",
                "is_active": True
            },
            
            # TD
            {
                "issuer": "TD",
                "product_name": "Cash Back Visa Infinite",
                "card_network": "Visa",
                "annual_fee": 139.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "groceries": {"rate": 3.0, "type": "cashback"},
                    "gas": {"rate": 3.0, "type": "cashback"},
                    "recurring": {"rate": 3.0, "type": "cashback"},
                    "default": {"rate": 1.0, "type": "cashback"}
                },
                "welcome_bonus": {
                    "value": 200,
                    "condition": "Spend $3000 in first 3 months",
                    "type": "cashback"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental", "mobile_device"],
                "other_perks": [],
                "min_income": 60000,
                "min_household_income": 100000,
                "description": "3% cash back on groceries, gas and recurring bills. Strong insurance coverage.",
                "apply_url": "https://www.td.com/ca/en/personal-banking/products/credit-cards/cash-back/cash-back-visa-infinite-card",
                "is_active": True
            },
            
            # Simplii Financial
            {
                "issuer": "Simplii Financial",
                "product_name": "Cash Back Visa",
                "card_network": "Visa",
                "annual_fee": 0.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "dining": {"rate": 4.0, "type": "cashback"},
                    "groceries": {"rate": 1.5, "type": "cashback"},
                    "gas": {"rate": 1.5, "type": "cashback"},
                    "recurring": {"rate": 1.5, "type": "cashback"},
                    "default": {"rate": 0.5, "type": "cashback"}
                },
                "welcome_bonus": {
                    "value": 100,
                    "condition": "Spend $1000 in first 3 months",
                    "type": "cashback"
                },
                "insurance_benefits": [],
                "other_perks": [],
                "min_income": 0,
                "min_household_income": 0,
                "description": "4% back on dining, 1.5% on groceries/gas. No annual fee. Great for foodies.",
                "apply_url": "https://www.simplii.com/en/credit-cards/cash-back-visa-card.html",
                "is_active": True
            },
            
            # CIBC
            {
                "issuer": "CIBC",
                "product_name": "Dividend Visa Infinite",
                "card_network": "Visa",
                "annual_fee": 120.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "groceries": {"rate": 4.0, "type": "cashback"},
                    "gas": {"rate": 4.0, "type": "cashback"},
                    "transportation": {"rate": 2.0, "type": "cashback"},
                    "default": {"rate": 1.0, "type": "cashback"}
                },
                "welcome_bonus": {
                    "value": 200,
                    "condition": "Spend $3000 in first 4 months",
                    "type": "cashback"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental", "mobile_device"],
                "other_perks": [],
                "min_income": 60000,
                "min_household_income": 100000,
                "description": "4% back on groceries and gas. 2% on transit. Great for commuters.",
                "apply_url": "https://www.cibc.com/en/personal-banking/credit-cards/cash-back-credit-cards/dividend-visa-infinite-card.html",
                "is_active": True
            },
            
            # BMO
            {
                "issuer": "BMO",
                "product_name": "Cash Back Mastercard",
                "card_network": "Mastercard",
                "annual_fee": 0.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "groceries": {"rate": 3.0, "type": "cashback"},
                    "default": {"rate": 1.0, "type": "cashback"}
                },
                "welcome_bonus": {
                    "value": 100,
                    "condition": "Spend $1000 in first 3 months",
                    "type": "cashback"
                },
                "insurance_benefits": [],
                "other_perks": [],
                "min_income": 0,
                "min_household_income": 0,
                "description": "3% back on groceries. No annual fee. Simple and effective.",
                "apply_url": "https://www.bmo.com/main/personal/credit-cards/bmo-cashback-mastercard/",
                "is_active": True
            },
        ]
        
        # Insert all cards
        for card_data in cards:
            card = CreditCard(**card_data)
            db.add(card)
        
        db.commit()
        
        logger.info(f"✅ Successfully seeded {len(cards)} credit cards!")
        logger.info("Cards added:")
        for card_data in cards:
            logger.info(f"  - {card_data['issuer']} {card_data['product_name']} (${card_data['annual_fee']})")
        
    except Exception as e:
        logger.error(f"❌ Failed to seed credit cards: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Starting credit cards database seeding...")
    seed_credit_cards()
    logger.info("Done!")
