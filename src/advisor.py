"""
Financial Advisor Module
Provides financial advice and recommendations
"""


class FinancialAdvisor:
    """Class to provide financial advice based on user profile"""
    
    def provide_investment_advice(self, user_profile):
        """Provide investment advice based on user's risk tolerance and financial situation"""
        print("\n--- 投资建议 / Investment Advice ---")
        
        if not user_profile.name:
            print("请先创建个人档案。Please create your profile first.")
            return
        
        surplus = user_profile.get_monthly_surplus()
        
        if surplus <= 0:
            print("⚠️ 警告：您的支出超过收入。建议先控制支出。")
            print("⚠️ Warning: Your expenses exceed your income. Please control spending first.")
            return
        
        print(f"\n您的月度结余：${surplus:,.2f} (Monthly Surplus)")
        print(f"风险承受能力：{user_profile.risk_tolerance} (Risk Tolerance)")
        print("\n推荐投资配置 (Recommended Allocation):\n")
        
        if user_profile.risk_tolerance == "low":
            print("保守型投资组合 (Conservative Portfolio):")
            print("- 60% 高评级债券 (High-grade bonds)")
            print("- 20% 货币市场基金 (Money market funds)")
            print("- 15% 蓝筹股 (Blue-chip stocks)")
            print("- 5% 紧急储备金 (Emergency fund)")
            
        elif user_profile.risk_tolerance == "medium":
            print("平衡型投资组合 (Balanced Portfolio):")
            print("- 40% 股票基金 (Stock funds)")
            print("- 35% 债券基金 (Bond funds)")
            print("- 15% 房地产投资信托 (REITs)")
            print("- 10% 现金储备 (Cash reserves)")
            
        else:  # high
            print("进取型投资组合 (Aggressive Portfolio):")
            print("- 60% 成长型股票 (Growth stocks)")
            print("- 20% 国际股票 (International stocks)")
            print("- 10% 债券 (Bonds)")
            print("- 10% 新兴市场/加密货币 (Emerging markets/Crypto)")
        
        print(f"\n建议每月投资金额：${surplus * 0.7:,.2f}")
        print(f"Suggested monthly investment: ${surplus * 0.7:,.2f}")
    
    def create_budget_plan(self, user_profile):
        """Create a budget plan for the user"""
        print("\n--- 预算规划 / Budget Planning ---")
        
        if not user_profile.name:
            print("请先创建个人档案。Please create your profile first.")
            return
        
        income = user_profile.income
        
        print(f"\n基于月收入 ${income:,.2f} 的建议预算 (Recommended Budget):")
        print(f"- 住房 (Housing): ${income * 0.30:,.2f} (30%)")
        print(f"- 食品 (Food): ${income * 0.15:,.2f} (15%)")
        print(f"- 交通 (Transportation): ${income * 0.10:,.2f} (10%)")
        print(f"- 储蓄/投资 (Savings/Investment): ${income * 0.20:,.2f} (20%)")
        print(f"- 债务偿还 (Debt Payment): ${income * 0.10:,.2f} (10%)")
        print(f"- 娱乐 (Entertainment): ${income * 0.10:,.2f} (10%)")
        print(f"- 其他 (Other): ${income * 0.05:,.2f} (5%)")
        
        current_surplus = user_profile.get_monthly_surplus()
        print(f"\n当前月度结余：${current_surplus:,.2f}")
        print(f"Current monthly surplus: ${current_surplus:,.2f}")
    
    def set_savings_goals(self, user_profile):
        """Help user set and track savings goals"""
        print("\n--- 储蓄目标 / Savings Goals ---")
        
        if not user_profile.name:
            print("请先创建个人档案。Please create your profile first.")
            return
        
        print("\n常见储蓄目标 (Common Savings Goals):")
        print("1. 紧急基金 (Emergency Fund)")
        print("2. 买房首付 (House Down Payment)")
        print("3. 退休储蓄 (Retirement)")
        print("4. 子女教育 (Children's Education)")
        print("5. 自定义目标 (Custom Goal)")
        
        choice = input("\n选择目标类型 (Choose goal type): ").strip()
        
        try:
            goal_amount = float(input("目标金额 (Goal amount): $").strip())
            months = int(input("目标月数 (Months to achieve): ").strip())
            
            monthly_needed = goal_amount / months
            surplus = user_profile.get_monthly_surplus()
            
            print(f"\n每月需要储蓄：${monthly_needed:,.2f}")
            print(f"Monthly savings needed: ${monthly_needed:,.2f}")
            print(f"当前月度结余：${surplus:,.2f}")
            print(f"Current monthly surplus: ${surplus:,.2f}")
            
            if monthly_needed <= surplus:
                print("\n✅ 目标可实现！Goal is achievable!")
            else:
                print("\n⚠️ 需要增加收入或减少支出。")
                print("⚠️ Need to increase income or reduce expenses.")
                shortage = monthly_needed - surplus
                print(f"缺口：${shortage:,.2f} / Shortfall: ${shortage:,.2f}")
                
        except ValueError:
            print("\n输入错误。Invalid input.")
