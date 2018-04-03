--DRILL DOWN (on Postgre 9.5 + )

SELECT d.type,SUM(f.fatalities) FROM disaster AS d, fact_table AS f
WHERE f.disaster_id=d.id
GROUP BY GROUPING SETS ((type),());

--- drill down from type to (type,country)
SELECT l.country, d.type, SUM(f.fatalities)
FROM fact_table AS f, disaster AS d, location AS l
WHERE f.location_id=l.id AND f.disaster_id=d.id AND l.country!=''
GROUP BY GROUPING SETS ((l.country,d.type),d.type,());

--- drill down from (type,country) to (type,province)
SELECT l.province,d.type,sum(f.fatalities) 
FROM fact_table AS f, disaster AS d, location AS l 
WHERE f.location_id=l.id AND f.disaster_id=d.id AND l.province!='' 
GROUP BY GROUPING SETS ((l.province,d.type),d.type,());

--ROLL UP
---same queries in inverse order

--SLICE
---fatalities per group of disaster
SELECT disaster.group_,SUM(f.fatalities) from fact_table as f, disaster
WHERE  f.disaster_id = disaster.id
GROUP BY disaster.group_
ORDER BY disaster.group_;

---fatalities in Ontario in 1999
SELECT SUM(f.fatalities) FROM fact_table as f, date, location
WHERE f.start_date_id=date.id AND f.location_id=location.id AND date.year='1999' AND location.province='Ontario';

---fatalities due to natural disaster in Ontario in 1999
SELECT SUM(f.fatalities) FROM fact_table as f, date, location, disaster
WHERE f.start_date_id=date.id AND f.location_id=location.id 
AND f.disaster_id = disaster.id AND date.year='1999' AND location.province='Ontario' AND disaster.subgroup = 'Natural';

---fatalities per month
SELECT date.month, SUM(f.fatalities)
FROM fact_table as f, date
WHERE  f.start_date_id = date.id
GROUP BY date.month
ORDER BY date.month;

---DICE (subcube of aggregated data)
SELECT SUM(f.fatalities), disaster.category, location.province 
FROM fact_table as f, location, disaster
WHERE (location.province = 'Newfoundland and Labrador' OR location.province = 'British Columbia') 
AND f.location_id = location.id AND f.disaster_id = disaster.id AND (disaster.category = 'Air' OR disaster.category = 'Residential')
GROUP BY disaster.category, location.province
ORDER BY location.province;

--TOP N (or bottom n)
--- the 5 cities in Canada with the most riots
SELECT location.city FROM fact_table as f,location, disaster
WHERE f.location_id=location.id AND f.disaster_id = disaster.id
AND location.country='Canada' AND disaster.category = 'Rioting'
GROUP BY location.city
ORDER BY COUNT(*) DESC
LIMIT 5;

--- the province with the most space debris.
SELECT location.province,count(*) FROM fact_table as f,location, disaster
WHERE f.location_id=location.id AND f.disaster_id = disaster.id
AND disaster.category = 'Space Debris'
GROUP BY location.province
ORDER BY COUNT(*) DESC;

---the province with the most storms and severe thunderstorms.
SELECT location.province,count(*) FROM fact_table as f,location, disaster
WHERE f.location_id=location.id AND f.disaster_id = disaster.id
AND disaster.category = 'Storms and Severe Thunderstorms'
GROUP BY location.province
ORDER BY COUNT(*) DESC;


-- CONTRAST
---contrast the number of fatalities in Ontario due to wildfires, during 1997, with the number of fatalities in Ontario due to flooding, during 1997.

SELECT SUM(f.fatalities), d.category, l.province, da.year 
FROM fact_table as f, location as l, disaster as d, date AS da
WHERE l.province = 'Ontario' AND da.year = '1997' 
AND (d.category = 'Flood' OR d.category = 'Wildfire') 
AND f.location_id = l.id AND f.disaster_id = d.id AND f.start_date_id = da.id
GROUP BY d.category, l.province, da.year
ORDER BY l.province;

---contrast the number of fatalities in Ontario due to wildfires, during 1992, with the number of fatalities in Quebec due to flooding, during 1992.

SELECT d.category, l.province,SUM(f.fatalities),da.year
FROM fact_table as f, location as l, disaster as d, date AS da
WHERE ((l.province = 'Ontario' AND d.category = 'Cold Event' ) OR (l.province = 'Quebec' AND d.category = 'Flood')) AND da.year = '1992' AND f.location_id = l.id AND f.disaster_id = d.id AND f.start_date_id = da.id
GROUP BY d.category, l.province, da.year
ORDER BY l.province;
