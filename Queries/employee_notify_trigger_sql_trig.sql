DROP TRIGGER IF EXISTS employee_notify_trigger
ON employees;
 
CREATE TRIGGER employee_notify_trigger
AFTER INSERT OR UPDATE
ON employees
FOR EACH ROW
EXECUTE FUNCTION notify_employee_change();