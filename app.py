import os
from dotenv import load_dotenv
from openpyxl import Workbook
from flask import Flask, render_template, request, redirect, send_file
import mysql.connector
import pdfplumber
import re

load_dotenv()

app = Flask(__name__)

# ------------------------------------
# MySQL Database Connection
# ------------------------------------

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = db.cursor()

print("Database Connected Successfully!")

# ------------------------------------
# Skill Database
# ------------------------------------

skill_database = [

    "Python",
    "SQL",
    "Excel",
    "Power BI",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Tableau",
    "Machine Learning",
    "Deep Learning",
    "Statistics",
    "Data Analysis",
    "Communication",
    "Problem Solving",
    "Leadership",
    "Git",
    "HTML",
    "CSS",
    "JavaScript",
    "Flask",
    "C",
    "C++",

    # Non-IT Skills

    "Communication Skills",
    "Teamwork",
    "Basic Computer Applications",
    "Office Automation",
    "Accounting Software",
    "Financial Modeling",
    "Fintech",
    "Microsoft Excel",
    "Attention to Detail",

    # Programming Skills

    "MySQL",
    "Object-Oriented Programming (OOP)",
    "Data Structures & Algorithms",
    "Database Programming",
    "Debugging & Testing",
    "CRM Applications",
    "Windows Operating Systems"

]

# ------------------------------------
# Login Page
# ------------------------------------

@app.route('/')
def home():

    return render_template("login.html")


# ------------------------------------
# Login Validation
# ------------------------------------

@app.route('/login', methods=['POST'])
def login():

    email = request.form.get("email")
    password = request.form.get("password")

    query = "SELECT * FROM hr_users WHERE email=%s AND password=%s"

    cursor.execute(query, (email, password))

    user = cursor.fetchone()

    if user:

        return render_template(
            "dashboard.html",
            candidate_name=None,
            email=None,
            phone=None,
            ats_score=None,
            status=None,
            matched_skills=[],
            missing_skills=[],
            recommendation=""
        )

    return render_template(
        "login.html",
        error="Invalid Email or Password"
    )


# ------------------------------------
# Resume Analysis
# ------------------------------------

