
--  Project Application: Spotify
--  Code description: This code has query related to implementation od Indexes, temporary tables, triggers, stored procedure and function on tables within spotify_db


--  use database
use spotify_db;

--  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -INDEX--  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -
--  1.When an artist wants to see details about one of their songs, we need to join ARTIST to SONG_ARTIST and then to the SONG table via song_id. 
--  An index on just the song_id in this linking table will drastically speed up the join, especially if the query starts by filtering on artist_id.
CREATE INDEX idx_sa_song_id ON song_artist (song_id);

--  2.Artists frequently want to know the distribution of thrie listener across countries. This requires filtering the large LISTENER table by country. 
--  Indexing country column makes it fast to segment and filter the listener base for tour planning, targeted ads etc.
CREATE INDEX idx_listener_country ON listener (country);

--  3.Artists constantly look at trends, "How did their streams perform this week compared to last week?" 
--  A composite index including interaction_type makes it extremely efficient to find all Play interactions that happened in  a duration.
CREATE INDEX idx_si_time_type ON song_interaction (interaction_timestamp, interaction_type);

--  4.composite index ON SONG_ARTIST (artist_id, song_id) helps drastically speed up queries to fetch all the songs by an artist.
CREATE INDEX idx_song_artist ON song_artist (artist_id, song_id);

--  5.Index on song_interaction (song_id, interaction_type, timestamp) will help artist to analyze  specific song interactions (Plays, Likes, Skip, share) over time faster.
CREATE INDEX idx_song_performance ON song_interaction (song_id, interaction_type, interaction_timestamp);

--  6.Index on ARTIST.genre improve performance for queries that filter or sort artists by their genre.
CREATE INDEX idx_artist_genre ON artist (genre);

--  7.Email is already unique, creating a unique index  allows for faster lookups when logging in or finding a user by email.
CREATE UNIQUE INDEX idx_listener_email ON listener (email);


--  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -Views--  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  

--  1. Artist View: Song Performance Summary
--  This view help artist to know how all their songs are doing, providing raw counts for plays, likes ,share and skips. 
--  They can use this to quickly identify their most and least popular tracks.

CREATE VIEW artist_song_performance AS
SELECT
    SA.artist_id,
    A.artist_first_name,
    A.artist_last_name,
    S.song_name,
    COUNT(CASE WHEN SI.interaction_type = 'play' THEN 1 END) AS total_plays,
    COUNT(CASE WHEN SI.interaction_type = 'like' THEN 1 END) AS total_likes,
    COUNT(CASE WHEN SI.interaction_type = 'share' THEN 1 END) AS total_share
FROM
    song S
JOIN song_artist SA ON S.song_id = SA.song_id
JOIN artist A on A.artist_id = SA.artist_id
LEFT JOIN song_interaction SI ON S.song_id = SI.song_id
GROUP BY
    SA.artist_id,   A.artist_first_name, A.artist_last_name, S.song_name;

--  --  -180 rows inserted

--  2. Artist View: Listener Demographics (Gender and Country)
--  This view helps the artist understand who is listening to their music. 
--  Knowing the top countries, genders, or age ranges is vital for tour planning and marketing

--  DROP VIEW Artist_Audience_Breakdown;
CREATE VIEW Artist_Audience_Breakdown AS
SELECT
    SA.artist_id,
    L.country,
    L.gender,
    COUNT(DISTINCT L.listener_id) AS UniqueListeners,
    COUNT(SI.interaction_id) AS TotalInteractions
FROM
    song_artist SA
JOIN song S ON SA.song_id = S.song_id
JOIN song_interaction SI ON S.song_id = SI.song_id
JOIN listener L ON SI.listener_id = L.listener_id
GROUP BY
    SA.artist_id, L.country, L.gender;

--  --  -189 rows inserted


--  3.  artist/ spotify analyst View: Loyal Listeners
--  This view defines and identifies the "Loyal Listener" of artists.
--   lOYAL Definition: someone who has interacted with the artist's music 10+ times and liked 5+ songs and follow them
--  This will help artists and spotify analysts to do targeted song recommendation.

--  DROP VIEW Artist_Loyal_Listeners;
CREATE VIEW Artist_Loyal_Listeners AS
SELECT
    SA.artist_id,
    L.listener_id,
    L.listener_first_name,
    L.listener_last_name,
    COUNT(SI.interaction_id) AS TotalInteractions,
    SUM(CASE WHEN SI.interaction_type = 'Like' THEN 1 ELSE 0 END) AS TotalLikes
FROM
    listener L
