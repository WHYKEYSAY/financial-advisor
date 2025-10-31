"""
Financial Advisor Application
Main entry point for the financial advisory software
"""

from advisor import FinancialAdvisor
from user_profile import UserProfile
from utils import display_menu, get_user_input


def main():
    """Main function to run the financial advisor application"""
    print("=" * 50)
    print("欢迎使用理财建议软件")
    print("Welcome to Financial Advisor")
    print("=" * 50)
    print()
    
    # Create user profile
    user_profile = UserProfile()
    advisor = FinancialAdvisor()
    
    while True:
        print("\n请选择功能 / Please select an option:")
        print("1. 创建/更新个人财务档案 (Create/Update Profile)")
        print("2. 获取投资建议 (Get Investment Advice)")
        print("3. 预算规划 (Budget Planning)")
        print("4. 储蓄目标 (Savings Goals)")
        print("5. 退出 (Exit)")
        
        choice = input("\n请输入选项 (Enter choice): ").strip()
        
        if choice == "1":
            user_profile.update_profile()
        elif choice == "2":
            advisor.provide_investment_advice(user_profile)
        elif choice == "3":
            advisor.create_budget_plan(user_profile)
        elif choice == "4":
            advisor.set_savings_goals(user_profile)
        elif choice == "5":
            print("\n感谢使用！Thank you for using Financial Advisor!")
            break
        else:
            print("\n无效选项，请重试。Invalid option, please try again.")


if __name__ == "__main__":
    main()
