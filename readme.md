# Deployment

Create a folder to hold the files for the deployment.  In this example
the folder is called "SageErpUsers".

<code>
git clone https://github.com/jcarter62/sage_erp_users_api.git
</code>

# .env file

Create a env.txt file in the root of the deployment folder.  The env.txt 
file contains the configuration for the application.  This file is not
checked into source control, and during deployment the file is copied
to api/.env.

A sample file is provided in the deployment folder.  Copy the
sample file to env.txt and edit the file to match your environment.

Copy env.txt to api/.env after you have edited the file.


# SQL Server - Server State:

Note: the db user needs to have access to read server state.  
Here is an example script to allow the user api to have read 
access to the required data.  In this case the user named api
is being granted access to the server state.


<code>
USE master;

GRANT VIEW SERVER STATE TO api
</code>
