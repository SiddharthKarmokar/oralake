FROM gvenzl/oracle-xe:21-slim

ENV ORACLE_PASSWORD=Password123
ENV ORACLE_PWD=Password123
ENV ORACLE_DATABASE=XEPDB1

COPY --chown=oracle:dbs src/sql/init/ /opt/oracle/scripts/sql/

RUN chmod 755 /opt/oracle/scripts/sql/*.sql


