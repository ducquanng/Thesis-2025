# --- Streamlit & app module imports ---
import streamlit as st
import tempfile

# Import functions from the core logic file
from core import (
    initialize_chat_models,
    load_or_create_vectorstore,
    generate_cold_email,
    parse_input,
)

# --- App Page Config ---
st.set_page_config(page_title="MKB Werkplaats", layout="wide")

def main():
    # --- Page Title & Intro ---
    st.title("📬 Marketing Email Generator")
    st.markdown("""
Welcome to the MKB Marketing Email Generator — an app that automatically generates personalized invitations for innovation challenges for Dutch SMEs.
    """)

    # --- Step 1: Upload Excel File ---
    st.markdown("## 📄 Step 1: Upload Excel file")
    uploaded_file = st.file_uploader("Upload your Challenge Excel file", type=["xlsx"])

    if uploaded_file:
        # Save uploaded Excel to a temporary file
        temp_excel = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        temp_excel.write(uploaded_file.read())
        excel_path = temp_excel.name
    else:
        # Use default path if no file uploaded
        excel_path = "MKB-challenge-data.xlsx"

    # --- Step 2: User Inputs Challenge & Company Name ---
    st.markdown("## 💬 Step 2: Enter Challenge + Company name")
    user_input = st.text_input("Format: 'Challenge Name | Company Name'")

    # --- Step 3: Generate Email on Button Click ---
    if st.button("Generate Email"):
        # Validate input format
        challenge_name, company_name = parse_input(user_input)
        if not challenge_name or not company_name:
            st.error("Incorrect format. Use: 'Challenge Name | Company Name'")
            return

        # --- Load vectorstore and chat model ---
        with st.spinner("Loading data and AI models..."):
            try:
                # Load (or create) the FAISS vectorstore from Excel
                vectorstore = load_or_create_vectorstore(excel_path)
                # Initialize GPT-4 chat model
                chat_models = initialize_chat_models()
            except Exception as e:
                st.error(f"Error loading resources: {e}")
                return

        # --- Generate the personalized cold email ---
        with st.spinner("Generating personalized email..."):
            try:
                email = generate_cold_email(
                    challenge_name,
                    company_name,
                    vectorstore,
                    chat_models["chat"]
                )
                # Display the email in markdown format
                st.markdown(f"{email.splitlines()[0]}\n\n" + "\n".join(email.splitlines()[1:]))
            except Exception as e:
                st.error(f"Email generation failed: {e}")

# --- Streamlit App Entry Point ---
if __name__ == '__main__':
    main()
