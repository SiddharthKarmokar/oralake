#!/bin/bash
set -e

echo "Oracle XE custom startup script running..."

# Wait until Oracle is ready
until pg_isready -h localhost -p 1521 >/dev/null 2>&1; do
  echo "Waiting for Oracle to be ready..."
  sleep 5
done

# Run SQL commands automatically (optional)
echo "Running initial SQL setup..."
sqlplus / as sysdba <<EOF
WHENEVER SQLERROR EXIT SQL.SQLCODE;
ALTER SESSION SET CONTAINER = XEPDB1;
-- Example setup:
-- CREATE USER oralake IDENTIFIED BY oralake;
-- GRANT CONNECT, RESOURCE TO oralake;
-- ALTER USER oralake QUOTA UNLIMITED ON USERS;
EXIT;
EOF

echo "Oracle startup complete."
