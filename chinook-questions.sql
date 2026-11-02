-- Chinook query activity (week 3, Thursday). Write one query under each question.
-- How to run this file, what the tables are and what each question expects is in
-- README.md beside it. Test each query at the mysql> prompt first, then paste it here.
-- Hand-in: week-03/hackathon/chinook/chinook-questions.sql in your own learner repo.

USE Chinook;


-- ============================================================
-- Part A: one table (SELECT, WHERE, ORDER BY, LIMIT)
-- ============================================================

-- Q01. Every genre name, A to Z.
    SELECT Name FROM Chinook.Genre
    ORDER BY Name ASC;
    

-- Q02. The customers who live in Canada: first name, last name and city, sorted by city.
    SELECT FirstName, LastName, City FROM Chinook.`Customer`
    ORDER BY CITY;

-- Q03. The ten longest tracks that run over 10 minutes: name and length in minutes
--      (one decimal), longest first.
    SELECT Name, Milliseconds FROM Chinook.Track
    ORDER BY Milliseconds
    LIMIT 100;


-- Q04. Invoices from 2025 whose total is above 10: invoice id, date and total, highest total first.
    SELECT InvoiceId, InvoiceDate, Total FROM Chinook.Invoice
    WHERE total > 10;

-- Q05. Albums whose title contains the word Live, A to Z.
    SELECT Title FROM Chinook.Album
    WHERE title = 'Live'
    ORDER BY Title ASC;
    
    

-- Q06. Customers in the USA or Canada who gave a company name: the full name in one
--      column called customer, the company and the country, sorted by company.

    SELECT FirstName, LastName, Company, Country FROM Chinook.Customer
    ORDER BY Company;
-- ============================================================
-- Part B: aggregates (GROUP BY, HAVING)
-- ============================================================

-- Q07. One row about the whole Track table: how many tracks, and the shortest, longest
--      and average length in minutes (two decimals).
    SELECT
        COUNT(*) AS TotalTracks,
        ROUND(MIN(Milliseconds) / 60000, 2) AS Shortest,
        ROUND(MAX(Milliseconds) / 60000, 2) AS Longest,
        ROUND(AVG(Milliseconds) / 60000, 2) AS Average
    FROM Track;
-- Q08. How many customers live in each country, most customers first, then country A to Z.
    SELECT
        Country,
        COUNT(*) AS TotalCustomers
    FROM Customer
    GROUP BY Country
    ORDER BY TotalCustomers DESC, Country ASC;


-- Q09. Total billed per billing country (two decimals), only the countries billed more
--      than 100 in all, highest first.
    SELECT
        BillingCountry,
        ROUND(SUM(Total), 2) AS TotalBilled
    FROM Invoice
    GROUP BY BillingCountry
    HAVING SUM(Total) > 100
    ORDER BY TotalBilled DESC;

-- Q10. Albums with more than 25 tracks: the album id and its track count, most tracks first.
--      (Only the id for now. Q13 adds the title.)
    SELECT
        AlbumId,
        COUNT(*) AS TrackCount
    FROM Track
    GROUP BY AlbumId
    HAVING COUNT(*) > 25
    ORDER BY TrackCount DESC;


-- Q11. Per customer id: how many invoices and how much they spent in all (two decimals),
--      only the customers who spent more than 45, biggest spender first.
    SELECT
        CustomerId,
        COUNT(*) AS InvoiceCount,
        ROUND(SUM(Total), 2) AS TotalSpent
    FROM Invoice
    GROUP BY CustomerId
    HAVING SUM(Total) > 45
    ORDER BY TotalSpent DESC;

-- ============================================================
-- Part C: joins
-- ============================================================

-- Q12. Every album title with the name of its artist, sorted by artist then title.
    SELECT
        Album.Title AS AlbumTitle,
        Artist.Name AS ArtistName
    FROM Album
    JOIN Artist
        ON Album.ArtistId = Artist.ArtistId
    ORDER BY Artist.Name, Album.Title;

-- Q13. Q10 again, with the album title and the artist name instead of the id.
    SELECT
        Album.Title AS AlbumTitle,
        Artist.Name AS ArtistName,
        COUNT(Track.TrackId) AS TrackCount
    FROM Track
    JOIN Album
        ON Track.AlbumId = Album.AlbumId
    JOIN Artist
        ON Album.ArtistId = Artist.ArtistId
    GROUP BY Album.AlbumId, Album.Title, Artist.Name
    HAVING COUNT(Track.TrackId) > 25
    ORDER BY TrackCount DESC;

-- Q14. Every track by Iron Maiden: album title and track name, sorted by album then track.
    SELECT
        Album.Title AS AlbumTitle,
        Track.Name AS TrackName
    FROM Track
    JOIN Album
        ON Track.AlbumId = Album.AlbumId
    JOIN Artist
        ON Album.ArtistId = Artist.ArtistId
    WHERE Artist.Name = 'Iron Maiden'
    ORDER BY Album.Title, Track.Name;

