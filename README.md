# Discount Code

## General Notes
* The project is intended to manage discount codes for brands.
* Theres the main app called dcapp, 2 side modules named ratelimiter and clients.
* Currently there are 2 endpoints to generate and get discount codes in dcapp.
* A simple ratelimiter to apply simple limiting rules for getcode is implemented in ratelimiter module.
* Clients module is for communicating with other microservices.



## How To Start The Project
* To build and run containers, in the root of project simply run
```bash
docker-compose up --build 
```
* To run docker-compose in background run
```bash
docker-compose up -d
```
* For more information about running docker-compose, checkout https://docs.docker.com/engine/reference/commandline/compose_up/
* Check output logs. Both postgres and backend containers should be running without problem.
* Server listens on port 8000, if you wish to forward 8000 to another port like xxxx on your machine, change "8000:8000" to "8000:xxxx" in docker-compose and re-up the containers.



## Endpoints
### Generate Codes
#### Request
* POST /generate-dc/
* Request_body
```json
{
    "brand_slug": "string: The brand to generate code for",
    "count": "int: number of discount codes to generate",
    "percent": "int: discount percent"
}
```
#### Response
* Response: 200 HttpResponse with no body.

### Get Code
#### Request
* POST /get-dc/
* Request Header
```json
{
    "username": "string: This header is expected to be filled by Auth service if the user is logged in".
}
```
* Request Body
```json
{
    "brand_slug": "string: The brand to get discount code from."
}
```
#### Response
* Permissions: Login Required
* Rate limit: request to get a discount code from same brand 2 times in 5 seconds(can be changed in settings) will be rate limited.
* Response 200: 200 HttpResponse. content is of bytes types. Its the string representing the fetched discount code.
* Response 403: If not logged in, or sending too many requests will get ratelimited.

### Usage Example With Curl
* Generate codes
```bash
curl --location --request POST 'localhost:8000/generate-dc/' \
--header 'Content-Type: application/json' \
--data-raw '{"brand_slug": "test_brand", "count":1000, "percent": 30}'
```
* Get code (Will get 403 for ratelimit or not specifiying username in headers)
```bash
curl --location --request POST 'localhost:8000/get-dc/' \
--header 'username: hesam' \
--header 'Content-Type: application/json' \
--data-raw '{"brand_slug": "test_brand"}'
```



## Next Steps
* Use tools like Swagger to document endpoints and apis.
* Add verifydiscount code and deletediscountcode  endpoints.
* Use persistant celery to send async notificatins instead of thread.
* Add redis to getdiscountcode, load batch codes from db and cache them. This can make reads faster and better avoid race conditions.
* Add expiration date and CronJob to purge expired discountcode records from db, to avoid database getting too big.
* Add shared-memory and persistant rate limiter for overusage for users, can be implemented with Redis.
* Add gitlab ci and pipelines to test and lint the code before merge.
* Write unittests for utils and ratelimiter. Then integration tests written for dcapp can be changed to unittests.