@app.route('/analyze', methods=['POST'])
def analyze():

    job_description = request.form["jobDescription"]

    # ------------------------------------
    # Extract Job Role Automatically
    # ------------------------------------

    job_role = "Not Found"

    job_role_match = re.search(
        r"(Job\s*Title|Role|Position)\s*:\s*(.+)",
        job_description,
        re.IGNORECASE
    )

    if job_role_match:

        job_role = job_role_match.group(2).strip()

    print("Job Role :", job_role)

    # ------------------------------------
    # Read Resume
    # ------------------------------------

    resume = request.files["resumeFile"]

    resume_text = ""

    with pdfplumber.open(resume) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if text:

                resume_text += text

    print("========== JOB DESCRIPTION ==========")
    print(job_description)

    print("========== RESUME ==========")
    print(resume_text)

    # ------------------------------------
    # Extract Candidate Name
    # ------------------------------------

    candidate_name = ""

    lines = resume_text.split("\n")

    for line in lines:

        line = line.strip()

        if line:

            candidate_name = line
            break

    print("Candidate Name :", candidate_name)

        # ------------------------------------
    # Extract Email
    # ------------------------------------

    email_match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        resume_text
    )

    if email_match:

        email = email_match.group()

    else:

        email = "Not Found"

    print("Email :", email)

    # ------------------------------------
    # Extract Phone Number
    # ------------------------------------

    phone_match = re.search(
        r"(\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}",
        resume_text
    )

    if phone_match:

        phone = re.sub(r"\D", "", phone_match.group())

        if phone.startswith("91") and len(phone) == 12:

            phone = phone[2:]

    else:

        phone = "Not Found"

    print("Phone :", phone)

    # ------------------------------------
    # Extract Required Skills
    # ------------------------------------

    required_skills = []

    for skill in skill_database:

        if skill.lower() in job_description.lower():

            required_skills.append(skill)

    jd_skills = ", ".join(required_skills)

    print("Required Skills :", required_skills)
    print("JD Skills :", jd_skills)

    # ------------------------------------
    # Compare Resume Skills
    # ------------------------------------

    matched_skills = []

    missing_skills = []

    for skill in required_skills:

        if skill.lower() in resume_text.lower():

            matched_skills.append(skill)

        else:

            missing_skills.append(skill)

    print("Matched Skills :", matched_skills)
    print("Missing Skills :", missing_skills)
        # ------------------------------------
    # Calculate ATS Score
    # ------------------------------------

    if len(required_skills) > 0:

        ats_score = (len(matched_skills) / len(required_skills)) * 100

    else:

        ats_score = 0

    # ------------------------------------
    # Status & Recommendation
    # ------------------------------------

    if ats_score >= 70:

        status = "Shortlisted"

        recommendation = "Candidate is suitable for the next round."

    else:

        status = "Not Shortlisted"

        recommendation = "Candidate needs more matching skills."

    print("\n========== ATS RESULT ==========")

    print("Candidate Name :", candidate_name)
    print("Job Role :", job_role)
    print("Email :", email)
    print("Phone :", phone)
    print("Matched Skills :", matched_skills)
    print("Missing Skills :", missing_skills)
    print("ATS Score :", round(ats_score, 2))
    print("Status :", status)

    # ------------------------------------
    # Check Duplicate Candidate
    # ------------------------------------

    check_query = """
    SELECT * FROM candidates
    WHERE email=%s OR phone=%s
    """

    cursor.execute(check_query, (email, phone))

    existing_candidate = cursor.fetchone()

    # ------------------------------------
    # Save Candidate to Database
    # ------------------------------------

    if existing_candidate:

        return render_template(

            "dashboard.html",

            candidate_name=candidate_name,
            email=email,
            phone=phone,
            ats_score=round(ats_score, 2),
            status=status,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            message="⚠ Candidate already exists. Resume not saved."

        )

    insert_query = """
    INSERT INTO candidates
    (
        candidate_name,
        email,
        phone,
        job_role,
        jd_skills,
        ai_ats_score,
        status,
        matched_skills,
        missing_skills
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    values = (

        candidate_name,
        email,
        phone,
        job_role,
        jd_skills,
        round(ats_score, 2),
        status,
        ", ".join(matched_skills),
        ", ".join(missing_skills)

    )

    cursor.execute(insert_query, values)

    db.commit()

    print("Candidate Saved Successfully!")

    # ------------------------------------
    # Return Dashboard
    # ------------------------------------

    return render_template(

        "dashboard.html",

        candidate_name=candidate_name,

        email=email,

        phone=phone,

        ats_score=round(ats_score, 2),

        status=status,

        matched_skills=matched_skills,

        missing_skills=missing_skills,

        recommendation=recommendation

    )

# ------------------------------------
# View All Candidates
# ------------------------------------# ------------------------------------
# View All Candidates
# ------------------------------------

@app.route('/candidates')
def candidates():

    search = request.args.get("search", "")
    status = request.args.get("status", "")
    job_role = request.args.get("job_role", "")

    query = "SELECT * FROM candidates WHERE 1=1"
    values = []

    # Search by Candidate Name
    if search:
        query += """
        AND (
        candidate_name LIKE %s
        OR email LIKE %s
        OR job_role LIKE %s
        )
        """

        values.extend([
        "%" + search + "%",
        "%" + search + "%",
        "%" + search + "%"
        ])

    # Filter by Status
    if status:
        query += " AND status=%s"
        values.append(status)

    # Filter by Job Role
    if job_role:
        query += " AND job_role=%s"
        values.append(job_role)

    query += " ORDER BY id DESC"

    cursor.execute(query, tuple(values))
    candidate_list = cursor.fetchall()

    # ------------------------------------
    # Dashboard Statistics
    # ------------------------------------

    if job_role:

        cursor.execute(
            "SELECT COUNT(*) FROM candidates WHERE job_role=%s",
            (job_role,)
        )
        total_candidates = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM candidates
            WHERE job_role=%s
            AND status='Shortlisted'
            """,
            (job_role,)
        )
        shortlisted = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM candidates
            WHERE job_role=%s
            AND status='Not Shortlisted'
            """,
            (job_role,)
        )
        not_shortlisted = cursor.fetchone()[0]

    else:

        cursor.execute("SELECT COUNT(*) FROM candidates")
        total_candidates = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM candidates WHERE status='Shortlisted'"
        )
        shortlisted = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM candidates WHERE status='Not Shortlisted'"
        )
        not_shortlisted = cursor.fetchone()[0]

    # ------------------------------------
    # Get All Job Roles
    # ------------------------------------

    cursor.execute("""
        SELECT DISTINCT job_role
        FROM candidates
        WHERE job_role IS NOT NULL
        ORDER BY job_role
    """)

    job_roles = cursor.fetchall()

    # ------------------------------------
    # Render Page
    # ------------------------------------

    return render_template(

        "candidates.html",

        candidates=candidate_list,

        total_candidates=total_candidates,

        shortlisted=shortlisted,

        not_shortlisted=not_shortlisted,

        search=search,

        status=status,

        job_role=job_role,

        job_roles=job_roles

    )


# ------------------------------------
# Export Candidates to Excel
# ------------------------------------

@app.route('/export')
def export():

    cursor.execute("SELECT * FROM candidates")

    candidates = cursor.fetchall()

    wb = Workbook()

    ws = wb.active

    ws.title = "Candidates"

    ws.append([
        "ID",
        "Candidate Name",
        "ATS Score",
        "Status",
        "Matched Skills",
        "Missing Skills",
        "Email",
        "Phone",
        "Job Role",
        "JD Skills"
    ])

    for candidate in candidates:

        ws.append(candidate)

    wb.save("Candidates.xlsx")

    return send_file(
        "Candidates.xlsx",
        as_attachment=True
    )


# ------------------------------------
# Candidate Details
# ------------------------------------

@app.route('/candidate/<int:id>')
def candidate_details(id):

    query = "SELECT * FROM candidates WHERE id=%s"

    cursor.execute(query, (id,))

    candidate = cursor.fetchone()

    return render_template(
        "candidate_details.html",
        candidate=candidate
    )
# ------------------------------------
# Delete Candidate
# ------------------------------------

@app.route('/delete/<int:id>')
def delete_candidate(id):

    query = "DELETE FROM candidates WHERE id=%s"

    cursor.execute(query, (id,))

    db.commit()

    return redirect("/candidates")

# ------------------------------------
# Run Flask
# ------------------------------------

if __name__ == "__main__":

    app.run(debug=True)