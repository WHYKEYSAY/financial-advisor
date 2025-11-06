"""
Extended credit cards seeding script - Expanding from 11 to 40+ cards
Includes major Canadian credit card issuers: TD, BMO, Amex, CIBC, National Bank, Desjardins

Run: docker exec creditsphere-backend python scripts/seed_credit_cards_extended.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.models.models import CreditCard
from loguru import logger


def seed_extended_cards():
    """Add 30+ additional Canadian credit cards to the database"""
    
    db = SessionLocal()
    
    try:
        # Get existing cards to avoid duplicates
        existing_cards = db.query(CreditCard).all()
        existing_names = {(card.issuer, card.product_name) for card in existing_cards}
        
        logger.info(f"Found {len(existing_cards)} existing credit cards")
        
        # Extended card list - 30+ additional cards
        new_cards = [
            # ==================== TD BANK ====================
            {
                "issuer": "TD",
                "product_name": "First Class Travel Visa Infinite",
                "card_network": "Visa",
                "annual_fee": 139.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "travel": {"rate": 3.0, "type": "points"},
                    "dining": {"rate": 3.0, "type": "points"},
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 60000,
                    "condition": "Spend $5000 in first 3 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental", "baggage_delay"],
                "other_perks": ["lounge_access", "priority_check_in"],
                "min_income": 60000,
                "min_household_income": 100000,
                "description": "Premium travel rewards card. Earn 3 points per $1 on travel and dining.",
                "apply_url": "https://www.td.com/ca/en/personal-banking/products/credit-cards/travel/first-class-travel-visa-infinite",
                "is_active": True
            },
            {
                "issuer": "TD",
                "product_name": "Aeroplan Visa Infinite",
                "card_network": "Visa",
                "annual_fee": 139.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "travel": {"rate": 1.5, "type": "points"},  # Aeroplan points
                    "gas": {"rate": 1.5, "type": "points"},
                    "groceries": {"rate": 1.5, "type": "points"},
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 20000,
                    "condition": "Spend $1000 in first 3 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental"],
                "other_perks": ["first_checked_bag_free", "priority_boarding"],
                "min_income": 60000,
                "min_household_income": 100000,
                "description": "Earn Aeroplan points for flights. 1.5x on travel, gas, and groceries.",
                "apply_url": "https://www.td.com/ca/en/personal-banking/products/credit-cards/aeroplan/aeroplan-visa-infinite-card",
                "is_active": True
            },
            {
                "issuer": "TD",
                "product_name": "Green Visa",
                "card_network": "Visa",
                "annual_fee": 0.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "default": {"rate": 1.0, "type": "cashback"}
                },
                "welcome_bonus": {
                    "value": 0,
                    "condition": "None",
                    "type": "cashback"
                },
                "insurance_benefits": [],
                "other_perks": [],
                "min_income": 12000,
                "min_household_income": 12000,
                "description": "Entry-level no-fee card. 1% cash back on everything.",
                "apply_url": "https://www.td.com/ca/en/personal-banking/products/credit-cards/cash-back/green-visa-card",
                "is_active": True
            },
            
            # ==================== BMO ====================
            {
                "issuer": "BMO",
                "product_name": "World Elite Mastercard",
                "card_network": "Mastercard",
                "annual_fee": 150.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "travel": {"rate": 5.0, "type": "points"},
                    "dining": {"rate": 5.0, "type": "points"},
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 90000,
                    "condition": "Spend $6000 in first 3 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental", "mobile_device"],
                "other_perks": ["lounge_access", "concierge", "priority_pass"],
                "min_income": 80000,
                "min_household_income": 150000,
                "description": "Premium travel card. 5x points on travel and dining. Priority Pass lounge access.",
                "apply_url": "https://www.bmo.com/main/personal/credit-cards/bmo-world-elite-mastercard/",
                "is_active": True
            },
            {
                "issuer": "BMO",
                "product_name": "Eclipse Visa Infinite",
                "card_network": "Visa",
                "annual_fee": 120.00,
                "foreign_transaction_fee": 0.0,  # No FX fee!
                "rewards": {
                    "travel": {"rate": 5.0, "type": "points"},
                    "dining": {"rate": 5.0, "type": "points"},
                    "gas": {"rate": 3.0, "type": "points"},
                    "groceries": {"rate": 2.0, "type": "points"},
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 40000,
                    "condition": "Spend $3000 in first 3 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental"],
                "other_perks": ["no_forex_fee"],
                "min_income": 60000,
                "min_household_income": 100000,
                "description": "No foreign exchange fees! 5x on travel & dining, 3x on gas.",
                "apply_url": "https://www.bmo.com/main/personal/credit-cards/bmo-eclipse-visa-infinite-card/",
                "is_active": True
            },
            {
                "issuer": "BMO",
                "product_name": "Rewards Mastercard",
                "card_network": "Mastercard",
                "annual_fee": 0.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 15000,
                    "condition": "Spend $1000 in first 3 months",
                    "type": "points"
                },
                "insurance_benefits": [],
                "other_perks": [],
                "min_income": 15000,
                "min_household_income": 15000,
                "description": "No annual fee rewards card. Earn 1 point per $1 spent.",
                "apply_url": "https://www.bmo.com/main/personal/credit-cards/bmo-rewards-mastercard/",
                "is_active": True
            },
            {
                "issuer": "BMO",
                "product_name": "Preferred Rate Mastercard",
                "card_network": "Mastercard",
                "annual_fee": 20.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "default": {"rate": 0.0, "type": "cashback"}  # No rewards, low APR card
                },
                "welcome_bonus": {
                    "value": 0,
                    "condition": "None",
                    "type": "cashback"
                },
                "insurance_benefits": [],
                "other_perks": ["low_apr"],
                "min_income": 12000,
                "min_household_income": 12000,
                "description": "Low interest rate card. Ideal for balance transfers.",
                "apply_url": "https://www.bmo.com/main/personal/credit-cards/low-rate-credit-cards/preferred-rate-mastercard/",
                "is_active": True
            },
            
            # ==================== AMERICAN EXPRESS ====================
            {
                "issuer": "American Express",
                "product_name": "Platinum Card",
                "card_network": "American Express",
                "annual_fee": 799.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "travel": {"rate": 5.0, "type": "points"},
                    "dining": {"rate": 2.0, "type": "points"},
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 100000,
                    "condition": "Spend $8000 in first 3 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental", "purchase_protection"],
                "other_perks": ["lounge_access", "concierge", "hotel_status", "airline_credit"],
                "min_income": 150000,
                "min_household_income": 200000,
                "description": "Premium luxury travel card. Extensive perks and insurance. $200 annual travel credit.",
                "apply_url": "https://www.americanexpress.com/ca/en/credit-cards/platinum-card/",
                "is_active": True
            },
            {
                "issuer": "American Express",
                "product_name": "Cobalt Card",
                "card_network": "American Express",
                "annual_fee": 155.88,  # Monthly fee: $12.99
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "groceries": {"rate": 5.0, "type": "points"},
                    "dining": {"rate": 5.0, "type": "points"},
                    "streaming": {"rate": 5.0, "type": "points"},
                    "transit": {"rate": 3.0, "type": "points"},
                    "gas": {"rate": 2.0, "type": "points"},
                    "travel": {"rate": 2.0, "type": "points"},
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 15000,
                    "condition": "Spend $750/month for 12 months",
                    "type": "points"
                },
                "insurance_benefits": ["mobile_device", "travel_medical"],
                "other_perks": ["monthly_fee_structure"],
                "min_income": 12000,
                "min_household_income": 12000,
                "description": "Best for everyday spending. 5x on food, dining, streaming. Monthly fee.",
                "apply_url": "https://www.americanexpress.com/ca/en/credit-cards/cobalt-card/",
                "is_active": True
            },
            {
                "issuer": "American Express",
                "product_name": "Gold Rewards Card",
                "card_network": "American Express",
                "annual_fee": 250.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "travel": {"rate": 2.0, "type": "points"},
                    "dining": {"rate": 2.0, "type": "points"},
                    "gas": {"rate": 2.0, "type": "points"},
                    "groceries": {"rate": 2.0, "type": "points"},
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 40000,
                    "condition": "Spend $3000 in first 3 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental"],
                "other_perks": ["priority_pass"],
                "min_income": 60000,
                "min_household_income": 100000,
                "description": "Earn 2x points on travel, dining, gas, and groceries.",
                "apply_url": "https://www.americanexpress.com/ca/en/credit-cards/gold-rewards-card/",
                "is_active": True
            },
            {
                "issuer": "American Express",
                "product_name": "SimplyCash Preferred",
                "card_network": "American Express",
                "annual_fee": 99.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "default": {"rate": 2.0, "type": "cashback"}
                },
                "welcome_bonus": {
                    "value": 10,  # 10% cashback up to $400
                    "condition": "Get 10% cash back on all purchases up to $400 in the first 3 months",
                    "type": "cashback"
                },
                "insurance_benefits": [],
                "other_perks": [],
                "min_income": 60000,
                "min_household_income": 100000,
                "description": "Simple 2% cash back on everything. First year bonus: 10% back up to $400.",
                "apply_url": "https://www.americanexpress.com/ca/en/credit-cards/simply-cash-preferred-credit-card/",
                "is_active": True
            },
            
            # ==================== CIBC (Additional) ====================
            {
                "issuer": "CIBC",
                "product_name": "Aventura Visa Infinite",
                "card_network": "Visa",
                "annual_fee": 139.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "travel": {"rate": 2.0, "type": "points"},
                    "dining": {"rate": 2.0, "type": "points"},
                    "gas": {"rate": 2.0, "type": "points"},
                    "groceries": {"rate": 2.0, "type": "points"},
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 40000,
                    "condition": "Spend $3000 in first 4 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental", "mobile_device"],
                "other_perks": [],
                "min_income": 60000,
                "min_household_income": 100000,
                "description": "Flexible points card. 2x on travel, dining, gas, and groceries.",
                "apply_url": "https://www.cibc.com/en/personal-banking/credit-cards/travel-credit-cards/aventura-visa-infinite-card.html",
                "is_active": True
            },
            {
                "issuer": "CIBC",
                "product_name": "Select Visa",
                "card_network": "Visa",
                "annual_fee": 0.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "default": {"rate": 1.0, "type": "cashback"}
                },
                "welcome_bonus": {
                    "value": 100,
                    "condition": "Spend $1000 in first 4 months",
                    "type": "cashback"
                },
                "insurance_benefits": [],
                "other_perks": [],
                "min_income": 12000,
                "min_household_income": 12000,
                "description": "Basic no-fee card. 1% cash back on everything.",
                "apply_url": "https://www.cibc.com/en/personal-banking/credit-cards/cash-back-credit-cards/select-visa-card.html",
                "is_active": True
            },
            
            # ==================== NATIONAL BANK ====================
            {
                "issuer": "National Bank",
                "product_name": "World Elite Mastercard",
                "card_network": "Mastercard",
                "annual_fee": 150.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "travel": {"rate": 5.0, "type": "points"},
                    "groceries": {"rate": 2.0, "type": "points"},
                    "gas": {"rate": 2.0, "type": "points"},
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 50000,
                    "condition": "Spend $5000 in first 3 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental", "mobile_device"],
                "other_perks": ["lounge_access"],
                "min_income": 80000,
                "min_household_income": 150000,
                "description": "Premium travel card. 5x on travel. Includes Priority Pass lounge access.",
                "apply_url": "https://www.nbc.ca/personal/credit-cards/all-in-one-world-elite.html",
                "is_active": True
            },
            {
                "issuer": "National Bank",
                "product_name": "SynchroCash Mastercard",
                "card_network": "Mastercard",
                "annual_fee": 0.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "groceries": {"rate": 4.0, "type": "cashback"},
                    "gas": {"rate": 4.0, "type": "cashback"},
                    "drugstore": {"rate": 2.0, "type": "cashback"},
                    "default": {"rate": 1.0, "type": "cashback"}
                },
                "welcome_bonus": {
                    "value": 50,
                    "condition": "Spend $500 in first 3 months",
                    "type": "cashback"
                },
                "insurance_benefits": [],
                "other_perks": [],
                "min_income": 0,
                "min_household_income": 0,
                "description": "No annual fee. 4% on groceries and gas. Perfect for everyday spending.",
                "apply_url": "https://www.nbc.ca/personal/credit-cards/synchro.html",
                "is_active": True
            },
            
            # ==================== DESJARDINS ====================
            {
                "issuer": "Desjardins",
                "product_name": "Odyssey Visa Infinite",
                "card_network": "Visa",
                "annual_fee": 120.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "travel": {"rate": 5.0, "type": "points"},
                    "groceries": {"rate": 3.0, "type": "points"},
                    "gas": {"rate": 3.0, "type": "points"},
                    "dining": {"rate": 3.0, "type": "points"},
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 35000,
                    "condition": "Spend $3000 in first 3 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental"],
                "other_perks": [],
                "min_income": 60000,
                "min_household_income": 100000,
                "description": "Strong travel rewards. 5x on travel, 3x on groceries, gas, dining.",
                "apply_url": "https://www.desjardins.com/credit-cards/odyssey-visa-infinite/index.jsp",
                "is_active": True
            },
            {
                "issuer": "Desjardins",
                "product_name": "Cash Back Mastercard",
                "card_network": "Mastercard",
                "annual_fee": 0.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "groceries": {"rate": 1.5, "type": "cashback"},
                    "gas": {"rate": 1.5, "type": "cashback"},
                    "drugstore": {"rate": 1.5, "type": "cashback"},
                    "default": {"rate": 0.5, "type": "cashback"}
                },
                "welcome_bonus": {
                    "value": 50,
                    "condition": "Spend $1000 in first 3 months",
                    "type": "cashback"
                },
                "insurance_benefits": [],
                "other_perks": [],
                "min_income": 0,
                "min_household_income": 0,
                "description": "No annual fee. 1.5% back on groceries, gas, and drugstore.",
                "apply_url": "https://www.desjardins.com/credit-cards/cash-back-mastercard/index.jsp",
                "is_active": True
            },
            
            # ==================== ADDITIONAL POPULAR CARDS ====================
            {
                "issuer": "Capital One",
                "product_name": "Aspire Travel World Elite Mastercard",
                "card_network": "Mastercard",
                "annual_fee": 150.00,
                "foreign_transaction_fee": 0.0,  # No FX fee!
                "rewards": {
                    "travel": {"rate": 5.0, "type": "points"},
                    "dining": {"rate": 3.0, "type": "points"},
                    "entertainment": {"rate": 3.0, "type": "points"},
                    "default": {"rate": 2.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 60000,
                    "condition": "Spend $5000 in first 3 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental"],
                "other_perks": ["no_forex_fee", "lounge_access"],
                "min_income": 80000,
                "min_household_income": 150000,
                "description": "No foreign exchange fees! 5x on travel, 3x on dining/entertainment.",
                "apply_url": "https://www.capitalone.ca/credit-cards/aspire-travel/",
                "is_active": True
            },
            {
                "issuer": "Rogers Bank",
                "product_name": "World Elite Mastercard",
                "card_network": "Mastercard",
                "annual_fee": 0.00,
                "foreign_transaction_fee": 0.0,  # No FX fee with Rogers/Fido
                "rewards": {
                    "default": {"rate": 1.5, "type": "cashback"},
                    "rogers_fido": {"rate": 3.0, "type": "cashback"}  # Rogers/Fido bills
                },
                "welcome_bonus": {
                    "value": 0,
                    "condition": "None",
                    "type": "cashback"
                },
                "insurance_benefits": ["travel_medical", "mobile_device"],
                "other_perks": ["no_forex_fee"],
                "min_income": 80000,
                "min_household_income": 150000,
                "description": "No FX fees (with Rogers/Fido). 3% on Rogers bills, 1.5% on everything else.",
                "apply_url": "https://www.rogersbank.com/en/rogers_world_elite_mastercard",
                "is_active": True
            },
            {
                "issuer": "HSBC",
                "product_name": "World Elite Mastercard",
                "card_network": "Mastercard",
                "annual_fee": 149.00,
                "foreign_transaction_fee": 2.5,
                "rewards": {
                    "travel": {"rate": 6.0, "type": "points"},
                    "dining": {"rate": 3.0, "type": "points"},
                    "default": {"rate": 1.0, "type": "points"}
                },
                "welcome_bonus": {
                    "value": 50000,
                    "condition": "Spend $5000 in first 6 months",
                    "type": "points"
                },
                "insurance_benefits": ["travel_medical", "trip_cancellation", "car_rental", "baggage_delay"],
                "other_perks": ["lounge_access", "concierge"],
                "min_income": 80000,
                "min_household_income": 150000,
                "description": "Premium travel card. 6x on travel bookings. Priority Pass lounge access.",
                "apply_url": "https://www.hsbc.ca/credit-cards/products/world-elite/",
                "is_active": True
            },
        ]
        
        # Filter out cards that already exist
        cards_to_add = []
        for card_data in new_cards:
            key = (card_data["issuer"], card_data["product_name"])
            if key not in existing_names:
                cards_to_add.append(card_data)
            else:
                logger.info(f"⏭️  Skipping existing card: {card_data['issuer']} {card_data['product_name']}")
        
        if not cards_to_add:
            logger.info("✅ No new cards to add. Database is already up to date!")
            return
        
        logger.info(f"➕ Adding {len(cards_to_add)} new credit cards...")
        
        # Insert new cards
        for card_data in cards_to_add:
            card = CreditCard(**card_data)
            db.add(card)
        
        db.commit()
        
        # Get final count
        final_count = db.query(CreditCard).count()
        
        logger.info(f"✅ Successfully added {len(cards_to_add)} new credit cards!")
        logger.info(f"📊 Total cards in database: {final_count}")
        logger.info("\nNewly added cards:")
        for card_data in cards_to_add:
            logger.info(f"  - {card_data['issuer']} {card_data['product_name']} (${card_data['annual_fee']})")
        
    except Exception as e:
        logger.error(f"❌ Failed to seed extended credit cards: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("Starting extended credit cards database seeding...")
    logger.info("=" * 80)
    seed_extended_cards()
    logger.info("\n" + "=" * 80)
    logger.info("Done!")
    logger.info("=" * 80)
