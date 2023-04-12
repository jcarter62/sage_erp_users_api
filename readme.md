
Note: the db user needs to have access to read server state.  
Here is an example script to allow the user api to have read 
access to the required data.


<code>
USE master;

GRANT VIEW SERVER STATE TO api
</code>