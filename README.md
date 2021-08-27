# mlse_case_study
This was a case study completed for MLSE which asked to use the Twitter API to retrieve, download, clean, and store the trending tweets across Canada into an SQL database on a daily basis.

I decided to implement the solution into an AWS environment in order to not have to rely on my own hardware, and as a fun challenge for myself. 

The overall setup uses 4 services in AWS:
1. Lambda - for running the code
2. RDS PostgreSQL - to store the cleaned data into a fact table in a PostgreSQL environment
3. S3 - to store the raw json data downloaded from Twitter
4. Cloudwatch Events - to configure a daily trigger which will run the Lambda once per day at 3 PM. 

Associated pictures to show proof of everything configured will be attached.

Potential improvements:
1. Currently the program appends data into the tables, but does not check to make sure the data point does not already exist. Would be very useful to prevent duplicate entries.
2. While I currently only pull in data that is Canada wide, I could also retrieve the trending information from 7 different cities in Canada (Identified from the Get Trends/Available Twitter API Call). 
3. Could not find any examples where there was a promoted trend on Twitter, so while I know it is "Null" for false in the "Promoted" field, I would like to know what "True" is so that I can better store it.