-- Q15. Every Jazz track: track name, album title and media type name, sorted by album then track.
    SELECT
        Track.Name AS TrackName,
        Album.Title AS AlbumTitle,
        MediaType.Name AS MediaTypeName
    FROM Track
    JOIN Album
        ON Track.AlbumId = Album.AlbumId
    JOIN MediaType
        ON Track.MediaTypeId = MediaType.MediaTypeId
    JOIN Genre
        ON Track.GenreId = Genre.GenreId
    WHERE Genre.Name = 'Jazz'
    ORDER BY Album.Title, Track.Name;

-- Q16. Each customer with the employee who supports them: customer full name and rep full
--      name (one column each), sorted by rep then customer.
    SELECT
        CONCAT(Customer.FirstName, ' ', Customer.LastName) AS CustomerName,
        CONCAT(Employee.FirstName, ' ', Employee.LastName) AS RepName
    FROM Customer
    JOIN Employee
        ON Customer.SupportRepId = Employee.EmployeeId
    ORDER BY RepName, CustomerName;

-- Q17. Every employee and how many customers they support, including the employees who
--      support nobody (they show 0), most customers first, then last name.
    SELECT
        Employee.EmployeeId,
        CONCAT(Employee.FirstName, ' ', Employee.LastName) AS EmployeeName,
        COUNT(Customer.CustomerId) AS CustomerCount
    FROM Employee
    LEFT JOIN Customer
        ON Employee.EmployeeId = Customer.SupportRepId
    GROUP BY Employee.EmployeeId, Employee.FirstName, Employee.LastName
    ORDER BY CustomerCount DESC, Employee.LastName ASC;

-- Q18. The five genres that earned the most: genre name and revenue (the sum of unit price
--      times quantity over every invoice line, two decimals), highest first.
    SELECT
        Genre.Name AS GenreName,
        ROUND(SUM(InvoiceLine.UnitPrice * InvoiceLine.Quantity), 2) AS Revenue
    FROM Genre
    JOIN Track
        ON Genre.GenreId = Track.GenreId
    JOIN InvoiceLine
        ON Track.TrackId = InvoiceLine.TrackId
    GROUP BY Genre.GenreId, Genre.Name
    ORDER BY Revenue DESC
    LIMIT 5;

-- Q19. How many tracks have never been sold? One number, found with a LEFT JOIN
--      from Track to InvoiceLine and a test for NULL.
    SELECT
        COUNT(*) AS NeverSoldTracks
    FROM Track
    LEFT JOIN InvoiceLine
        ON Track.TrackId = InvoiceLine.TrackId
    WHERE InvoiceLine.InvoiceLineId IS NULL;

-- ============================================================
-- Part D: subqueries
-- ============================================================

-- Q20. Every track on the album called Let There Be Rock: name and length in milliseconds,
--      in track order (by TrackId). Use a subquery for the album id, not a join.
    SELECT
        Name,
        Milliseconds
    FROM Track
    WHERE AlbumId = (
        SELECT AlbumId
        FROM Album
        WHERE Title = 'Let There Be Rock'
    )
    ORDER BY TrackId;

-- Q21. Tracks that cost more than the average track price: name and unit price,
--      the first ten alphabetically.
    SELECT
        Name,
        UnitPrice
    FROM Track
    WHERE UnitPrice > (
        SELECT AVG(UnitPrice)
        FROM Track
    )
    ORDER BY Name ASC
    LIMIT 10;

-- Q22. Artists with no album at all, A to Z. Write it with NOT IN and a subquery.
    SELECT
        Name
    FROM Artist
    WHERE ArtistId NOT IN (
        SELECT ArtistId
        FROM Album
    )
    ORDER BY Name ASC;

-- Q22b. Same question, written as a LEFT JOIN. Same rows?
    SELECT
        Artist.Name
    FROM Artist
    LEFT JOIN Album
        ON Artist.ArtistId = Album.ArtistId
    WHERE Album.AlbumId IS NULL
    ORDER BY Artist.Name ASC;

-- Q23. The invoice with the highest total: invoice id, customer id, date and total.
    SELECT
        InvoiceId,
        CustomerId,
        InvoiceDate,
        Total
    FROM Invoice
    ORDER BY Total DESC
    LIMIT 1;

-- Q24. Customers who bought at least one Metal track: full name and country, sorted by
--      name. The list of customer ids comes from a subquery that joins Invoice,
--      InvoiceLine, Track and Genre.
    SELECT
        CONCAT(FirstName, ' ', LastName) AS CustomerName,
        Country
    FROM Customer
    WHERE CustomerId IN (
        SELECT Invoice.CustomerId
        FROM Invoice
        JOIN InvoiceLine
            ON Invoice.InvoiceId = InvoiceLine.InvoiceId
        JOIN Track
            ON InvoiceLine.TrackId = Track.TrackId
        JOIN Genre
            ON Track.GenreId = Genre.GenreId
        WHERE Genre.Name = 'Metal'
    )
    ORDER BY CustomerName ASC;

-- ============================================================
-- Stretch (for home, or if you finish early)
-- ============================================================

-- Q25. Each employee with the name of the person they report to. The general manager
--      reports to nobody and must still appear, with NULL. Hint: join Employee to
--      itself under two aliases.


-- Q26. Customers whose total spend is above the average customer's total spend: full name
--      and what they spent (two decimals), biggest first. The average of the per-customer
--      totals needs a subquery in FROM (the notes page calls it a derived table).