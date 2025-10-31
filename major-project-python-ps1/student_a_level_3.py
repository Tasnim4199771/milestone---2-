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
    print("Rendering Global Infection Rate page...")

    today = date.today().strftime("%d %B %Y")

    # === Load infection type dropdown ===
    # This query is safe as it has no user input
    infection_types = fetch_data(
        "SELECT DISTINCT description FROM Infection_Type ORDER BY description;"
    )

    # === Extract filters ===
    inf_type = form_data.get("inf_type", [""])[0]
    year = form_data.get("year", [""])[0]

    results = []
    global_rate = None
    data_list_html = ""

    # Build dropdown options
    inf_type_options = "".join(
        f"<option value=\"{desc[0]}\" {'selected' if desc[0]==inf_type else ''}>{desc[0]}</option>"
        for desc in infection_types
    )

    # === Run only if both selected ===
    if inf_type and year and year.isdigit():
        try:
            # --- 1. Get infection_type ID ---
            # SECURE: Use ? placeholder for the value
            inf_type_id_result = fetch_data(
                "SELECT id FROM Infection_Type WHERE description = ?",
                (inf_type,)
            )
            inf_type_id = inf_type_id_result[0][0] if inf_type_id_result else None

            # --- 2. Get global infection rate (Total Cases / Total Population) ---
            global_query = """
                SELECT ROUND((SUM(i.cases)*1.0 / SUM(cp.population))*100000, 2)
                FROM InfectionData i
                JOIN CountryPopulation cp 
                    ON i.country = cp.country AND i.year = cp.year
                JOIN Infection_Type it 
                    ON i.inf_type = it.id
                WHERE it.description = ? AND i.year = ?;
                """
            # SECURE: Pass params as a tuple
            global_rate_result = fetch_data(global_query, (inf_type, int(year)))
            global_rate = global_rate_result[0][0] if global_rate_result and global_rate_result[0][0] is not None else None
            
            if global_rate is not None and inf_type_id is not None:
                # --- 3. Get country-specific data exceeding the global rate ---
                
                # NOTE on SQL injection: Since global_rate is derived from the database, it is numeric
                # and low-risk, but for absolute security, it should also be parameterized.
                # However, SQLite does not allow a column alias (like 'rate') to be referenced in the WHERE clause,
                # so the calculation must be repeated for the WHERE condition.
                results_query = f"""
                    SELECT 
                        c.name,
                        r.name,
                        id.cases,
                        cp.population,
                        ROUND((id.cases * 1.0 / cp.population)*100000, 2) AS rate
                    FROM InfectionData id
                    JOIN Country c ON id.country = c.CountryID
                    JOIN Region r ON c.region = r.RegionID
                    JOIN CountryPopulation cp ON id.country = cp.country AND id.year = cp.year
                    WHERE id.inf_type = ? 
                      AND id.year = ? 
                      AND ROUND((id.cases * 1.0 / cp.population)*100000, 2) > ?
                    ORDER BY rate DESC;
                    """
                
                # SECURE: Pass inf_type_id, year, and global_rate as parameters
                params = (inf_type_id, int(year), global_rate)
                results = fetch_data(results_query, params)

        except Exception as e:
            print("Database error during main query:", e)
            results = []

    # === Generate HTML Data Rows (CSS Grid format) ===
    if global_rate is not None:
        header_text = f"Countries Exceeding Global Rate ({global_rate:,.2f} per 100,000)"
    else:
        header_text = "Countries Exceeding Global Rate"
        
    data_list_html = f"""
        <div class="data-list-container">
            <div class="data-entry header">
                <div class="data-field country">Country</div>
                <div class="data-field region">Region</div>
                <div class="data-field cases">Cases</div>
                <div class="data-field population">Population</div>
                <div class="data-field percentage">Infection Rate (%)</div>
            </div>
            """
    if results:
        # Format numbers and generate rows
        for row in results:
            country, region, cases, population, rate = row
            data_list_html += f"""
            <div class="data-entry">
                <div class="data-field country">{country}</div>
                <div class="data-field region">{region}</div>
                <div class="data-field cases">{cases:,.0f}</div>
                <div class="data-field population">{population:,.0f}</div>
                <div class="data-field percentage">{rate:,.2f}%</div>
            </div>
            """
    else:
        data_list_html += f"<div class='data-field' style='grid-column: 1 / -1; text-align: center; padding: 15px;'>No data found or global rate not calculated for {inf_type} in {year}.</div>"

    data_list_html += "</div>" # Close data-list-container

    # === Final HTML Layout ===
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Analysis | Global Infection Rate</title>
<link rel="stylesheet" href="/static/css/3a.css">
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
        <a href="/page2">Vaccination</a>
        <a href="/page4">Infection</a>
        <a href="/page3">Progress</a>
        <a class="active" href="/page6">Analysis</a>
    </div>
    <div class="search-container">
        <input type="text" placeholder="Search...">
    </div>
</div>

<div class="main-container">
    <div class="filter-panel">
        <form method="get" action="/page6" class="filter-form">
            <h2>Global Infection Rate</h2>
            <div class="filter-line">
                <label>Infection Type:</label>
                <select name="inf_type">
                    <option value="">--Select Infection--</option>
                    {inf_type_options}
                </select>

                <label>Year:</label>
                <select name="year">
                    <option value="">--Select Year--</option>
                    {''.join(f"<option value='{y}' {'selected' if str(y)==year else ''}>{y}</option>" for y in range(2000,2026)) }
                </select>
            </div>

            <div class="apply-reset">
                <button type="submit" class="apply">Apply Filter</button>
                <a href="/page6" class="reset">Reset</a>
            </div>
        </form>
    </div>

    <div class="data-panel">
        <h3>{header_text}</h3>
        {data_list_html}
    </div>
</div>

<footer>
    <p>Help | Contacts | Sources</p>
    <p>Last Updated: {today}</p>
</footer>
</body>
</html>
"""