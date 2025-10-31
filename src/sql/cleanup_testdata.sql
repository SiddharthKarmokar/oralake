-- Cleanup Test Data Script
-- Run this if tests fail and leave orphaned data

SET SERVEROUTPUT ON;

DECLARE
    v_count NUMBER;
BEGIN
    -- Delete versions for test objects
    DELETE FROM ora_lake_versions 
    WHERE object_id IN (
        SELECT object_id FROM ora_lake_objects 
        WHERE object_name LIKE 'test_%'
           OR object_name LIKE 'thumbnail_%'
    );
    v_count := SQL%ROWCOUNT;
    DBMS_OUTPUT.PUT_LINE('Deleted ' || v_count || ' version records');
    
    -- Delete metadata for test objects
    DELETE FROM ora_lake_metadata 
    WHERE object_id IN (
        SELECT object_id FROM ora_lake_objects 
        WHERE object_name LIKE 'test_%'
           OR object_name LIKE 'thumbnail_%'
    );
    v_count := SQL%ROWCOUNT;
    DBMS_OUTPUT.PUT_LINE('Deleted ' || v_count || ' metadata records');
    
    -- Delete test objects
    DELETE FROM ora_lake_objects 
    WHERE object_name LIKE 'test_%'
       OR object_name LIKE 'thumbnail_%';
    v_count := SQL%ROWCOUNT;
    DBMS_OUTPUT.PUT_LINE('Deleted ' || v_count || ' object records');
    
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Cleanup complete!');
    
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('Error during cleanup: ' || SQLERRM);
        RAISE;
END;
/

-- Verify cleanup
SELECT 'Remaining test objects: ' || COUNT(*) as status
FROM ora_lake_objects
WHERE object_name LIKE 'test_%'
   OR object_name LIKE 'thumbnail_%';