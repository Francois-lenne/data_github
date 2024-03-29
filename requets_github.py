
# package you need to import for this project
import os
import requests
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timedelta
import pandas as pd
import pandas_redshift as pr




def get_commit_stats(username, token):
    # Create a session to handle retries
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # Get list of repositories
    repos_response = session.get(f'https://api.github.com/users/{username}/repos', auth=(username, token))
    repos = repos_response.json()

    start_date = datetime.now() - timedelta(days=7)  # start date, 7 days ago

    data = []

    for repo in repos:
        # Skip forked repositories
        if repo['fork']:
            continue

        repo_name = repo['name']
        
        # Check if repository has commits
        commits_response = session.get(f'https://api.github.com/repos/{username}/{repo_name}/commits', auth=(username, token))
        commits = commits_response.json()
        if not commits:
            continue  # skip repository if it has no commits

        # Check if the last commit is within the period
        last_commit_date = datetime.strptime(commits[0]['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ')
        if last_commit_date < start_date:
            continue  # skip repository if the last commit is not within the period

        # Get number of commits and lines changed by date
        date = start_date
        while date < datetime.now():
            since = date.isoformat() + 'Z'  # convert to ISO 8601 format
            until = (date + timedelta(days=1)).isoformat() + 'Z'
            commits_response = session.get(f'https://api.github.com/repos/{username}/{repo_name}/commits?since={since}&until={until}', auth=(username, token))
            commits = commits_response.json()
            num_commits = len(commits)
            lines_added = 0
            lines_deleted = 0
            for commit in commits:
                commit_response = session.get(commit['url'], auth=(username, token))
                stats = commit_response.json().get('stats', {})
                lines_added += stats.get('additions', 0)
                lines_deleted -= stats.get('deletions', 0)
            data.append([repo_name, date.strftime("%Y-%m-%d"), num_commits, lines_added, lines_deleted])
            date += timedelta(days=1)  # move to next day

    df_delete_add = pd.DataFrame(data, columns=['Repo', 'Date', 'Commits', 'Lines added', 'Lines deleted'])
    return df_delete_add









# retrieve all the repo and the languages used in the github repository


def get_repo_languages(username, token):
    # Get list of repositories
    repos_response = requests.get(f'https://api.github.com/users/{username}/repos', auth=(username, token))
    repos = repos_response.json()

    data = []

    for repo in repos:
        # Skip forked repositories
        if repo['fork']:
            continue

        repo_name = repo['name']
        
        # Get repository languages
        languages_response = requests.get(f'https://api.github.com/repos/{username}/{repo_name}/languages', auth=(username, token))
        languages = languages_response.json()
        
        data.append([repo_name, ", ".join(languages.keys())])

    df_repo_language = pd.DataFrame(data, columns=['Repo', 'Languages'])

    df_repo_language['Languages'] = df_repo_language['Languages'].apply(lambda x: x.split(', ')) # transform the string of languages into a list of languages
    return df_repo_language










# retrieve the number of views and stars of the github repository for the last 7 days
def get_repo_views_stars(username, token):
    # Get list of repositories
    repos_response = requests.get(f'https://api.github.com/users/{username}/repos', auth=(username, token))
    repos = repos_response.json()

    data = []

    for repo in repos:
        # Skip forked repositories
        if repo['fork']:
            continue

        repo_name = repo['name']
        
        # Get repository traffic views
        views_response = requests.get(f'https://api.github.com/repos/{username}/{repo_name}/traffic/views', auth=(username, token))
        views_data = views_response.json()
        
        # Get repository stars
        stars = repo['stargazers_count']
        
        # Get views per day
        for view in views_data['views']:
            view_date = datetime.strptime(view['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
            if view_date >= datetime.now() - timedelta(days=7):  # only include views from the last 7 days
                data.append([repo_name, stars, view_date.strftime("%Y-%m-%d"), view['count']])

    df_view_star = pd.DataFrame(data, columns=['Repo', 'Stars', 'Date', 'Views'])
    return df_view_star





# function to retrieve collaborator and author of the repo 


def get_author_repo_collaborators(username, token):
    # Get list of repositories
    repos_response = requests.get(f'https://api.github.com/users/{username}/repos', auth=(username, token))
    repos = repos_response.json()

    data = []

    for repo in repos:
        # Skip forked repositories
        if repo['fork']:
            continue

        repo_name = repo['name']
        author_name = repo['owner']['login']
        
        # Get list of collaborators
        collaborators_response = requests.get(f'https://api.github.com/repos/{username}/{repo_name}/collaborators', auth=(username, token))
        collaborators = collaborators_response.json()
        collaborators_names = [collaborator['login'] for collaborator in collaborators]
        
        data.append([author_name, repo_name, collaborators_names])

    df_author_repo_collaborators = pd.DataFrame(data, columns=['Author', 'Repo', 'Collaborators'])
    return df_author_repo_collaborators



# main function to call all the functions above


def main():



   # retrieve the data from the github api 
    username = 'Francois-lenne'
    token = os.getenv('GITHUB_TOKEN')

    df_delete_add_line = get_commit_stats(username, token)
    print(df_delete_add_line)
    df_repo_language = get_repo_languages(username, token)
    print(df_repo_language)
    df_view_star_date = get_repo_views_stars(username, token)
    print(df_view_star_date)
    df_author_repo_collaborators = get_author_repo_collaborators(username, token)
    print(df_author_repo_collaborators)



    # load the data into the redshift database


    # information for AWS redshift

    dbname = os.getenv('REDSHIFT_DBNAME')
    host = os.getenv('REDSHIFT_HOST')
    port = os.getenv('REDSHIFT_PORT')
    user = os.getenv('REDSHIFT_USER')
    password = os.getenv('REDSHIFT_PASSWORD')

    # information for AWS S3

    bucket = os.getenv('S3_BUCKET')
    subdirectory = os.getenv('S3_SUBDIRECTORY')
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')



    pr.connect_to_redshift(dbname=dbname, host=host, port=port, user=user, password=password)
    pr.connect_to_s3(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, bucket=bucket, subdirectory=subdirectory)



    # Load the data into the redshift database


    ## load the data into the redshift database for the stat repo
    pr.pandas_to_redshift(data_frame=df_delete_add_line, redshift_table_name='stat_commit_repo', append=True)

    ## load the data into the redshift database for the repo stat by date 
    pr.pandas_to_redshift(data_frame=df_view_star_date, redshift_table_name='stat_repo_by_date', append=True)





    pr.close_up_shop()
    return "Success"




if __name__ == "__main__":
    main()



