import json
import base64

__all__ = [
    'get_branch',
    'get_author',
    'get_changes',
    'get_github_json',
]

def get_branch(commit):
    branch = commit['ref'].split('/')
    branch = branch[-1]
    return branch

def get_author(commit):
    author = commit['commits'][0]['author']['name']
    return author

def get_changes(commit):
    changes_path = commit['commits'][0]
    added = changes_path['added']
    modified = changes_path['modified']
    removed = changes_path['removed']
    return (added, modified, removed)

def get_github_json(data):
    content_from_github = data.json()['content']
    json_raw_data = base64.b64decode(content_from_github)
    json_object = json.loads(json_raw_data)
    return json_object

