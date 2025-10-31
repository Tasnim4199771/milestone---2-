import sqlite3
from datetime import date
import pyhtml # ADDED

# --- Database Connection Setup ---
DATABASE_FILE = 'immunisation.db'

# REMOVED: The custom fetch_data function is removed as it's replaced by pyhtml.get_results_from_query

def get_page_html(form_data):
    print("Rendering Global Infection Rate page...")

    today = date.today().strftime("%d %B %Y")

    # === Load infection type dropdown ===
    # Using pyhtml utility. This query is safe as it has no user input.
    try:
        infection_types_raw = pyhtml.get_results_from_query(
            DATABASE_FILE,
            "SELECT DISTINCT description FROM Infection_Type ORDER BY description;"
        )
        # Flatten the list of tuples into a simple list of descriptions
        infection_types = [desc[0] for desc in infection_types_raw]
    except sqlite3.Error as e:
        print(f"Database error fetching infection types: {e}")
        infection_types = []


    # === Extract filters ===
    # .get() returns a list, so [0] retrieves the value, default to ""
    inf_type = form_data.get("inf_type", [""])[0].strip()
    year = form_data.get("year", [""])[0].strip()

    results = []
    global_rate = None
    data_list_html = ""

    # Build dropdown options
    inf_type_options = "".join(
        f"<option value='{desc}' {'selected' if desc==inf_type else ''}>{desc}</option>"
        for desc in infection_types
    )

    # === Fetch Data based on filters ===
    if inf_type and year.isdigit():
        
        # Determine the Infection Type ID (inf_id) for the selected description
        try:
            # NOTE: String concatenation required for pyhtml.get_results_from_query.
            # Escaping single quotes to prevent breaking the SQL string for the inf_type
            safe_inf_type = inf_type.replace("'", "''")
            
            inf_id_raw = pyhtml.get_results_from_query(
                DATABASE_FILE,
                f"SELECT id FROM Infection_Type WHERE description = '{safe_inf_type}';"
            )
            
            # inf_id_raw is a list of tuples, e.g., [('MEAS',)]
            inf_id = inf_id_raw[0][0] if inf_id_raw else None
        
        except sqlite3.Error as e:
            print(f"Database error fetching infection ID: {e}")
            inf_id = None
        
        if inf_id:
            # --- 1. Fetch Country-specific Infection Data ---
            country_query = f"""
                SELECT
                    C.CountryName, R.RegionName, T.target_pop, I.cases,
                    (I.cases * 100.0 / T.target_pop) AS InfectionRate
                FROM InfectionData I
                JOIN Country C ON I.country = C.CountryID
                JOIN Region R ON C.RegionID = R.RegionID
                JOIN Target_Population T ON I.country = T.CountryID AND I.year = T.YearID
                WHERE I.inf_type = '{inf_id}' AND I.year = {year} AND I.cases IS NOT NULL
                ORDER BY InfectionRate DESC;
            """
            
            # --- 2. Fetch Global Infection Rate ---
            global_query = f"""
                SELECT
                    SUM(I.cases) * 100.0 / SUM(T.target_pop) AS GlobalRate
                FROM InfectionData I
                JOIN Target_Population T ON I.country = T.CountryID AND I.year = T.YearID
                WHERE I.inf_type = '{inf_id}' AND I.year = {year};
            """

            try:
                results = pyhtml.get_results_from_query(DATABASE_FILE, country_query)
                global_rate_raw = pyhtml.get_results_from_query(DATABASE_FILE, global_query)
                
                # Global rate is a list of tuples, e.g., [(rate,)]
                if global_rate_raw and global_rate_raw[0] and global_rate_raw[0][0] is not None:
                    global_rate = global_rate_raw[0][0]
                else:
                    global_rate = None

            except sqlite3.Error as e:
                print(f"Database error fetching data results: {e}")
                results = []
                global_rate = None

    # === Process results for HTML table ===
    if not inf_type or not year.isdigit():
        header_text = "Select an Infection Type and Year to view data."
        data_list_html = f"""
            <div class="data-entry no-results">
                Please use the filters on the left to select an infection and year.
            </div>
        """
    elif not results or global_rate is None:
        header_text = f"Infection Data for {inf_type} in {year}"
        data_list_html = f"""
            <div class="data-entry no-results">
                No infection data found for **{inf_type}** in **{year}**.
            </div>
        """
    else:
        # Global Rate Header
        global_rate_str = f"{global_rate:.4f}%" if global_rate is not None else "N/A"
        header_text = f"Infection Data for {inf_type} in {year} (Global Rate: {global_rate_str})"

        # Country Data Rows
        for country, region_name, target_pop, cases, infection_rate in results:
            
            # Formatting numeric values
            # Target Pop and Cases: Format as integer with thousand separators or "N/A"
            target_pop_str = f"{int(target_pop):,}" if target_pop is not None else "N/A"
            cases_str = f"{int(cases):,}" if cases is not None else "N/A"
            
            # Infection Rate: Format as percentage (e.g., 0.1234%) or "N/A"
            rate_str = f"{infection_rate:.4f}%" if infection_rate is not None else "N/A"
            
            # Optional: Add class for high infection rates
            rate_class = "percentage high" if infection_rate is not None and infection_rate > 0.5 else "percentage"
            
            data_list_html += f"""
                <div class="data-entry">
                    <div class="data-field country">{country}</div>
                    <div class="data-field region">{region_name}</div>
                    <div class="data-field population">{target_pop_str}</div>
                    <div class="data-field cases">{cases_str}</div>
                    <div class="data-field {rate_class}">{rate_str}</div>
                </div>
            """

    # === Final HTML Layout (Ensuring it links to 3a.css) ===
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Infection Data | Immunisation Portal</title>
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
            <a href="/page2">Vaccination</a>
            <a href="/page5">Mission</a>
            <a class="active" href="/page4">Infection</a>
            <a href="/page3">Progress</a>
            <a href="/page6">Analysis</a>
        </div>
        <div class="search-container">
            <input type="text" placeholder="Search...">
        </div>
    </div>

<div class="main-container">
    <div class="filter-panel">
        <form method="get" action="/page4" class="filter-form">
            <h2>Filter Infection Data</h2>
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
                <a href="/page4" class="reset">Reset</a>
            </div>
        </form>
        
        <div class="notes-box">
            <h4>Data Notes</h4>
            <p>Infection Rate is calculated as (Reported Cases / Target Population) * 100.</p>
            <p>Target Population data is sourced from the Target_Population table in the database.</p>
        </div>
    </div>

    <div class="data-panel">
        <h3>{header_text}</h3>
        
        <div class="data-list-container">
            <div class="data-entry header">
                <div class="data-field country">Country</div>
                <div class="data-field region">Region</div>
                <div class="data-field population">Target Population</div>
                <div class="data-field cases">Reported Cases</div>
                <div class="data-field percentage">Infection Rate (%)</div>
            </div>

            {data_list_html}
            
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