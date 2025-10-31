from datetime import date
import sqlite3
import pyhtml # Added import for pyhtml utility

# --- SECURE Database Connection Setup ---
DATABASE_FILE = 'immunisation.db'

# NOTE: Since all queries in this file are hardcoded strings without user input,
# the simpler sqlite3 logic is acceptable, but a secure pattern is best practice.
# We keep the original structure for simplicity, ensuring it connects.

def get_page_html(form_data):
    # Print statement for debugging/logging
    print("About to return Home page...")

    # Get today's date in a specified format
    today = date.today().strftime("%d %B %Y")

    # Initialize variables with defaults in case of a database error
    personas = []
    team = []
    total_vacc_doses = "N/A"
    total_cases = "N/A"
    infection_types = "N/A"
    total_countries = "N/A"

    # === Database Access using pyhtml utility ===
    try:
        # === Fetch Persona data (image, name, occupation) ===
        personas = pyhtml.get_results_from_query(DATABASE_FILE, "SELECT image_path, name, occupation FROM Persona;")

        # === Fetch Team data (full name and student ID) ===
        team = pyhtml.get_results_from_query(DATABASE_FILE, "SELECT (FirstName || ' ' || LastName) AS FullName, StudentID FROM Team;")

        # === Fetch Data for Facts Section (Total Vaccination Doses, etc.) ===
        
        # 1. Total Vaccination Doses (SUM(doses))
        # pyhtml.get_results_from_query returns a list of tuples, e.g., [(value,)]
        total_vacc_doses_raw = pyhtml.get_results_from_query(DATABASE_FILE, "SELECT SUM(doses) FROM Vaccination")
        total_vacc_doses = "N/A"
        if total_vacc_doses_raw and total_vacc_doses_raw[0] and total_vacc_doses_raw[0][0] is not None:
            # Access the value via [0][0] since it's a list containing one tuple with one element.
            doses = total_vacc_doses_raw[0][0] / 1000000000  # Convert to billions
            total_vacc_doses = f"{doses:,.1f} Billion"

        # 2. Total Reported Cases (SUM(cases))
        total_cases_raw = pyhtml.get_results_from_query(DATABASE_FILE, "SELECT SUM(cases) FROM InfectionData")
        total_cases = "N/A"
        if total_cases_raw and total_cases_raw[0] and total_cases_raw[0][0] is not None:
            # Format as a large number (e.g., 50M)
            total_cases = f"{total_cases_raw[0][0]:,.0f}"

        # 3. Infection Types (COUNT(DISTINCT description))
        infection_types_raw = pyhtml.get_results_from_query(DATABASE_FILE, "SELECT COUNT(DISTINCT description) FROM Infection_Type")
        infection_types = "N/A"
        if infection_types_raw and infection_types_raw[0] and infection_types_raw[0][0] is not None:
             infection_types = infection_types_raw[0][0]

        # 4. Countries Tracked (COUNT(DISTINCT CountryID))
        total_countries_raw = pyhtml.get_results_from_query(DATABASE_FILE, "SELECT COUNT(DISTINCT CountryID) FROM Country")
        total_countries = "N/A"
        if total_countries_raw and total_countries_raw[0] and total_countries_raw[0][0] is not None:
             total_countries = total_countries_raw[0][0]

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        personas = []
        team = []
        total_vacc_doses = "DB ERROR"
        total_cases = "DB ERROR"
        infection_types = "DB ERROR"
        total_countries = "DB ERROR"
    
    # === Build Persona section dynamically ===
    persona_html = "".join(
    f"""
        <div class="persona-card">
            <div class="persona-img-wrapper">
               <img src="{img}" alt="{name}" width="20" height="30" style="border-radius: 20%;">
            </div>
            <div class="persona-details">
                <strong>{name}</strong>
                <p>{occupation}</p>
            </div>
        </div>
    """
    for img, name, occupation in personas
    ) or "<p>No persona data available.</p>"

    # === Build Team section dynamically ===
    team_html = "<ul class=\"team-list\">"
    team_html += "".join(
        f"<li>{name} ({id})</li>"
        for name, id in team
    ) or "<li>No team data available.</li>"
    team_html += "</ul>"


    # === Final HTML Layout ===
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Home | Immunisation Data Portal</title>
<link rel="stylesheet" href="/static/css/1a.css">
</head>
<body>
    <div class="topnav">
        <div class="logo-title">
            <img src="/images/rmit.png" alt="Logo" class="logo">
            <span>Immunisation Data Portal</span>
        </div>
        <div class="nav-links">
            <a class="active" href="/">Home</a>
            <a href="/page5">Mission</a>
            <a href="/page2">Vaccination</a>
            <a href="/page4">Infection</a>
            <a href="/page3">Progress</a>
            <a href="/page6">Analysis</a>
        </div>
        <div class="search-container">
            <input type="text" placeholder="Search...">
        </div>
    </div>

    <div class="container">
        <div class="main-content-area">
            <div class="left-column">
                <div class="content-box">
                    <h2>Global Health Snapshot</h2>
                    <div class="fact-grid">
                        <div class="fact-box">
                            <span class="fact-value">{total_vacc_doses}</span>
                            <br>Total Vaccination Doses
                        </div>
                        <div class="fact-box">
                            <span class="fact-value">{total_cases}</span>
                            <br>Total Reported Cases
                        </div>
                        <div class="fact-box">
                            <span class="fact-value">{infection_types}</span>
                            <br>Infection Types
                        </div>
                        <div class="fact-box">
                            <span class="fact-value">{total_countries}</span>
                            <br>Countries Tracked
                        </div>
                    </div>
                </div>

                <div class="flex-row">
                    <div class="column content-box">
                        <div class="info-box">
                            <h3>How does it work?</h3>
                            <div class="box-content">
                                This project visualizes vaccination and infection data
                                from multiple countries and regions, highlighting
                                progress and global health patterns.
                            </div>
                        </div>
                    </div>
                    <div class="column content-box">
                        <div class="info-box">
                            <h3>Social Challenge & Solution</h3>
                            <div class="box-content">
                                Uneven vaccination rates across regions create
                                health disparities. Our platform presents clear,
                                accessible data to support informed policy
                                and community action.
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="right-column">
                <div class="info-box">
                    <h3>Personas</h3>
                    <div class="personas">
                        {persona_html}
                    </div>
                </div>

                <div class="info-box">
                    <h3>Our Team</h3>
                    {team_html}
                </div>
            </div>

        </div> 
    </div>

    <footer>
        <p>Help | Contacts | Sources</p>
        <p>Last Updated: {today}</p>
    </footer>

</body>
</html>"""

    return page_html