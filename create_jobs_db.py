import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('jobs.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table named 'users'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        job_title TEXT NOT NULL,
        job_description TEXT NOT NULL,
        time_since_posted TEXT NOT NULL,
        job_link TEXT NOT NULL
    )
''')

jobs = [
    ('Software Engineer', 'Develop software applications', '2 days ago', 'http://example.com/job1'),
    ('Data Scientist', 'Analyze data and build models', '1 week ago', 'http://example.com/job2'),
    ('Product Manager', 'Oversee product development', '3 hours ago', 'http://example.com/job3')
]

cursor.executemany('''
    INSERT INTO jobs (job_title, job_description, time_since_posted, job_link)
    VALUES (?, ?, ?, ?)
''', jobs)

conn.commit()





# Query and display all data from the 'users' table
cursor.execute("SELECT * FROM jobs")
rows = cursor.fetchall()

print("jobs in the database:")
for row in rows:
    print(row)

# Delete all rows from the 'jobs' table
cursor.execute('DELETE FROM jobs')

# Reset the auto-incrementing primary key
cursor.execute('DELETE FROM sqlite_sequence WHERE name="jobs"')

# Commit the changes
conn.commit()


# Close the connection to the database
conn.close()
