CREATE OR REPLACE PACKAGE ora_lake_ops AS
  PROCEDURE add_object(
    p_name VARCHAR2,
    p_type VARCHAR2,
    p_content BLOB,
    p_tags CLOB,
    p_description CLOB,
    p_schema_hint CLOB
  );
  FUNCTION get_object(p_id NUMBER) RETURN BLOB;
  PROCEDURE tag_object(
    p_id NUMBER,
    p_tag VARCHAR2,
    p_description CLOB DEFAULT NULL,
    p_schema_hint CLOB DEFAULT NULL
  );
  FUNCTION query_objects_by_tag(p_tag VARCHAR2) RETURN SYS_REFCURSOR;
END ora_lake_ops;
/
