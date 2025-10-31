import sqlite3

conn = sqlite3.connect("immunisation.db")
cursor = conn.cursor()

# create Team table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Team (
    StudentID TEXT PRIMARY KEY,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    FullName TEXT GENERATED ALWAYS AS (FirstName || ' ' || LastName) VIRTUAL
);

""")

# create Persona table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Persona (
    PersonaID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Role TEXT,
    Background TEXT,
    Age INTEGER,
    Location TEXT,
    Occupation TEXT,
    Education TEXT,
    TechnologyUse TEXT,
    Context TEXT,
    Needs TEXT,
    Goals TEXT,
    Skills TEXT,
    PainPoints TEXT,
    ImagePath TEXT
);
""")
cursor.execute("""
INSERT INTO Team (StudentID, FirstName, LastName)
VALUES ('S4204234', 'Prantik', 'Saha');
""")
cursor.execute("""
INSERT INTO Team (StudentID, FirstName, LastName)
VALUES ('S4199771', 'Tasnim', 'Hasan');
""")

cursor.execute("""
INSERT INTO Team (StudentID, FirstName, LastName)
VALUES ('S4199771', 'Tasnim', 'Hasan');
""")

personas = [
    ("Dr. Amina Rahman", "Healthcare Professional", "Public Health Specialist", 36, "Dhaka", "Doctor", "MBBS, MPH", "Mobile & hospital apps", "Vaccination tracking", "Reliable data", "Better rates", "Analysis", "System inconsistency", "images/persona1.jpg"),
    ("Arif Hossain", "Data Analyst", "Government Data Division", 29, "Chittagong", "Analyst", "BSc Statistics", "Excel & SQL", "Data cleaning", "Accessible reports", "Faster dashboards", "Visualization", "Fragmented sources", "images/persona2.jpg"),
    ("Sara Ahmed", "Parent", "Urban resident", 34, "Dhaka", "Homemaker", "High School", "Mobile usage", "Child vaccination", "Reminders & info", "Healthy family", "Basic tech", "Lack of awareness", "images/persona3.jpg")
]

conn.commit()
conn.close()


