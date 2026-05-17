import psycopg2

conn = psycopg2.connect("postgresql://postgres:password@localhost:5432/orkstrai")
cur = conn.cursor()
cur.execute("SELECT id, status FROM projects WHERE id='b8a0d5c0-edf2-46fd-801a-ac94b5b9ed00'")
print("Project:", cur.fetchone())

cur.execute("SELECT count(*) FROM agent_logs WHERE project_id='b8a0d5c0-edf2-46fd-801a-ac94b5b9ed00'")
print("Logs count:", cur.fetchone())

cur.execute("SELECT status FROM agent_logs WHERE project_id='b8a0d5c0-edf2-46fd-801a-ac94b5b9ed00' ORDER BY started_at DESC LIMIT 5")
print("Recent log statuses:", cur.fetchall())

cur.execute("SELECT count(*) FROM generated_artifacts WHERE project_id='b8a0d5c0-edf2-46fd-801a-ac94b5b9ed00'")
print("Artifacts count:", cur.fetchone())

conn.close()
