import oracledb

conn = oracledb.connect(
    user="system",
    password="12345@!@#$%",
    dsn="localhost:1521/XE"
)

print("Connected to Oracle:", conn.version)
conn.close()
