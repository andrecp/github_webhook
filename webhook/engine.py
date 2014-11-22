__all__ = [
    'get_branch',
    'get_author',
]

def get_branch(commit):
    branch = commit['ref'].split('/')
    branch = branch[-1]
    return branch

def get_author(commit):
    author = commit['commits'][0]['author']['name']
    return author
