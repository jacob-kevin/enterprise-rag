CREATE OR REPLACE FUNCTION notify_employee_change()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify(
        'employee_changes',
        NEW.employee_id::text
    );
 
    RETURN NEW;
END;
$$ LANGUAGE plpgsql