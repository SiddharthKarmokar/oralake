CREATE OR REPLACE PACKAGE ora_lake_ops AS
  FUNCTION add_object(
    p_name         VARCHAR2,
    p_type         VARCHAR2,
    p_content      BLOB,
    p_tags         CLOB DEFAULT NULL,
    p_description  CLOB DEFAULT NULL,
    p_schema_hint  CLOB DEFAULT NULL
  ) RETURN NUMBER;

  FUNCTION get_object(p_id NUMBER) RETURN BLOB;

  PROCEDURE tag_object(
    p_id           NUMBER,
    p_tag          VARCHAR2,
    p_description  CLOB DEFAULT NULL,
    p_schema_hint  CLOB DEFAULT NULL
  );

  FUNCTION query_objects_by_tag(p_tag VARCHAR2) RETURN SYS_REFCURSOR;

  PROCEDURE increment_version(p_id NUMBER);

  PROCEDURE update_object(
      p_name        IN VARCHAR2,
      p_obj_type    IN VARCHAR2,
      p_content     IN BLOB,
      p_tags        IN VARCHAR2,
      p_description IN VARCHAR2
  );

  PROCEDURE rollback_object(
      p_name           IN VARCHAR2,
      p_obj_type       IN VARCHAR2,
      p_target_version IN NUMBER
  );
END ora_lake_ops;
/
