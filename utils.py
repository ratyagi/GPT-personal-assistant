# Utility functions (data processing, GPT prompt prep)
import pandas as pd

def load_csv(file_bytes):
    return pd.read_csv(file_bytes)

def summarize_expenses(df):
    total = df["Amount"].sum()
    summary = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    by_category_str = "\n".join([f"{cat}: ${amt:.2f}" for cat, amt in summary.items()])
    return f"Total spent: ${total:.2f}\n\nSpending by category:\n{by_category_str}"

def format_summary_for_gpt(summary_text):
    return f"""I have the following expense summary:
{summary_text}

Suggest 3 financial tip based on this."""

def format_goal_prompt(summary_text, goal):
    return f"""Here's a summary of a user's recent expenses:
{summary_text}

Their financial goal is: "{goal}".

Based on this, give one personalized, actionable saving or budgeting tip that will help them reach their goal. Keep it concise and clear."""