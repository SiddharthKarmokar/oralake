import oracledb

# --- CONFIG ---
DB_USER = "system"
DB_PASS = "Password123"
DB_DSN  = "localhost:1521/FREEPDB1"   # change if yours differs (e.g., ORCLPDB1)

# --- CONNECT ---
try:
    conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
    cur = conn.cursor()
    print("✅ Connected to Oracle database")
except Exception as e:
    raise SystemExit(f"❌ Connection failed: {e}")

# --- STEP 1: INSERT A NEW OBJECT ---
print("\n➡️  Inserting new object...")
object_id = cur.var(int)
cur.callproc("ORA_LAKE_OPS.add_object", [
    "test_object.json",        # name
    "JSON",                    # type
    b'{"version": 1}',         # content (BLOB)
    "demo",                    # tags
    "Initial insert test",     # description
    object_id                  # OUT parameter
])
object_id = object_id.getvalue()
print(f"✅ Object created with ID [{object_id}]")

# --- STEP 2: CREATE NEW VERSIONS ---
for i in range(2, 4):
    print(f"➡️  Creating version {i}...")
    content = f'{{"version": {i}}}'.encode()
    blob_var = cur.var(oracledb.DB_TYPE_BLOB)
    blob_var.setvalue(0, content)
    cur.callproc("ORA_LAKE_VERSION_OPS.create_new_version", [object_id, blob_var])

# --- STEP 3: ROLLBACK TO VERSION 2 ---
print("\n➡️  Rolling back to version 2...")
cur.callproc("ORA_LAKE_VERSION_OPS.rollback_version", [object_id, 2])

# --- STEP 4: VERIFY FINAL CONTENT ---
print("\n➡️  Fetching rolled-back object content...")
cur.execute("SELECT content FROM ORA_LAKE_OBJECTS WHERE id = :id", {"id": object_id})
row = cur.fetchone()
if row:
    blob = row[0]
    data = blob.read().decode()
    print(f"✅ Final content after rollback: {data}")
else:
    print("⚠️ Object not found after rollback")

# --- CLEANUP ---
conn.commit()
cur.close()
conn.close()
print("\n🏁 Test completed successfully.")
