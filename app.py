import streamlit as st
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time

# ------------------ CONFIG ------------------ #
EXCEL_FILE = "alldata.xlsm"
SPREADSHEET_ID = "1y8SlCPHeeUHCi1o3vfjNhEF1bi2fQHtQ4NxHeRT_Blk"  # Replace with your Sheet ID
SHEET_NAME = "electivedata"    # Change if needed

# ------------------ GOOGLE SHEETS SETUP ------------------ #
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
service = build("sheets", "v4", credentials=creds)

def get_submitted_records():
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A2:F",
        ).execute()
        values = result.get("values", [])
        
        submitted_ids = set()
        sis_id_to_data = {}

        for row in values:
            if len(row) >= 3:
                sis_id = row[2]
                submitted_ids.add(sis_id)
                sis_id_to_data[sis_id] = row  # Store full row or customize to just electives

        return submitted_ids, sis_id_to_data

    except Exception as e:
        st.error(f"❌ Error reading from Google Sheet: {e}")
        return set(), {}


def write_to_google_sheet(row_data):
    body = {"values": [row_data]}
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A1",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

# ------------------ STREAMLIT UI ------------------ #
st.title("🎓 Elective Selection Form")

try:
    df = pd.read_excel(EXCEL_FILE)
except Exception as e:
    st.error(f"❌ Error reading Excel file: {e}")
    st.stop()

# Get SIS IDs that already submitted
submitted_ids, sis_id_to_data = get_submitted_records()

# Select name
student_names = ["-- Select Your Name --"] + list(df["STUDENT NAME"].unique())
selected_name = st.selectbox("🔍 Select Your Name", student_names, index=0)

if selected_name != "-- Select Your Name --":
    with st.spinner("Loading your details..."):
        time.sleep(1)

    student_row = df[df["STUDENT NAME"] == selected_name].iloc[0]
    sis_id = str(student_row["sis ID"]).strip()

    st.markdown("### 🧾 Student Details")
    st.write(f"**👤 Name:** {student_row['STUDENT NAME']}")
    st.write(f"**🆔 SIS ID:** {sis_id}")
    st.write(f"**🏷️ BR_coded:** {student_row['BR_coded']}")
    st.write(f"**📌 Allotted MDM Prog.:** {student_row['Allotted MDM Prog.']}")
    #st.write(f"**📌 Elective Branch selected:** {submitted_ids['Elective branch2']}")
    print(submitted_ids)

    

    if sis_id in submitted_ids:
        prev_data = sis_id_to_data[sis_id]
        elective_choices = prev_data[3:] 
        print(elective_choices[2]) # Assuming electives start from column 4 (index 3)

        st.info(f"✅ You have already submitted your elective choices: {(elective_choices[2])}")
        st.warning("You cannot submit again.")
    else:
        all_elective_options = ['EXTC', 'MECH', 'CSE', 'ELPO', 'IT']
        br_coded = str(student_row["BR_coded"]).strip().upper()
        mdm_prog = str(student_row["Allotted MDM Prog."]).strip().upper()
        excluded = set([br_coded, mdm_prog])

        if br_coded in ['CSE', 'IT']:
            excluded.update(['CSE', 'IT'])

        available_electives = [e for e in all_elective_options if e.upper() not in excluded]

        if available_electives:
            selected_elective = st.selectbox("🎯 Select Your Elective", available_electives)

            if st.button("✅ Submit"):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data_row = [
                    str(timestamp),
                    str(student_row["STUDENT NAME"]),
                    str(student_row["sis ID"]),
                    br_coded,
                    mdm_prog,
                    selected_elective
                ]
                try:
                    write_to_google_sheet(data_row)
                    st.success("🎉 Submission successful!")
                except Exception as e:
                    st.error(f"❌ Error writing to Google Sheet: {e}")
        else:
            st.warning("❗ No elective options available based on your branch and MDM.")
else:
    st.info("Please select your name to proceed.")
