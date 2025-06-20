import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import io
from streamlit_login_auth_ui.widgets import __login__


# --- Login UI ---
__login__obj = __login__(
    auth_token="dummy_token",
    company_name="FinanceAI",
    width=230, height=250,
    logout_button_name='Logout',
    hide_menu_bool=True,
    hide_footer_bool=True,
    lottie_url='https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json'
)

LOGGED_IN = __login__obj.build_login_ui()

if LOGGED_IN == True:

    st.markdown("Your Streamlit Application Begins here!")

    # --- Main App ---
    st.title("Personal Finance Assistant")
    st.write("Upload your expense CSV to get a summary and smart saving tips.")

    # --- USER GOAL INPUT ---
    st.sidebar.header("Set Your Financial Goal")
    goal = st.sidebar.text_input("What are you saving for?", placeholder="e.g., Save $5000 for a trip")

    # Upload CSV
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file:
        # Read file bytes once
        file_bytes = uploaded_file.read()
        df = pd.read_csv(io.BytesIO(file_bytes))  # preview

        st.subheader("Expense Preview")
        st.dataframe(df)

        # Send file to FastAPI backend
        with st.spinner("Analyzing..."):
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), "text/csv")}
            data_payload = {"goal": goal}
            response = requests.post("http://localhost:8000/analyze", files=files, data=data_payload)

        if response.status_code == 200:
            data = response.json()
            st.subheader("Expense Summary")
            st.text(data["summary"])

            st.subheader("GPT Saving Tips")
            st.markdown(data["tips"])

            if "goal_advice" in data:
                st.subheader("Goal-Based Insight")
                st.markdown(data["goal_advice"])
        else:
            st.error("Something went wrong. Try again.")
            st.text(f"Status code: {response.status_code}\nDetails: {response.text}")

        # Plotly Charts
        if "Category" in df.columns and "Amount" in df.columns:
            st.subheader("Spending Breakdown Charts")
            bar_chart = px.bar(df, x="Category", y="Amount", title="Amount Spent per Category")
            pie_chart = px.pie(df, names="Category", values="Amount", title="Spending by Category")
            st.plotly_chart(bar_chart)
            st.plotly_chart(pie_chart)
        else:
            st.warning("CSV must contain 'Category' and 'Amount' columns for charts.")