JOIN song_interaction SI ON L.listener_id = SI.listener_id
JOIN song S ON SI.song_id = S.song_id
JOIN song_artist SA ON S.song_id = SA.song_id
--   NEW: Inner Join to ensure the listener is following this specific artist
INNER JOIN follow_artist FA ON FA.listener_id = L.listener_id AND FA.artist_id = SA.artist_id
GROUP BY
    SA.artist_id, L.listener_id, L.listener_first_name, L.listener_last_name
HAVING
    COUNT(SI.interaction_id) >= 10  --   At least 10 interactions
    AND SUM(CASE WHEN SI.interaction_type = 'Like' THEN 1 ELSE 0 END) >= 5; --   At least 5 likes


--  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  -temproray tables--  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  

--  1. Top Loyal Listeners for a Specific Artist
--  This temporary table is created to materialize the highly aggregated and ranked results of calculating loyal listeners. 
--  This avoids repeating the costly aggregations and window function calls (COUNT and RANK) on the large raw interactions table for every subsequent analysis step, 
--  ensuring faster query performance in the session. Repeatedly running complex queries  those involving self-joins or window functions on large tables can tie up database resources 
--  and slow down the system for other users.

CREATE TEMPORARY TABLE Temp_Artist_Loyal_Listeners
AS
SELECT
    l.listener_id,
    l.listener_first_name AS first_name,
     l.listener_last_name AS last_name,
     SUM(CASE WHEN i.interaction_type != 'skip' THEN 1 ELSE 0 END) AS TotalInteractions,
    RANK() OVER (ORDER BY  SUM(CASE WHEN i.interaction_type != 'skip' THEN 1 ELSE 0 END) DESC) AS LoyaltyRank
FROM
    listener l
JOIN song_interaction i ON l.listener_id = i.listener_id
JOIN song_artist sa on sa.song_id = i.song_id
WHERE
    sa.artist_id = 1 --   Specific Artist ID (e.g., Artist ID 101)
GROUP BY
    l.listener_id, l.listener_first_name, l.listener_last_name
ORDER BY
    TotalInteractions DESC;


-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -Triggers-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -

-- 1. This before trigger validates new and updated interaction records, preventing the entry of any type other than the four allowed values: play, like, share, or skip.

DELIMITER //

CREATE TRIGGER trg_validate_interaction_type
BEFORE INSERT ON song_interaction
FOR EACH ROW
BEGIN
    IF NEW.interaction_type NOT IN ('play', 'like', 'share', 'skip') THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Invalid interaction_type. Must be one of: play, like, share, or skip.';
    END IF;
END //

CREATE TRIGGER trg_validate_interaction_type_update
BEFORE UPDATE ON song_interaction
FOR EACH ROW
BEGIN
    IF NEW.interaction_type NOT IN ('play', 'like', 'share', 'skip') THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Invalid interaction_type. Must be one of: play, like, share, or skip.';
    END IF;
END //

DELIMITER ;

-- -- check
-- INSERT INTO song_interaction (listener_id, song_id, interaction_type, interaction_timestamp)
-- VALUES (101, 501, 'playing song', NOW());
--  Expected Result: error.Invalid interaction_type. Must be one of: play, like, share, or skip.



-- 2. This BEFORE INSERT trigger checks if the email address being inserted into the listener table already exists. 
-- If a duplicate is found, the insertion is stopped and error message is returned:
DELIMITER //

CREATE TRIGGER trg_check_duplicate_email
BEFORE INSERT ON listener
FOR EACH ROW
BEGIN
    DECLARE email_count INT;

    --  Check if an account already exists with the NEW email address
    SELECT COUNT(*)
    INTO email_count
    FROM listener
    WHERE email = NEW.email;

    --  If the count is greater than 0, a duplicate email was found
    IF email_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Account already exist with this email id. Try logging in or use another email id to create the account.';
    END IF;
END;//

DELIMITER ;

-- check
INSERT INTO listener (listener_first_name, listener_last_name, date_of_birth, gender, email, country,  join_date, account_id)
VALUES ('Demo', 'Listener', '1997-05-11', 'female', 'demo.listener@example.com', 'India', '2021-01-01', 41);



-- 3 The trg_prevent_duplicate_like is a BEFORE INSERT trigger on the song_interaction table. 
-- It ensures that a listener cannot insert a second 'like' for the same song by querying for a pre-existing like 
-- and raising an error to block the transaction if a duplicate is found. This enforces a one-like-per-listener-per-song data integrity rule directly within the database.

DELIMITER //

