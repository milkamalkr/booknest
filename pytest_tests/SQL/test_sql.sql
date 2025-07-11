select * from rental_history;

select * from rent_requests where status = 'pending';
select * from users where id = '4ab50e04-9cf0-405f-9ea2-335fa829277d';

select * from users where email = 'renter3@booknest.com';

select * from books where id = '9ffb897f-9005-4181-879e-e2c96071b5af';

select * from waitlists;


DELETE FROM waitlists;
UPDATE rent_requests SET status = 'returned';
UPDATE rental_history SET status = 'returned';

ALTER TABLE waitlists
DROP COLUMN position;


INSERT INTO waitlists (user_id, book_id, created_at) 
VALUES ('c499a4cd-77ab-428b-915b-0ea100568b07', 'e8174697-ebb7-471b-9823-bd5d1b8005cd', NOW())

SELECT 1 FROM waitlists WHERE book_id = 'e8174697-ebb7-471b-9823-bd5d1b8005cd' AND user_id = 'c499a4cd-77ab-428b-915b-0ea100568b07'

SELECT
    rh.rent_start,
    rh.rent_end,
    rh.status AS rental_status,
    rh.renter_id,
    rr.*
FROM
    rental_history rh
JOIN
    rent_requests rr
    ON rh.book_id = rr.book_id AND rh.renter_id = rr.renter_id
WHERE
    rh.book_id = 'db27d0ed-69c9-4df1-abe0-27623a2827e7'
ORDER BY
    rh.rent_start DESC;

SELECT conname
FROM pg_constraint
WHERE conrelid = 'rent_requests'::regclass
  AND contype = 'c';  -- c = check

ALTER TABLE rent_requests
DROP CONSTRAINT rent_requests_status_check;

ALTER TABLE rent_requests
ADD CONSTRAINT rent_requests_status_check
CHECK (status IN ('pending', 'accepted', 'declined', 'returned'));
