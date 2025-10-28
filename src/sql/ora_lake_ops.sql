CREATE OR REPLACE PACKAGE BODY ora_lake_ops AS

  FUNCTION add_object(
    p_name         VARCHAR2,
    p_type         VARCHAR2,
    p_content      BLOB,
    p_tags         CLOB DEFAULT NULL,
    p_description  CLOB DEFAULT NULL,
    p_schema_hint  CLOB DEFAULT NULL
  ) RETURN NUMBER IS
    l_id NUMBER;
  BEGIN
    INSERT INTO ora_lake_objects(object_name, object_type, content)
    VALUES(p_name, p_type, p_content)
    RETURNING object_id INTO l_id;

    IF p_tags IS NOT NULL OR p_description IS NOT NULL OR p_schema_hint IS NOT NULL THEN
      INSERT INTO ora_lake_metadata(object_id, tag, description, schema_hint)
      VALUES(l_id, p_tags, p_description, p_schema_hint);
    END IF;

    COMMIT;
    RETURN l_id;
  END add_object;

  FUNCTION get_object(p_id NUMBER) RETURN BLOB IS
    l_content BLOB;
  BEGIN
    SELECT content INTO l_content
    FROM ora_lake_objects
    WHERE object_id = p_id;
    RETURN l_content;
  END get_object;

  PROCEDURE tag_object(
    p_id           NUMBER,
    p_tag          VARCHAR2,
    p_description  CLOB DEFAULT NULL,
    p_schema_hint  CLOB DEFAULT NULL
  ) IS
  BEGIN
    INSERT INTO ora_lake_metadata(object_id, tag, description, schema_hint)
    VALUES(p_id, p_tag, p_description, p_schema_hint);
    COMMIT;
  END tag_object;

  FUNCTION query_objects_by_tag(p_tag VARCHAR2) RETURN SYS_REFCURSOR IS
    l_cursor SYS_REFCURSOR;
  BEGIN
    OPEN l_cursor FOR
      SELECT o.object_id, o.object_name
      FROM ora_lake_objects o
      JOIN ora_lake_metadata m ON o.object_id = m.object_id
      WHERE m.tag = p_tag;
    RETURN l_cursor;
  END query_objects_by_tag;

END ora_lake_ops;
/
