import streamlit as st
import requests
import time

st.title("💊 Insurance Charges Prediction App (FastAPI Backend)")
st.write("Enter customer details and get insurance charge prediction.")

# USER INPUTS
age = st.slider("Age", 18, 80, 35)
sex = st.radio("Sex", ["Male", "Female"])
bmi = st.number_input("BMI", 10.0, 50.0, 25.0, step=0.1)
children = st.slider("Number of Children", 0, 5, 0)
smoker = st.radio("Smoker", ["Yes", "No"])
region = st.selectbox("Region", ["southeast", "other"])

# JSON Payload for FastAPI
payload = {
    "age": age,
    "sex": sex,
    "bmi": bmi,
    "children": children,
    "smoker": smoker,
    "region": region
}

# Backend URL
BACKEND_URL = "https://insurance-backend-api.onrender.com/predict"
# Function: Call backend with retry + long timeout
def call_backend_with_retry(data, retries=3, timeout=40):
    for attempt in range(retries):
        try:
            return requests.post(BACKEND_URL, json=data, timeout=timeout)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(3)
            else:
                raise e


# Predict Button
if st.button("Predict Insurance Charges"):
    with st.spinner("Backend waking up... please wait (Render Free Tier)..."):
        try:
            response = call_backend_with_retry(payload, retries=3, timeout=40)

            if response.status_code == 200:
                result = response.json()
                charges = result["predicted_insurance_charges"]

                st.subheader("💰 Estimated Insurance Charges")
                st.success(f"₹ {charges:,.2f}")

            else:
                st.warning("⚠️ FastAPI returned an error. Check backend logs.")

        except Exception as e:
            st.error(f"❌ Error connecting to FastAPI: {e}")
