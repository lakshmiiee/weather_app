Weather Management & Alert System
Goal
Build a Weather Data Management Service using FastAPI and a relational database only.
The system should fetch weather data from an external provider, store it, and expose clean APIs for querying and alerts.

Functional Requirements
1. Weather Fetch & Storage
Endpoint

GET /weather?city={city_name}
Behavior

Fetch current weather for the given city from one external weather API
Normalize the response into your own schema
Store the weather snapshot in the database
Return the normalized response
Constraints

Do not fetch from the external API if a weather record for the city exists that is less than 10 minutes old
Use the database to determine freshness
Expected fields

city
temperature (°C)
humidity (%)
weather_condition
fetched_at (timestamp)
source
2. Data Freshness Logic (DB-Driven)
Rules

If the latest weather data for a city is newer than 10 minutes → return DB record
If older → fetch from external API, store a new snapshot
Multiple requests for the same city should not create inconsistent data
3. Historical Weather Data
Endpoint

GET /weather/history?city={city}&from={date}&to={date}
Behavior

Return stored weather snapshots for the city in the given date range
Sorted by time ascending
Support pagination
4. Weather Alert Subscriptions
Users should be able to subscribe to weather alerts.

Create alert

POST /alerts
Example conditions

temperature > 35
humidity < 40
weather_condition = "Rain"
Fields

city
condition_type
operator
threshold_value
active (boolean)
5. Alert Evaluation Engine
Behavior

Every time new weather data is stored:
Evaluate all active alerts for that city
Trigger alert if the condition is met
Prevent duplicate alerts for the same weather snapshot
Trigger behavior

Log alert trigger to DB (no email/SMS required)
Store:
alert_id
triggered_at
weather_snapshot_id
6. Alert History
Endpoint

GET /alerts/{id}/history
Behavior

Return all trigger events for the alert
Sorted by time descending
 
