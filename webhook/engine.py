import base64
import json
import os

__all__ = [
    'get_branch',
    'get_author',
    'get_changes',
    'get_github_json',
    'get_commit_url',
]

DEFAULTS = {
    'whitelist' : os.environ.get('WEBHOOK_WHITELIST', '.json;files'),
}

def get_branch(commit):
    branch = 'Could not decode branch'
    try:
        branch = commit['ref'].split('/')
        branch = branch[-1]
    except KeyError as e:
        print e
    return branch

def get_author(commit):
    author = 'Could not decode author'
    try:
        author = commit['commits'][0]['author']['name']
    except KeyError as e:
        print e
    return author

def _whitelist(candidate_list):
    allowed = DEFAULTS['whitelist'].split(';')
    whitelist = []
    print 'RECEIVED: ' + ' '.join(candidate_list)

    # Check if it's a JSON document
    for item in candidate_list:
        is_json = '.' + item.split('.')[-1] 
        if is_json in allowed:
            whitelist.append(item)
        # Check if it's a files/:name.ext
        folders = item.split('/')
        for sub_folders in folders:
            if sub_folders in allowed:
                whitelist.append(item)
    print 'WHITELIST: ' + ' '.join(whitelist)
    return whitelist

def get_base_url(commit):
    base_url ='Could not decode commit url' 
    try:
        # We are getting {URL}/commit/{HASH} and base url is {URL}
        base_url = commit['commits'][0]['url'].split('commit')[0]
    except KeyError as e:
        print e
    return base_url

def get_changes(commit):
    changes_path = {}
    changes_path['added'] = []
    changes_path['modified'] = []
    changes_path['removed'] = []
    try:
        changes_path = commit['commits'][0]
    except KeyError as e:
        print e
    
    added = changes_path['added']
    modified = changes_path['modified']
    removed = changes_path['removed']
    
    # Get only the whitelist items
    added = _whitelist(added)
    modified = _whitelist(modified)
    removed = _whitelist(removed)
    return (added, modified, removed)

def get_github_json(data):
    content_from_github = data.json()['content']
    json_raw_data = base64.b64decode(content_from_github)
    json_object = json.loads(json_raw_data)
    return json_object

