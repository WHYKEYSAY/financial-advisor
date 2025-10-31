# Financial Advisor Software / 理财建议软件

A bilingual (English/Chinese) personal financial advisory application that helps users manage their finances, create budgets, and receive investment recommendations.

## Features / 功能

- **User Profile Management / 个人档案管理**
  - Track income, expenses, savings, and debt
  - Set risk tolerance preferences
  
- **Investment Advice / 投资建议**
  - Personalized investment portfolio recommendations based on risk tolerance
  - Conservative, balanced, and aggressive portfolio options
  
- **Budget Planning / 预算规划**
  - Recommended budget allocations based on income
  - Track monthly surplus/deficit
  
- **Savings Goals / 储蓄目标**
  - Set financial goals (emergency fund, house down payment, retirement, etc.)
  - Calculate monthly savings needed
  - Track progress toward goals

## Installation / 安装

1. Clone or download this repository
2. Ensure Python 3.7+ is installed
3. No external dependencies required for basic functionality

```bash
python src/main.py
```

## Usage / 使用方法

Run the main application:

```bash
cd financial-advisor
python src/main.py
```

Follow the on-screen menu to:
1. Create/Update your financial profile
2. Get investment advice
3. Create a budget plan
4. Set savings goals

## Project Structure / 项目结构

```
financial-advisor/
├── src/
│   ├── __init__.py       # Package initializer
│   ├── main.py           # Main entry point
│   ├── advisor.py        # Financial advice logic
│   ├── user_profile.py   # User profile management
│   └── utils.py          # Utility functions
├── tests/                # Unit tests (to be added)
├── data/                 # Data files (for future use)
├── docs/                 # Additional documentation
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Future Enhancements / 未来改进

- [ ] Data persistence (save/load user profiles)
- [ ] Financial charts and visualizations
- [ ] Investment tracking and portfolio analysis
- [ ] Tax planning recommendations
- [ ] Multi-currency support
- [ ] Mobile app version

## Contributing / 贡献

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License / 许可证

This project is open source and available for personal and educational use.

## Disclaimer / 免责声明

This software provides general financial information and suggestions for educational purposes only. It is not professional financial advice. Always consult with a qualified financial advisor before making investment decisions.

本软件仅提供一般性财务信息和建议，仅供教育目的使用。这不是专业的财务建议。在做出投资决定之前，请务必咨询合格的财务顾问。
