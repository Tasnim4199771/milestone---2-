import pyhtml
from datetime import date

def get_page_html(form_data):
    print("Rendering Global Infection Rate page...")

    today = date.today().strftime("%d %B %Y")

    # === Load infection type dropdown ===
    try:
        infection_types = pyhtml.get_results_from_query(
            "immunisation.db",
            "SELECT DISTINCT description FROM Infection_Type ORDER BY description;"
        )
    except Exception as e:
        print("Dropdown load error:", e)
        infection_types = []

    # === Extract filters ===
    inf_type = form_data.get("inf_type", [""])[0]
    year = form_data.get("year", [""])[0]

    results = []
    global_rate = None

    # === Run only if both selected ===
    if inf_type and year:
        try:
            # --- Get global infection rate ---
            global_query = f"""
                SELECT ROUND((SUM(i.cases)*1.0 / SUM(cp.population))*100000, 2)
                FROM InfectionData i
                JOIN CountryPopulation cp 
                    ON i.country = cp.country AND i.year = cp.year
                JOIN Infection_Type it 
                    ON i.inf_type = it.id
                WHERE it.description = '{inf_type}' AND i.year = {year};
            """
            global_rate = pyhtml.get_results_from_query("immunisation.db", global_query)[0][0]

            # --- Get countries exceeding global rate ---
            query = f"""
                SELECT 
                    c.name AS Country,
                    it.description AS InfectionType,
                    ROUND((i.cases*1.0 / cp.population)*100000, 2) AS Rate,
                    i.year AS Year
                FROM InfectionData i
                JOIN Country c ON i.country = c.CountryID
                JOIN CountryPopulation cp 
                    ON i.country = cp.country AND i.year = cp.year
                JOIN Infection_Type it ON i.inf_type = it.id
                WHERE it.description = '{inf_type}' AND i.year = {year}
                GROUP BY c.name, i.year
                HAVING Rate > (
                    SELECT (SUM(i2.cases)*1.0 / SUM(cp2.population))*100000
                    FROM InfectionData i2
                    JOIN CountryPopulation cp2 
                        ON i2.country = cp2.country AND i2.year = cp2.year
                    JOIN Infection_Type it2 ON i2.inf_type = it2.id
                    WHERE it2.description = '{inf_type}' AND i2.year = {year}
                )
                ORDER BY Rate DESC;
            """
            results = pyhtml.get_results_from_query("immunisation.db", query)
        except Exception as e:
            print("Database query error:", e)
            results = []

    # === Build table HTML ===
    if not inf_type or not year:
        table_html = """
        <table class="data-table">
          <tr><td colspan="4" style="text-align:center;">Please select infection type and year to view results.</td></tr>
        </table>
        """
    else:
        headers = ["Country", "Infection Type", "Infection per 100,000 people", "Year"]
        global_row = f"<tr class='global-row'><td>Global</td><td>{inf_type}</td><td>{global_rate or 'N/A'}</td><td>{year}</td></tr>"
        data_rows = "".join(
            "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
            for row in results
        ) or "<tr><td colspan='4'>No countries exceed the global rate.</td></tr>"

        table_html = f"""
        <table class="data-table">
            <thead><tr>{''.join(f'<th>{h}</th>' for h in headers)}</tr></thead>
            <tbody>{global_row}{data_rows}</tbody>
        </table>
        """

    # === Infection dropdown HTML ===
    inf_type_options = "".join(
        f"<option {'selected' if inf_type==t[0] else ''}>{t[0]}</option>" for t in infection_types
    )

    # === Return full HTML ===
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Global Infection Rate | Immunisation Data</title>
<link rel="stylesheet" href="/static/css/3b.css">
<style>

</style>
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

<form method="get" action="" class="filter-form">
  <h3>Global Infection Rate</h3>
  <div class="filter-line">
    <label>Infection Type:</label>
    <select name="inf_type">
      <option value="">--Select Infection--</option>
      {inf_type_options}
    </select>

    <label>Year:</label>
    <select name="year">
      <option value="">--Select Year--</option>
      {''.join(f"<option {'selected' if str(y)==year else ''}>{y}</option>" for y in range(2010,2026))}
    </select>
  </div>

  <div class="filter-buttons">
    <button type="submit" class="apply">Apply Filter</button>
    <a href="" class="reset">Reset</a>
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
</html>"""