CREATE TRIGGER trg_prevent_duplicate_like
BEFORE INSERT ON song_interaction
FOR EACH ROW
BEGIN
    DECLARE interaction_count INT;

    --  ONLY proceed with the check if the new interaction is a 'like'
    IF NEW.interaction_type = 'like' THEN
        
        --  Check if a 'like' record already exists for this listener and song
        SELECT COUNT(*)
        INTO interaction_count
        FROM song_interaction
        WHERE 
            listener_id = NEW.listener_id 
            AND song_id = NEW.song_id 
            AND interaction_type = 'like'; --  Crucial: only count existing 'likes'

        --  If an existing 'like' record is found
        IF interaction_count > 0 THEN
            --  Prevent the insertion and raise a custom error message
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'You have already liked this song';
        END IF;
    END IF; --  End of NEW.interaction_type = 'like' condition
END;//
DELIMITER ;

-- -check
INSERT INTO song_interaction (listener_id, song_id, interaction_type, interaction_timestamp)
VALUES (130, 3, 'like', NOW());
-- ERROR : You have already liked this song

-- 4. This BEFORE INSERT trigger checks if a listener is already following an artist by querying for a pre-existing follow record and raising an error to block the transaction if a duplicate is found.

DELIMITER //

CREATE TRIGGER trg_prevent_duplicate_follow
BEFORE INSERT ON follow_artist
FOR EACH ROW
BEGIN
    --  Check if a record with the same listener_id and artist_id already exists
    IF EXISTS (
        SELECT 1
        FROM follow_artist
        WHERE listener_id = NEW.listener_id
          AND artist_id = NEW.artist_id
    ) THEN
        --  Prevent the insertion and raise an error
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'You are already following this artist.';
    END IF;
END;//

DELIMITER ;

-- -check
-- INSERT INTO follow_artist (listener_id, artist_id, follow_date)
-- VALUES (130, 3, NOW());
-- ERROR : You are already following this artist.


-- 5. This BEFORE INSERT trigger checks if an artist with the same first and last name already exists by querying for a pre-existing artist record and raising an error to block the transaction if a duplicate is found.
DELIMITER //

CREATE TRIGGER prevent_duplicate_artist
BEFORE INSERT ON artist
FOR EACH ROW
BEGIN
    -- Declare a variable to store the count of existing duplicates
    DECLARE artist_count INT;

    -- Check if an artist with the same first name AND last name already exists
    SELECT COUNT(*)
    INTO artist_count
    FROM artist
    WHERE artist_first_name = NEW.artist_first_name
      AND artist_last_name = NEW.artist_last_name;

    -- If the count is greater than 0, a duplicate exists
    IF artist_count > 0 THEN
        -- Signal an error (SQLSTATE '45000' is a generic user-defined exception)
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Cannot add duplicate singer. An artist with this first and last name already exists.';
    END IF;
END; //

DELIMITER ;


-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- STORED PROCEDURE-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -

-- 1. This stored procedure, usp_RegisterNewListener, registers a new listener by first creating a 'Free' account  in the LISTENER_ACCOUNT_TYPE table. 
-- It then uses the ID from this new account to correctly insert the listener's personal details into the LISTENER table. 
-- The procedure uses a transaction to ensure both steps succeed or fail together, maintaining data integrity and satisfying the account_id's mandatory foreign key constraint.

DELIMITER //

CREATE PROCEDURE Register_New_Listener (
    IN p_first_name VARCHAR(100),
    IN p_last_name VARCHAR(100),
    IN p_dob DATE,
    IN p_gender VARCHAR(50),
    IN p_email VARCHAR(150),
    IN p_country VARCHAR(100)
)
BEGIN
    DECLARE v_new_account_id INT;

    --  Start a transaction
    START TRANSACTION;

    --  1. Create the default 'Free' listener account type record
    INSERT INTO listener_account_type (account_type, start_date, auto_renew)
    VALUES ('Free', CURDATE(), FALSE);

    --  Get the ID of the newly created account
    SET v_new_account_id = LAST_INSERT_ID();

    --  2. Create the listener record, linking it to the new account ID
    INSERT INTO LISTENER (
        listener_first_name, 
        listener_last_name, 
        Date_of_birth, 
        gender, 
        email, 
        country, 
        join_date, 
        account_id
    )
    VALUES (
        p_first_name, 
        p_last_name, 
        p_dob, 
        p_gender, 
        p_email, 
        p_country, 
        CURDATE(), 
        v_new_account_id
    );

    COMMIT;
END;//

DELIMITER ;


