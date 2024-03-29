import pandas_redshift as pr
import os



# connection to redshift


dbname = os.getenv('REDSHIFT_DBNAME')
host = os.getenv('REDSHIFT_HOST')
port = os.getenv('REDSHIFT_PORT')
user = os.getenv('REDSHIFT_USER')
password = os.getenv('REDSHIFT_PASSWORD')


pr.connect_to_redshift(dbname=dbname, host=host, port=port, user=user, password=password)




# creation of the table 


## create the table for the commit stats


pr.exec_commit("""
    CREATE TABLE IF NOT EXISTS stat_commit_repo (
        Repo VARCHAR(256), 
        Date DATE, 
        Commits INTEGER, 
        Line_Added INTEGER, 
        Line_Delete INTEGER
    );
""")


## create the table for the repo stat by date



pr.exec_commit("""
    CREATE TABLE IF NOT EXISTS stat_repo_by_date (
        Repo VARCHAR(256), 
        Date DATE, 
        Views INTEGER, 
        Stars INTEGER
    );
""")