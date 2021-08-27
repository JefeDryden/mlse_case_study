# mlse_case_study
This was a case study completed for MLSE which asked to use the Twitter API to retrieve, download, clean, and store the trending tweets across Canada into an SQL database on a daily basis.

I decided to implement the solution into an AWS environment in order to not have to rely on my own hardware, and as a fun challenge for myself. 

The overall setup uses 4 services in AWS:
1. Lambda - for running the code
2. RDS PostgreSQL - to store the cleaned data into a fact table in a PostgreSQL environment
3. S3 - to store the raw json data downloaded from Twitter
4. Cloudwatch Events - to configure a daily trigger which will run the Lambda once per day at 4 PM (20:00GMT). 

Associated pictures to show proof of everything configured will be attached. They show one particular execution of the code at 1:56PM. The logs, data entry, and file timestamps in the pictures should all match this to show that the program is working.

Link to Google Studio report can be found here! https://datastudio.google.com/s/iFN4MW--Cj8

Potential improvements:
1. Currently the program appends data into the tables, but does not check to make sure the data point does not already exist. Would be very useful to prevent duplicate entries.
2. While I currently only pull in data that is Canada wide, I could also retrieve the trending information from 7 different cities in Canada (Identified from the Get Trends/Available Twitter API Call). 
3. Could not find any examples where there was a promoted trend on Twitter, so while I know it is "Null" for false in the "Promoted" field, I would like to know what "True" is so that I can better store it.
4. I considered separating the various categories of supplmental functions into separate files. I decided that due to the small size of the overall file, it would only make reading the function more difficult.

The code itself uses the handler -> mlse_trending.handler
To run the code on your local device, make sure to set up the appropriate local variables for the PostgreSQL server and Twitter API credentials. Also 
