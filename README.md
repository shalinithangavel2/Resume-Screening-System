# Resume Screening System (ATS)

A Flask-based resume screening tool that helps HR teams quickly compare resumes against a job description, calculate an ATS match score, and keep track of candidates — all backed by a MySQL database.

I built this to understand how real-world ATS tools work under the hood: parsing resumes, matching skills, and scoring candidates automatically instead of doing it manually.

## Features

- HR login system
- Upload a candidate's resume (PDF)
- Paste in a job description
- Automatic job role detection from the JD
- Extracts candidate name, email, and phone number from the resume
- Matches resume skills against required skills from the JD
- Calculates an ATS score and flags candidates as Shortlisted / Not Shortlisted
- Detects duplicate candidates (by email or phone) before saving
- View, search, and filter all candidates by name, email, or job role
- Delete candidate records
- Dashboard with shortlisting statistics
- Export all candidate data to Excel

## Demo Videos

**Setup & Login**
A quick look at the login flow and dashboard.

https://github.com/shalinithangavel2/Resume-Screening-System/raw/main/demo/demo_setup.mp4

**Full Walkthrough**
Resume upload, ATS scoring, matched/missing skills, and the candidates dashboard.

https://github.com/shalinithangavel2/Resume-Screening-System/raw/main/demo/demo_walkthrough.mp4

*(If the videos above don't load, you can find them directly in the [`demo`](./demo) folder of this repo.)*

## Tech Stack

**Backend:** Python, Flask
**Database:** MySQL
**Frontend:** HTML, CSS
**Libraries:** pdfplumber, openpyxl, mysql-connector-python

## Project Structure

```
Resume-Screening-System/
│
├── app.py
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── candidates.html
│   └── candidate_details.html
│
├── static/
│   ├── style.css
│   └── images/
│
├── uploads/
├── README.md
└── .gitignore
```

## Getting Started

1. Clone the repository
   ```bash
   git clone https://github.com/shalinithangavel2/Resume-Screening-System.git
   cd Resume-Screening-System
   ```

2. Install the dependencies
   ```bash
   pip install flask pdfplumber mysql-connector-python openpyxl
   ```

3. Create a MySQL database named `ai_ats_resume_screening`, along with `hr_users` and `candidates` tables.

4. Update the database credentials in `app.py` to match your local MySQL setup.

5. Run the app
   ```bash
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

## How It Works

1. HR logs in.
2. Uploads a resume and pastes in the job description.
3. The app extracts the candidate's name, email, phone number, and job role.
4. It compares the resume's skills against the skills mentioned in the JD.
5. An ATS score is calculated, and the candidate is marked Shortlisted or Not Shortlisted.
6. The result — matched skills, missing skills, and score — is saved to the database (unless the candidate already exists).
7. HR can view all candidates, filter by role or status, and export the data to Excel.

## What's Next

A few things I'd like to add going forward:
- Smarter, ML-based resume ranking instead of pure keyword matching
- Edit options for candidate records
- Multi-user HR login with roles/permissions
- Email notifications to candidates
- PDF report generation for shortlisted candidates

## Author

**Shalini T**
B.Sc. Computer Science with Data Analytics

## License

This project was built for learning purposes and is free to use or reference.
