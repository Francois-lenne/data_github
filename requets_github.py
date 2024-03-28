
# package you need to import for this project
import os
import requests
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timedelta
import pandas as pd



# credentials informations
username = 'Francois-lenne'
token = os.getenv('GITHUB_TOKEN')




# retrieve all the repo and the languages used in the github repository


def language_repo(username, token):
    repos_response = requests.get(f'https://api.github.com/users/{username}/repos', auth=(username, token))
    repos = repos_response.json()

    for repo in repos:
        # Skip forked repositories
        if repo['fork']:
            continue

        repo_name = repo['name']
        
        # Get repository languages
        languages_response = requests.get(f'https://api.github.com/repos/{username}/{repo_name}/languages', auth=(username, token))
        languages = languages_response.json()
        
        print(f'Repo: {repo_name}, Languages: {", ".join(languages.keys())}')




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
                lines_deleted += stats.get('deletions', 0)
            data.append([repo_name, date.strftime("%Y-%m-%d"), num_commits, lines_added, lines_deleted])
            date += timedelta(days=1)  # move to next day

    df_delete_add = pd.DataFrame(data, columns=['Repo', 'Date', 'Commits', 'Lines added', 'Lines deleted'])
    return df_delete_add


df_delete_add = get_commit_stats(username, token)







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




df_repo_language = get_repo_languages(username, token)



df_repo_language







# retrieve the number of views and stars of the github repository for the last 7 day
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
                data.append([repo_name, stars, view['timestamp'], view['count']])

    df_view_star = pd.DataFrame(data, columns=['Repo', 'Stars', 'Date', 'Views'])
    return df_view_star

