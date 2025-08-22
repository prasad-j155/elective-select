import streamlit as st
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build


# ------------------ CONFIG ------------------ #
EXCEL_FILE = "alldata.xlsm"
SPREADSHEET_ID = "1y8SlCPHeeUHCi1o3vfjNhEF1bi2fQHtQ4NxHeRT_Blk"  # Replace with your Sheet ID
SHEET_NAME = "electivedata"    # Change if needed

# ------------------ GOOGLE SHEETS SETUP ------------------ #
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
#creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
service = build("sheets", "v4", credentials=creds)




def write_to_google_sheet(row_data):
    body = {"values": [row_data]}
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A1",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

def branch_to_sub(branch):
    if branch == 'CSE':
        return 'CSE : E-Commerce'
    elif branch == 'MECH':
        return 'MECH : Engineering Materials'
    elif branch == 'ELPO':
        return 'ELPO : Power Supply System'
    elif branch == 'EXTC':
        return 'EXTC : Analog Communication'
    elif branch == 'IT':
        return 'IT : Cyber Law'

# ------------------ STREAMLIT UI ------------------ #
st.markdown("#### SHRI SANT GAJANAN MAHARAJ COLLEGE OF ENGINEERING,SHEGAON")
st.title("🎓 Elective Selection Form")
st.markdown(
    "#### 📢(for diploma students only)"
)
# Session state for re-rendering dropdowns
if "selected_branch" not in st.session_state:
    st.session_state.selected_branch = None
if "selected_mdm" not in st.session_state:
    st.session_state.selected_mdm = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ------------------ FINAL THANK YOU ------------------ #
if st.session_state.submitted:
    st.success("🎉 Thank you! Your response has been recorded.")
    st.stop()

# ------------------ Name ------------------ #
student_name = st.text_input("👤 Student Name")

# ------------------ Branch ------------------ #
branch_options = ['CSE', 'IT', 'MECH', 'EXTC', 'ELPO']
branch = st.selectbox("🏷️ Select Your Branch", branch_options)
st.session_state.selected_branch = branch

# ------------------ Class ------------------ #
class_options = ['2M', '2S', '2R', '2N', '2U1','2U2']

if branch =='CSE':
    class_options = ['2R']
elif branch == 'IT':
    class_options = ['2N']
elif branch =='MECH':
    class_options =['2M']
elif branch =='ELPO':
    class_options=['2S']
elif branch =='EXTC':
    class_options =['2U1','2U2']
else:
    class_options=['2M', '2S', '2R', '2N', '2U1','2U2']

class_options_sel = st.selectbox("📘 Select Your Class", class_options)


# ------------------ MDM Programme ------------------ #
mdm_excluded = set([branch])
# Special case for CSE / IT
if branch in ["CSE", "IT"]:
    mdm_excluded.update(["CSE", "IT"])

mdm_options = [b for b in branch_options if b not in mdm_excluded]
mdm = st.selectbox("🧾 Select Your MDM Programme", mdm_options)
st.session_state.selected_mdm = mdm

# ------------------ Elective Selection ------------------ #
#print("branch",branch)
if branch in ["CSE", "IT"]:
    excluded_electives = set([branch, mdm,"CSE","IT"])
else:
    excluded_electives = set([branch, mdm])
    


# special logic for CSE / IT already handled above by mdm field


available_electives_codes = [b for b in branch_options if b not in excluded_electives]
available_elective_labels = [branch_to_sub(code) for code in available_electives_codes]

elective_selected = st.selectbox("🎯 Select Your Elective", available_elective_labels)

# ------------------ Submit ------------------ #
if st.button("✅ Submit"):
    if not student_name:
        st.warning("Please enter your name before submitting.")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_row = [
            timestamp,
            student_name,
            branch,
            class_options_sel,
            mdm,
            elective_selected
        ]
        try:
            write_to_google_sheet(data_row)
            st.session_state.submitted = True
            st.success("🎉 Thank you! Your response has been recorded.")
        except Exception as e:
            st.error(f"❌ Error writing to Google Sheet: {e}")









