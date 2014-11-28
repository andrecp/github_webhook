__all__ = [
    'get_branch',
    'get_author',
    'get_changes',
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
    removed = changes_path['removed']
    modified = changes_path['modified']
    return (added, removed, modified)
