import requests
import pygit2
import os
from datetime import datetime

def clone_repository(github_username, repo_name):
    forked_repo_url = f'https://github.com/{github_username}/{repo_name}.git'
    local_repo_path = f'./{repo_name}'
    if not os.path.exists(local_repo_path):
        repo = pygit2.clone_repository(forked_repo_url, local_repo_path)
    else:
        repo = pygit2.Repository(local_repo_path)
    return repo, local_repo_path

def create_branch(repo, new_branch_name):
    reference = repo.lookup_reference('refs/heads/main')
    target_commit = repo.get(reference.target)
    repo.create_branch(new_branch_name, target_commit)
    repo.checkout('refs/heads/' + new_branch_name)

def commit_changes(repo, github_username, new_branch_name, commit_message):
    index = repo.index
    # /test ディレクトリのみを追加
    for root, dirs, files in os.walk(os.path.join(repo.workdir, 'test')):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), repo.workdir)
            index.add(file_path)
    
    index.write()
    author = pygit2.Signature(github_username, f'{github_username}@users.noreply.github.com')
    committer = author
    tree = index.write_tree()
    repo.create_commit(f'refs/heads/{new_branch_name}', author, committer, commit_message, tree, [repo.head.target])

def push_changes(repo, github_username, github_token, new_branch_name):
    remote = repo.remotes['origin']
    credentials = pygit2.UserPass(github_username, github_token)
    callbacks = pygit2.RemoteCallbacks(credentials=credentials)
    
    try:
        remote.push([f'refs/heads/{new_branch_name}'], callbacks=callbacks)
    except pygit2.GitError as e:
        print(f"Error pushing to remote: {e}")

def create_pull_request(github_token, repo_owner, repo_name, github_username, new_branch_name, pr_title, pr_body):
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    pr_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls'
    pr_data = {
        'title': pr_title,
        'body': pr_body,
        'head': f'{github_username}:{new_branch_name}',
        'base': 'main'
    }
    response = requests.post(pr_url, headers=headers, json=pr_data)
    if response.status_code == 201:
        print(f'Successfully created PR: {response.json()["html_url"]}')
    else:
        print(f'Error creating PR: {response.json()}')

def automate_github_workflow(github_token, github_username, repo_owner, repo_name, new_branch_name, commit_message, pr_title, pr_body):
    repo, local_repo_path = clone_repository(github_username, repo_name)
    create_branch(repo, new_branch_name)
    commit_changes(repo, github_username, new_branch_name, commit_message)
    push_changes(repo, github_username, github_token, new_branch_name)
    create_pull_request(github_token, repo_owner, repo_name, github_username, new_branch_name, pr_title, pr_body)

# PRを作成する関数
# 
# title: PRのタイトル
# body: PRの本文
# number: issue番号(string)
def create_pr(title, body, number):
    now = datetime.now()
    formatted_date = now.strftime('%Y%m%d_%H%M%S')
    issue_reference = f"#{number}\n{body}"

    GITHUB_TOKEN = ''
    GITHUB_USERNAME = 'koyama0318'
    REPO_OWNER = 'koyama0318'
    REPO_NAME = 'todo-app'
    NEW_BRANCH_NAME = 'test_branch_' + formatted_date
    COMMIT_MESSAGE = 'Add test code #' + number

    automate_github_workflow(GITHUB_TOKEN, GITHUB_USERNAME, REPO_OWNER, REPO_NAME, NEW_BRANCH_NAME, COMMIT_MESSAGE, title, issue_reference)

# テスト用
def main():
    # 引数を設定する場合は、argparseなどを使用して引数を取得します
    title = "PRのタイトル"
    body = "PRの本文"
    number = "42"  # Issue番号を設定

    create_pr(title, body, number)

if __name__ == "__main__":
    main()