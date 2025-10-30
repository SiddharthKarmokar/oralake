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
    INSERT INTO ora_lake_objects(object_name, object_type, content, created_at, updated_at, version_num)
    VALUES(p_name, p_type, p_content, SYSTIMESTAMP, SYSTIMESTAMP, 1)
    RETURNING object_id INTO l_id;

    INSERT INTO ora_lake_versions(object_id, version_num, content, created_at)
    VALUES(l_id, 1, p_content, SYSTIMESTAMP);

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
      SELECT o.object_id, o.object_name, o.version_num, o.created_at, o.updated_at
      FROM ora_lake_objects o
      JOIN ora_lake_metadata m ON o.object_id = m.object_id
      WHERE m.tag = p_tag;
    RETURN l_cursor;
  END query_objects_by_tag;


  PROCEDURE increment_version(p_id NUMBER) IS
  BEGIN
    UPDATE ora_lake_objects
    SET version_num = version_num + 1,
        updated_at = SYSTIMESTAMP
    WHERE object_id = p_id;
    COMMIT;
  END increment_version;


  PROCEDURE update_object(
      p_name        IN VARCHAR2,
      p_obj_type    IN VARCHAR2,
      p_content     IN BLOB,
      p_tags        IN VARCHAR2,
      p_description IN VARCHAR2
  ) IS
      v_object_id NUMBER;
      v_new_ver   NUMBER;
  BEGIN
      -- Find object_id for given name + type (get the most recent one)
      SELECT object_id INTO v_object_id
      FROM (
          SELECT object_id 
          FROM ora_lake_objects
          WHERE object_name = p_name AND object_type = p_obj_type
          ORDER BY created_at DESC
      )
      WHERE ROWNUM = 1;

      -- Compute next version number
      SELECT NVL(MAX(version_num), 0) + 1 INTO v_new_ver
      FROM ora_lake_versions
      WHERE object_id = v_object_id;

      -- Insert new version
      INSERT INTO ora_lake_versions(object_id, version_num, content, created_at)
      VALUES (v_object_id, v_new_ver, p_content, SYSTIMESTAMP);

      -- Update main object
      UPDATE ora_lake_objects
      SET content = p_content,
          version_num = v_new_ver,
          updated_at = SYSTIMESTAMP
      WHERE object_id = v_object_id;

      -- Optionally update metadata
      IF p_tags IS NOT NULL OR p_description IS NOT NULL THEN
          UPDATE ora_lake_metadata
          SET tag = p_tags,
              description = p_description
          WHERE object_id = v_object_id;
      END IF;

      COMMIT;
  END update_object;


  PROCEDURE rollback_object (
      p_name           IN VARCHAR2,
      p_obj_type       IN VARCHAR2,
      p_target_version IN NUMBER
  ) IS
      v_object_id     NUMBER;
      v_old_content   BLOB;
      v_old_tag       VARCHAR2(4000);
      v_description   VARCHAR2(4000);
      v_count         NUMBER;
  BEGIN
      -- Find object_id
      SELECT object_id
      INTO v_object_id
      FROM ora_lake_objects
      WHERE object_name = p_name
        AND object_type = p_obj_type
      FETCH FIRST 1 ROWS ONLY;

      -- Check if version exists in versions table
      SELECT COUNT(*) INTO v_count
      FROM ora_lake_versions
      WHERE object_id = v_object_id
        AND version_num = p_target_version;

      IF v_count = 0 AND p_target_version = 1 THEN
          -- Version 1 might only exist in main table (initial version)
          -- In this case, we need to handle it differently
          RAISE_APPLICATION_ERROR(-20001, 
              'Version ' || p_target_version || ' not found in version history. ' ||
              'Initial version may not have been saved.');
      END IF;

      -- Fetch old version's content and metadata
      SELECT v.content, m.tag, m.description
      INTO v_old_content, v_old_tag, v_description
      FROM ora_lake_versions v
      LEFT JOIN ora_lake_metadata m ON v.object_id = m.object_id
      WHERE v.object_id = v_object_id
        AND v.version_num = p_target_version
      FETCH FIRST 1 ROWS ONLY;

      -- Update main object table
      UPDATE ora_lake_objects
      SET content = v_old_content,
          updated_at = SYSTIMESTAMP,
          version_num = p_target_version
      WHERE object_id = v_object_id;

      -- Update metadata if available
      IF v_old_tag IS NOT NULL OR v_description IS NOT NULL THEN
          UPDATE ora_lake_metadata
          SET tag = v_old_tag,
              description = v_description
          WHERE object_id = v_object_id;
      END IF;

      COMMIT;

      DBMS_OUTPUT.PUT_LINE(
          'Rolled back object ' || p_name || ' (' || p_obj_type || ') to version ' || p_target_version
      );

  EXCEPTION
      WHEN NO_DATA_FOUND THEN
          DBMS_OUTPUT.PUT_LINE('No matching version found for rollback.');
          RAISE;
      WHEN OTHERS THEN
          DBMS_OUTPUT.PUT_LINE('Error during rollback: ' || SQLERRM);
          ROLLBACK;
          RAISE;
  END rollback_object;

END ora_lake_ops;
/
