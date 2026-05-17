from flask import Flask, render_template, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import os


app = Flask(__name__)

# ---------------- GOOGLE SHEETS CONNECTION ----------------

google_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    google_creds,
    scope
)


client = gspread.authorize(creds)

# Replace with your sheet name
sheet = client.open("StudentDatabase").sheet1


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- SUBMIT DATA ----------------

@app.route("/submit", methods=["POST"])
def submit():

    try:
        # Get form data
        name = request.form["name"]
        roll = request.form["roll"]
        cpi = request.form["cpi"]

        # Current time
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get all records
        records = sheet.get_all_records()

        found = False

        # Start checking from row 2
        for index, record in enumerate(records, start=2):

            # IMPORTANT:
            # Column name must EXACTLY match your sheet heading
            if str(record["ROLL NO."]) == str(roll):

                # Update existing row
                sheet.update(
                    f"A{index}:D{index}",
                    [[name, roll, cpi, time_now]]
                )

                found = True
                break

        # If roll number not found -> add new row
        if not found:

            sheet.append_row([
                name,
                roll,
                cpi,
                time_now
            ])

        return f"""
        <h1>Data Saved Successfully!</h1>

        <p><b>Name:</b> {name}</p>
        <p><b>Roll Number:</b> {roll}</p>
        <p><b>CPI:</b> {cpi}</p>

        <br>

        <a href="/">Go Back</a>
        """

    except Exception as e:

        return f"""
        <h1>Error Occurred</h1>

        <p>{e}</p>

        <br>

        <a href="/">Go Back</a>
        """


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)