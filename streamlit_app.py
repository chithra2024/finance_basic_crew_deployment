import os
import streamlit as st
import requests
from dotenv import load_dotenv
from markdown import markdown

# Load environment variables
load_dotenv()
KICKOFF_URL = os.getenv("KICKOFF_URL")
STATUS_URL = os.getenv("STATUS_URL")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

st.set_page_config(page_title="CrewAI Report Viewer", layout="centered")
st.title("📈 CrewAI Generator")

# Input fields
topic = st.text_input("Topic", placeholder="e.g. Stock Market")
current_year = st.text_input("Year", placeholder="e.g. 2025")

# Session state for kickoff ID and result
if "kickoff_id" not in st.session_state:
    st.session_state.kickoff_id = None
if "crew_output" not in st.session_state:
    st.session_state.crew_output = ""

# Start Crew
if st.button("🚀 Start Crew"):
    if not topic or not current_year:
        st.warning("Please fill in both topic and year.")
    else:
        payload = {
            "inputs": {
                "topic": topic,
                "current_year": current_year
            }
        }
        try:
            res = requests.post(
                KICKOFF_URL,
                headers={
                    "Authorization": f"Bearer {BEARER_TOKEN}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            res.raise_for_status()
            data = res.json()
            st.session_state.kickoff_id = data.get("kickoff_id")
            st.info("🚀 Crew started. You can now click 'Get Result'.")
            st.code(f"Kickoff ID: {st.session_state.kickoff_id}")
        except Exception as e:
            st.error(f"Error: {e}")

# Get Result
if st.button("📥 Get Result"):
    kickoff_id = st.session_state.kickoff_id
    if not kickoff_id:
        st.warning("No kickoff ID found. Start the crew first.")
    else:
        try:
            res = requests.get(
                f"{STATUS_URL}{kickoff_id}",
                headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
            )
            res.raise_for_status()
            data = res.json()

            if data["state"] == "SUCCESS" and data.get("last_executed_task", {}).get("output"):
                agent = data["last_executed_task"].get("agent", "Agent")
                output_md = data["last_executed_task"]["output"]
                st.markdown(f"### 👤 {agent}")
                st.markdown(output_md)
            elif data["state"] != "SUCCESS":
                st.info("⏳ Still processing. Please wait and try again.")
            else:
                st.warning("⚠️ Result not yet available.")
        except Exception as e:
            st.error(f"Error: {e}")
