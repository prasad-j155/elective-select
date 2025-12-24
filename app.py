import streamlit as st
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ------------------ CONFIG ------------------ #
EXCEL_FILE = "student-new.xlsx"
SPREADSHEET_ID = "1y8SlCPHeeUHCi1o3vfjNhEF1bi2fQHtQ4NxHeRT_Blk"  # Replace with your Sheet ID
SHEET_NAME = "electivedata"  # Or change to your actual sheet name

# ------------------ GOOGLE SHEETS SETUP ------------------ #
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
service = build("sheets", "v4", credentials=creds)

def get_submitted_records():
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A2:G",
        ).execute()
        values = result.get("values", [])

        submitted_ids = set()
        sis_id_to_data = {}

        for row in values:
            if len(row) >= 2:
                sis_id = row[1].strip()
                submitted_ids.add(sis_id)
                sis_id_to_data[sis_id] = row

        return submitted_ids, sis_id_to_data

    except Exception as e:
        st.error(f"❌ Error reading from Google Sheet: {e}")
        return set(), {}

def branch_to_sub(branch):
    if branch == 'CSE':
        return 'CSE : Information Systems for Engineers'
    elif branch == 'MECH':
        return 'MECH : Automotive Technology'
    elif branch == 'ELPO':
        return 'ELPO : Electrical Machines'
    elif branch == 'EXTC':
        return 'EXTC : Satellite Communication'
    elif branch == 'IT':
        return 'IT : Artificial Intelligence'

def write_to_google_sheet(row_data):
    body = {"values": [row_data]}
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A1",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

# ------------------ STREAMLIT UI ------------------ #
#st.markdown("### This is a smaller title")
st.markdown("#### SHRI SANT GAJANAN MAHARAJ COLLEGE OF ENGINEERING,SHEGAON")
st.title("🎓 Elective Selection Form")

try:
    df = pd.read_excel(EXCEL_FILE)
except Exception as e:
    st.error(f"❌ Error reading Excel file: {e}")
    st.stop()

submitted_ids, sis_id_to_data = get_submitted_records()

# Session states
if "sis_verified" not in st.session_state:
    st.session_state.sis_verified = False

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ------------------ FINAL THANK YOU ------------------ #
if st.session_state.submitted:
    st.success("🎉 Thank you! Your response has been recorded.")
    st.stop()

# ------------------ SIS ID Step ------------------ #
if not st.session_state.sis_verified:
    entered_sis_id = st.text_input("🔢 Enter Your SIS ID")
    if st.button("Next"):
        if entered_sis_id:
            sis_id_str = entered_sis_id.strip().upper()
            #sis_id_str = entered_sis_id.strip()
            matching_row = df[df["sis ID"].astype(str).str.strip().str.upper() == sis_id_str]
            #matching_row = df[df["sis ID"].astype(str).str.strip() == sis_id_str]

            if not matching_row.empty:
                st.session_state.sis_id = sis_id_str
                st.session_state.student_row = matching_row.iloc[0]
                st.session_state.sis_verified = True
            else:
                st.error("❌ SIS ID not found. Please check and try again.")
        else:
            st.warning("Please enter a valid numeric SIS ID.")

# ------------------ Elective Selection Step ------------------ #
if st.session_state.sis_verified:
    student_row = st.session_state.student_row
    sis_id_str = st.session_state.sis_id
    student_name = student_row["STUDENT NAME"]
    branch = str(student_row["Br."]).strip().upper()
    br_coded = str(student_row["BR_coded"]).strip().upper()
    mdm_prog = str(student_row["Allotted MDM Prog."]).strip().upper()

    st.markdown("### 🧾 Student Details")
    st.write(f"**👤 Name:** {student_name}")
    st.write(f"**🆔 SIS ID:** {sis_id_str}")
    st.write(f"**🏷️ Branch:** {branch}")
    st.write(f"**📌 Allotted MDM Programme:** {mdm_prog}")

    if sis_id_str in submitted_ids:
        prev_data = sis_id_to_data[sis_id_str]
        prev_elective = prev_data[6] if len(prev_data) > 6 else "N/A"
        
        st.info(f"✅ You have already submitted your elective choice: **{prev_elective}**")
        st.warning("You cannot submit again.")
        st.stop()  
    else:
        all_elective_options = ['EXTC', 'MECH', 'CSE', 'ELPO', 'IT']
        excluded = set([br_coded, mdm_prog])

        if br_coded in ['CSE', 'IT']:
            excluded.update(['CSE', 'IT'])

        available_electives = [e for e in all_elective_options if e.upper() not in excluded]
        options_display = [branch_to_sub(i) for i in available_electives]
        options_display.insert(0, "select your elective")
        
        

        with st.form("elective_form"):
            selected_elective = st.selectbox("🎯 Select Your Elective", options_display)
            #st.write(selected_elective=="select your elective")

            
            submit_final = st.form_submit_button("✅ Submit")

            if submit_final:
                if selected_elective=="select your elective":
                    st.warning("⚠️ Please select an elective before submitting.")
                else:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    data_row = [
                        timestamp,
                        sis_id_str,
                        student_name,
                        br_coded,
                        branch,
                        mdm_prog,
                        selected_elective
                    ]
                    try:
                        write_to_google_sheet(data_row)
                        st.session_state.submitted = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error writing to Google Sheet: {e}")

















