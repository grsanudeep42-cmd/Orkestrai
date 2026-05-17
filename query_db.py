import sqlite3

conn = sqlite3.connect('/home/anudeep/projects/orkstrai/backend/orkestrai.db')
c = conn.cursor()
c.execute("SELECT id, status FROM projects WHERE id='b8a0d5c0-edf2-46fd-801a-ac94b5b9ed00'")
print(c.fetchone())
conn.close()
