from datetime import date
import sqlite3

def get_page_html(form_data):
    print("About to return Home page...")

    today = date.today().strftime("%d %B %Y")

    # === Connect to database ===
    conn = sqlite3.connect("immunisation.db")
    cursor = conn.cursor()

    # === Fetch Persona data (image, name, occupation) ===
    cursor.execute("SELECT image_path, name, occupation FROM Persona;")
    personas = cursor.fetchall()

    # === Fetch Team data (full name and student ID) ===
    cursor.execute("SELECT (FirstName || ' ' || LastName) AS FullName, StudentID FROM Team;")
    team = cursor.fetchall()

    conn.close()

    # === Build Persona section dynamically ===
    persona_html = "".join(
    f"""
        <div class="persona-card">
            <div class="persona-img-wrapper">
               <img src="{img}" alt="{name}" width="100" height="100" style="border-radius: 5%; object-fit: cover; display: block; margin: 10px auto;" class="persona-img">

            </div>
            <p><b>{name}</b><br>{occupation}</p>
        </div>
        """
    for img, name, occupation in personas
)


    # === Build Team section dynamically ===
    team_html = "".join(
        f"<p>{full_name} — {student_id}</p>"
        for full_name, student_id in team
    )

    # === Final HTML ===
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home | Immunization Data Project</title>
    <link rel="stylesheet" href="/static/css/1b.css">
</head>
<body>

    <!-- ===== Top Navigation ===== -->
    <div class="topnav">
        <div class="logo-title">
            <img src="images/rmit.png" alt="Logo" class="logo">
            <span>Immunization Data Project</span>
        </div>

        <div class="nav-links">
            <a href="/">Home</a>
            <a class="active" href="/page5">Mission</a>
            <a href="/page2">Vaccination</a>
            <a href="/page4">Infection</a>
            <a href="/page3">Progress</a>
            <a href="/page6">Analysis</a>
        </div>

        <div class="search-container">
            <input type="text" placeholder="Search...">
        </div>
    </div>

    <!-- ===== Main Content ===== -->
    <div class="container">
        <div class="info-box">
            <h3>How does it work?</h3>
            <div class="box-content">
                This project visualizes vaccination and infection data
                from multiple countries and regions, highlighting
                progress and global health patterns.
            </div>
        </div>

        <div class="info-box">
            <h3>Personas</h3>
            <div class="personas">
                {persona_html}
            </div>
        </div>

        <div class="info-box">
            <h3>Social Challenge & Solution</h3>
            <div class="box-content">
                Uneven vaccination rates across regions create
                health disparities. Our platform presents clear,
                accessible data to support informed policy
                and community action.
            </div>
        </div>

        <div class="info-box">
            <h3>Our Team</h3>
            {team_html}
        </div>
    </div>

    <!-- ===== Footer ===== -->
    <footer>
        <p>Help | Contacts | Sources</p>
        <p>Last Updated: {today}</p>
    </footer>

</body>
</html>"""

    return page_html