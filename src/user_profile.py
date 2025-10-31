"""
User Profile Module
Manages user financial information and preferences
"""


class UserProfile:
    """Class to represent a user's financial profile"""
    
    def __init__(self):
        self.name = ""
        self.age = 0
        self.income = 0.0
        self.expenses = 0.0
        self.savings = 0.0
        self.debt = 0.0
        self.risk_tolerance = ""  # low, medium, high
        self.investment_goals = []
        
    def update_profile(self):
        """Update user profile with new information"""
        print("\n--- 更新个人档案 / Update Profile ---")
        
        try:
            self.name = input("姓名 (Name): ").strip()
            self.age = int(input("年龄 (Age): ").strip())
            self.income = float(input("月收入 (Monthly Income): ").strip())
            self.expenses = float(input("月支出 (Monthly Expenses): ").strip())
            self.savings = float(input("当前储蓄 (Current Savings): ").strip())
            self.debt = float(input("债务 (Debt): ").strip())
            
            print("\n风险承受能力 (Risk Tolerance):")
            print("1. 低风险 (Low)")
            print("2. 中等风险 (Medium)")
            print("3. 高风险 (High)")
            risk_choice = input("选择 (Choose): ").strip()
            
            risk_map = {"1": "low", "2": "medium", "3": "high"}
            self.risk_tolerance = risk_map.get(risk_choice, "medium")
            
            print("\n档案更新成功！Profile updated successfully!")
            self.display_profile()
            
        except ValueError:
            print("\n输入错误，请输入有效数字。Invalid input, please enter valid numbers.")
    
    def display_profile(self):
        """Display current user profile"""
        print("\n--- 当前档案 / Current Profile ---")
        print(f"姓名 (Name): {self.name}")
        print(f"年龄 (Age): {self.age}")
        print(f"月收入 (Monthly Income): ${self.income:,.2f}")
        print(f"月支出 (Monthly Expenses): ${self.expenses:,.2f}")
        print(f"储蓄 (Savings): ${self.savings:,.2f}")
        print(f"债务 (Debt): ${self.debt:,.2f}")
        print(f"风险承受能力 (Risk Tolerance): {self.risk_tolerance}")
        
    def get_monthly_surplus(self):
        """Calculate monthly surplus/deficit"""
        return self.income - self.expenses
    
    def get_net_worth(self):
        """Calculate net worth"""
        return self.savings - self.debt
