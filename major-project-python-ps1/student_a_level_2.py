import sqlite3
from datetime import date

# --- SECURE Database Connection Setup ---
DATABASE_FILE = 'immunisation.db'

def fetch_data(query, params=()):
    """Connects to the database and executes a query using prepared statements."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        # Execute query with parameters for security (Prepared Statement)
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()
# ------------------------------------------------------------------

def get_page_html(form_data):
    print("Rendering Vaccination Data Filter page...")

    today = date.today().strftime("%d %B %Y")

    # === Get user inputs ===
    country_name = form_data.get("country", [""])[0]
    region = form_data.get("region", [""])[0]
    antigen_type = form_data.get("antigen_type", [""])[0]
    year = form_data.get("year", [""])[0]

    # === Build WHERE filters securely ===
    filters = []
    params = []
    
    # 1. Filter by Country Name (uses LIKE for partial matching)
    if country_name:
        # SECURE: Use ? placeholder for the value
        filters.append("C.name LIKE ?")
        # Add the actual value (with wildcards) to the params list
        params.append(f'%{country_name}%')

    # 2. Filter by Region Name (exact match)
    if region:
        # SECURE: Use ? placeholder for the value
        # Note: TRIM(LOWER(?)) is necessary for case-insensitive/robust matching in SQL
        filters.append("TRIM(LOWER(R.name)) = TRIM(LOWER(?))")
        params.append(region)

    # 3. Filter by Antigen Type (uses LIKE for partial matching)
    if antigen_type:
        # SECURE: Use ? placeholder for the value
        filters.append("A.AntigenName LIKE ?")
        params.append(f'%{antigen_type}%')
        
    # 4. Filter by Year (must be an exact match)
    if year and year.isdigit():
        # SECURE: Use ? placeholder for the value
        filters.append("V.year = ?")
        # Since the value is a known integer, we don't need wildcards
        params.append(int(year))
        
    # Combines all filters with "AND" or remains empty if no filters are selected
    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    # === SQL Query for Vaccination Data (Detailed View) ===
    query = f"""
    SELECT
        C.name,           -- Index 0: Country
        R.name,           -- Index 1: Region
        A.AntigenName,    -- Index 2: Antigen Type
        V.year,           -- Index 3: Year
        V.target_num,     -- Index 4: Target Population
        V.doses,          -- Index 5: Doses Administered
        ROUND(V.coverage, 2) -- Index 6: Coverage Rate (Rounded to 2 decimal places)
    FROM Vaccination V
    JOIN Country C ON V.country = C.CountryID
    JOIN Region R ON C.region = R.RegionID
    JOIN Antigen A ON V.antigen = A.AntigenID
    {where_clause}
    ORDER BY C.name, V.year DESC;
    """

    # === Run the query SECURELY ===
    # Pass the query with placeholders and the list of parameters to the secure function
    results = fetch_data(query, params)
    print("Results found:", len(results))

    # === Generate HTML Data Rows (CSS Grid format) ===
    
    # Function to format large numbers (e.g., 1000000 -> 1,000,000)
    def format_number(n):
        return f"{n:,.0f}" if isinstance(n, (int, float)) else n

    data_rows_html = "".join(
        f"""
        <div class="data-entry">
            <div class="data-field country">{row[0]}</div>
            <div class="data-field region">{row[1]}</div>
            <div class="data-field antigen">{row[2]}</div>
            <div class="data-field year">{row[3]}</div>
            <div class="data-field population">{format_number(row[4])}</div>
            <div class="data-field doses">{format_number(row[5])}</div>
            <div class="data-field percentage">{row[6]}%</div>
        </div>
        """
        for row in results
    ) or "<div class='data-field' style='grid-column: 1 / -1; text-align: center; padding: 15px;'>No data found based on filter criteria.</div>"


    # === Final HTML Layout ===
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Vaccination Data | Immunisation</title>
<link rel="stylesheet" href="/static/css/2a.css">
</head>
<body>
<div class="topnav">
    <div class="logo-title">
        <img src="/images/rmit.png" alt="Logo" class="logo">
        <span>Immunisation Data Portal</span>
    </div>
    <div class="nav-links">
        <a href="/">Home</a>
        <a href="/page5">Mission</a>
        <a class="active" href="/page2">Vaccination</a>
        <a href="/page4">Infection</a>
        <a href="/page3">Progress</a>
        <a href="/page6">Analysis</a>
    </div>
    <div class="search-container">
        <input type="text" placeholder="Search...">
    </div>
</div>

<div class="content-wrapper">
    <div class="filter-panel">
        <h2>Filter Vaccination Data</h2>
        <form method="get" action="/page2" class="filter-form">
            <label>Country Name:</label>
            <input type="text" name="country" value="{country_name}" placeholder="e.g. Australia">
            
            <label>Region:</label>
            <input type="text" name="region" value="{region}" placeholder="e.g. Oceania">

            <label>Antigen Type:</label>
            <input type="text" name="antigen_type" value="{antigen_type}" placeholder="e.g. MEAMCV1">

            <label>Year:</label>
            <input type="number" name="year" value="{year}" placeholder="e.g., 2022">

            <div class="apply-reset">
                <button type="submit" class="apply">Apply Filter</button>
                <a href="/page2" class="reset">Reset Filters</a>
            </div>
        </form>
    </div>

    <div class="data-panel">
        <h3>Vaccination Coverage Results by Country/Region</h3>
        
        <div class="data-list-container">
            <div class="data-entry header">
                <div class="data-field country">Country</div>
                <div class="data-field region">Region</div>
                <div class="data-field antigen">Antigen Type</div>
                <div class="data-field year">Year</div>
                <div class="data-field population">Target Population</div>
                <div class="data-field doses">Doses Administered</div>
                <div class="data-field percentage">Coverage Rate</div>
            </div>

            {data_rows_html}
            
        </div>
    </div>
</div>

<footer>
    <p>Help | Contacts | Sources</p>
    <p>Last Updated: {today}</p>
</footer>
</body>
</html>
"""