-- 2. Procedure to automatically downgrade expired accounts that are not set to auto-renew
-- This stored procedure, usp_DowngradeExpiredAccounts, automates the process of downgrading paid subscriptions to a 'Free' account type in a MySQL database. 
-- It identifies accounts where the end_date has passed relative to a specified or current date, and the auto_renew flag is set to FALSE.


DELIMITER //

CREATE PROCEDURE usp_DowngradeExpiredAccounts(
    IN CurrentRunDate DATE --  Input parameter
)
BEGIN
    --  1. ALL VARIABLE DECLARATIONS MUST COME FIRST
    DECLARE EffectiveDate DATE;
    DECLARE RowsAffected INT;
    DECLARE ResultMessage VARCHAR(255);
    
    --  2. ALL HANDLER DECLARATIONS MUST COME NEXT (BEFORE ANY EXECUTABLE CODE)
    --  Define the handler for any SQL error
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        --  Rollback if an error occurred
        IF @in_transaction_flag THEN
            ROLLBACK;
        END IF;
        --  Re-signal the error
        RESIGNAL;
    END;

    --  3. EXECUTABLE CODE STARTS HERE
    
    --  Determine the date to use for checking expiry
    IF CurrentRunDate IS NULL THEN
        SET EffectiveDate = CURDATE(); --  Use current date if none is provided
    ELSE
        SET EffectiveDate = CurrentRunDate;
    END IF;

    --  Start Transaction
    SET @in_transaction_flag = TRUE;
    START TRANSACTION;

    --  1. Update the account_type to 'Free' for expired, non-renewing paid accounts
    UPDATE listener_account_type
    SET 
        account_type = 'Free',
        end_date = NULL,         --  Clear end_date for the new, indefinite Free plan
        auto_renew = FALSE       --  Ensure auto_renew is False for 'Free'
    WHERE 
        end_date < EffectiveDate     --  Subscription period has ended
        AND auto_renew = FALSE       --  The user did not select auto-renew
        AND account_type <> 'Free';  --  Only downgrade paid accounts

    --  Get the number of rows affected by the update
    SET RowsAffected = ROW_COUNT();

    --  Commit the transaction
    COMMIT;
    SET @in_transaction_flag = FALSE;

    --  2. Return a success message with the count
    SET ResultMessage = CONCAT(
        CAST(RowsAffected AS CHAR), 
        ' paid account(s) have been downgraded to Free (using ', 
        DATE_FORMAT(EffectiveDate, '%Y-%m-%d'), 
        ' as the current date).'
    );

    SELECT ResultMessage;

END //
DELIMITER ;


-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -Function-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -
-- 1.This MySQL function identifies an artist's most popular song based on listener engagement. 
-- It takes an artist's full name as input, calculates the total number of 'Like', 'Share', and 'Play' interactions for each of their songs, 
-- and returns the song name with the highest combined count.

DELIMITER //

CREATE FUNCTION GetTopSongByTotalInteractions (ArtistFullName VARCHAR(201))
RETURNS VARCHAR(200)
READS SQL DATA
BEGIN
    DECLARE TopSongName VARCHAR(200);
    DECLARE TargetArtistID INT;

    --  1. Find the ArtistID based on the full name
    SELECT 
        artist_id 
    INTO 
        TargetArtistID
    FROM 
        artist
    WHERE 
        CONCAT(artist_first_name, ' ', artist_last_name) = ArtistFullName
    LIMIT 1;

    --  Check if artist was found
    IF TargetArtistID IS NULL THEN
        RETURN 'Artist Not Found';
    END IF;

    --  2. Find the song with the highest total count of Like, Share, and Play interactions
    SELECT
        S.song_name
    INTO
        TopSongName
    FROM
        song S
    JOIN
        song_artist SA ON S.song_id = SA.song_id
    LEFT JOIN 
        song_interaction SI ON S.song_id = SI.song_id
    WHERE
        SA.artist_id = TargetArtistID
    GROUP BY
        S.song_id, S.song_name 
    ORDER BY
        --  Sum the counts of 'Like', 'Share', and 'Play' interactions
        SUM(CASE SI.interaction_type 
            WHEN 'Like' THEN 1
            WHEN 'Share' THEN 1
            WHEN 'Play' THEN 1
            ELSE 0 --  Skips and other interactions are counted as 0
        END) DESC,
        S.release_date DESC --  Secondary sort: use the most recently released song in case of a tie
    LIMIT 1;

    --  Return the result
    IF TopSongName IS NULL THEN
        RETURN 'No Interactions Found';
    ELSE
        RETURN TopSongName;
    END IF;
END ;//
DELIMITER ;

-- -check
SELECT GetTopSongByTotalInteractions('Arijit Singh');
