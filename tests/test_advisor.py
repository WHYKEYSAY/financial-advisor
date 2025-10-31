"""
Unit tests for the Financial Advisor module
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from advisor import FinancialAdvisor
from user_profile import UserProfile


def test_investment_advice_no_profile():
    """Test investment advice with empty profile"""
    advisor = FinancialAdvisor()
    profile = UserProfile()
    # Should handle gracefully without crashing
    advisor.provide_investment_advice(profile)


def test_budget_plan_no_profile():
    """Test budget plan with empty profile"""
    advisor = FinancialAdvisor()
    profile = UserProfile()
    # Should handle gracefully without crashing
    advisor.create_budget_plan(profile)


if __name__ == "__main__":
    print("Running basic tests...")
    test_investment_advice_no_profile()
    test_budget_plan_no_profile()
    print("Tests completed!")
