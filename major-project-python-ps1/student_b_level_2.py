import pyhtml
from datetime import date

def get_page_html(form_data):
    print("Rendering Infection Data Filter page...")

    today = date.today().strftime("%d %B %Y")

    # === Get user inputs ===
    economic_phase = form_data.get("economic_phase", [""])[0]
    inf_type = form_data.get("inf_type", [""])[0]
    year = form_data.get("year", [""])[0]
    summary_mode = form_data.get("summary", ["0"])[0]

    # === Build WHERE filters ===
    filters = []
    if economic_phase:
      filters.append(f"TRIM(LOWER(e.phase)) = TRIM(LOWER('{economic_phase}'))")


    if inf_type:
        filters.append(f"it.description LIKE '%{inf_type}%'")
    if year:
        filters.append(f"i.year = {year}")
    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    # === Summarize or detailed mode ===
    if summary_mode == "1":
        query = f"""
        SELECT 
            it.description AS "Preventable Disease",
            e.phase AS "Economic Phase",
            i.year AS "Year",
            ROUND(SUM(i.cases), 2) AS "Cases per 100k"
        FROM InfectionData i
        JOIN Infection_Type it ON i.inf_type = it.id
        JOIN Country c ON i.country = c.CountryID
        JOIN Economy e ON c.economy = e.economyID
        {where_clause}
        GROUP BY it.description, e.phase, i.year
        ORDER BY e.phase, i.year;
        """
    else:
        query = f"""
        SELECT 
            it.description AS "Preventable Disease",
            c.name AS "Country",
            e.phase AS "Economic Phase",
            i.year AS "Year",
            i.cases AS "Cases per 100k"
        FROM InfectionData i
        JOIN Infection_Type it ON i.inf_type = it.id
        JOIN Country c ON i.country = c.CountryID
        JOIN Economy e ON c.economy = e.economyID
        {where_clause}
        ORDER BY e.phase, c.name;
        """

    # === Run the query ===
    try:
        results = pyhtml.get_results_from_query("immunisation.db", query)
        print("Results found:", len(results))
    except Exception as e:
        print("Database error:", e)
        results = []

    # === Table setup ===
    if summary_mode == "1":
        headers = ["Preventable Disease", "Economic Phase", "Year", "Cases per 100k"]
    else:
        headers = ["Preventable Disease", "Country", "Economic Phase", "Year", "Cases per 100k"]

    rows_html = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in results
    ) or "<tr><td colspan='5'>No data found</td></tr>"

    table_html = f"""
    <table class='data-table'>
        <thead><tr>{''.join(f'<th>{h}</th>' for h in headers)}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """

    # === HTML layout ===
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Infection Data | Immunisation</title>
<link rel="stylesheet" href="/static/css/2b.css">
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
        <a class="active" href="/page4">Infection</a>
        <a href="/page3">Progress</a>
        <a href="/page6">Analysis</a>
    </div>
    <div class="search-container">
            <input type="text" placeholder="Search...">
      </div>
</div>

<form method="get" action="/page4" class="filter-form">
  <h3>Filter Infection Data</h3>
  <div class="filter-line">
    <label>Economic Status:</label>
    <select name="economic_phase">
      <option value="">--All--</option>
      <option value="High Income" {'selected' if economic_phase=='High Income' else ''}>Developed</option>
      <option value="Upper Middle Income" {'selected' if economic_phase in ('Upper Middle Income', 'Lower Middle Income') else ''
}>Developing</option>
      <option value="Low Income" {'selected' if economic_phase=='Low Income' else ''}>Underdeveloped</option>
    </select>

    <label>Infection Type:</label>
    <input type="text" name="inf_type" value="{inf_type}" placeholder="e.g. Measles">

    <label>Year:</label>
    <select name="year">
      <option value="">--All--</option>
      {''.join(f"<option {'selected' if str(y)==year else ''}>{y}</option>" for y in range(2010,2026))}
    </select>
  </div>

  <div class="filter-buttons">
    <button type="submit" class="apply">Apply Filter</button>
    <a href="/page4" class="reset">Reset</a>
    <button type="submit" name="summary" value="1" class="summary">Summarize Data</button>
  </div>
</form>

<div class="data-section">
  {table_html}
</div>

<footer>
  <p>Help | Contacts | Sources</p>
  <p>Last Updated: {today}</p>
</footer>
</body>
</html>
"""