
# package you need to import for this project
import os
import requests



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



