"""
Utility Functions
Helper functions for the financial advisor application
"""


def display_menu():
    """Display the main menu"""
    print("\n" + "=" * 50)
    print("Financial Advisor Menu")
    print("=" * 50)


def get_user_input(prompt, input_type=str):
    """
    Get validated user input
    
    Args:
        prompt: The prompt to display to the user
        input_type: The type to convert the input to (str, int, float)
    
    Returns:
        The validated input value
    """
    while True:
        try:
            user_input = input(prompt).strip()
            if input_type == str:
                return user_input
            else:
                return input_type(user_input)
        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}.")


def format_currency(amount):
    """
    Format a number as currency
    
    Args:
        amount: The amount to format
    
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"


def calculate_compound_interest(principal, rate, years):
    """
    Calculate compound interest
    
    Args:
        principal: Initial investment amount
        rate: Annual interest rate (as decimal, e.g., 0.05 for 5%)
        years: Number of years
    
    Returns:
        Final amount after compound interest
    """
    return principal * (1 + rate) ** years
