import sqlite3
from datetime import date
import pyhtml # ADDED

# --- Database Connection Setup ---
DATABASE_FILE = 'immunisation.db'

# REMOVED: The custom fetch_data function is removed as it's replaced by pyhtml.get_results_from_query

def get_page_html(form_data):
    print("Rendering Vaccination Data Filter page...")

    today = date.today().strftime("%d %B %Y")

    # === Get user inputs ===
    # .get() returns a list, so [0] retrieves the value, default to ""
    country_name = form_data.get("country", [""])[0].strip() 
    region = form_data.get("region", [""])[0].strip()
    antigen_type = form_data.get("antigen_type", [""])[0].strip()
    year = form_data.get("year", [""])[0].strip() # Check if it's a digit later

    # === Build WHERE filters using string formatting (Required for pyhtml utility) ===
    filters = []
    
    # NOTE: String concatenation is generally insecure (SQL Injection risk). 
    # This method is required to interface with the provided pyhtml.get_results_from_query
    
    # 1. Filter by Country Name (uses LIKE for partial matching)
    if country_name:
        # Basic escaping for single quotes (to prevent breaking the query string)
        safe_country_name = country_name.replace("'", "''") 
        filters.append(f"C.CountryName LIKE '%{safe_country_name}%'")

    # 2. Filter by Region Name
    if region:
        safe_region = region.replace("'", "''")
        filters.append(f"R.RegionName LIKE '%{safe_region}%'")

    # 3. Filter by Antigen Type (exact match)
    if antigen_type:
        safe_antigen_type = antigen_type.replace("'", "''")
        filters.append(f"V.Antigen = '{safe_antigen_type}'")

    # 4. Filter by Year (exact match)
    if year.isdigit():
        filters.append(f"Y.YearID = {year}")

    # === Build the main query ===
    where_clause = " AND ".join(filters)
    if where_clause:
        where_clause = " WHERE " + where_clause
        
    query = f"""
        SELECT
            C.CountryName, R.RegionName, V.Antigen, Y.YearID,
            V.target_num, V.doses, V.coverage
        FROM Vaccination V
        JOIN Country C ON V.Country = C.CountryID
        JOIN Region R ON C.RegionID = R.RegionID
        JOIN YearDate Y ON V.Year = Y.YearID
        {where_clause}
        ORDER BY C.CountryName, Y.YearID DESC;
    """

    # === Fetch Data using pyhtml.get_results_from_query ===
    try:
        results = pyhtml.get_results_from_query(DATABASE_FILE, query)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        results = []


    # === Process results for HTML table ===
    data_rows_html = ""
    if not results:
        data_rows_html = f"""
            <div class="data-entry no-results">
                No vaccination data found for the given criteria.
            </div>
        """
    else:
        for country, region_name, antigen, year_id, target_num, doses, coverage in results:
            
            # Formatting numeric values
            # Target num and doses: Format as integer with thousand separators or "N/A"
            target_num_str = f"{int(target_num):,}" if target_num is not None else "N/A"
            doses_str = f"{int(doses):,}" if doses is not None else "N/A"
            
            # Coverage: Format as percentage (e.g., 95.0%) or "N/A"
            coverage_str = f"{coverage:.1f}%" if coverage is not None else "N/A"
            
            # Optional: Add class for low coverage
            coverage_class = "percentage low" if coverage is not None and coverage < 50 else "percentage"
            
            data_rows_html += f"""
                <div class="data-entry">
                    <div class="data-field country">{country}</div>
                    <div class="data-field region">{region_name}</div>
                    <div class="data-field antigen">{antigen}</div>
                    <div class="data-field year">{year_id}</div>
                    <div class="data-field population">{target_num_str}</div>
                    <div class="data-field doses">{doses_str}</div>
                    <div class="data-field {coverage_class}">{coverage_str}</div>
                </div>
            """

    # === Final HTML Layout (No changes to the presentation logic) ===
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Vaccination Data | Immunisation Portal</title>
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
            <a class="active" href="/page2">Vaccination</a>
            <a href="/page5">Mission</a>
            <a href="/page4">Infection</a>
            <a href="/page3">Progress</a>
            <a href="/page6">Analysis</a>
        </div>
        <div class="search-container">
            <input type="text" placeholder="Search...">
        </div>
    </div>

<div class="container main-grid">
    <div class="filter-panel">
        <h2>Filter Vaccination Data</h2>
        <form method="GET" action="/page2">
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
</html>"""

    return page_html