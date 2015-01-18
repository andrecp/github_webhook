import base64
import json
import os

__all__ = [
    'get_branch',
    'get_author',
    'get_base_url',
    'get_serving_url',
    'get_changes',
    'get_github_json',
]

DEFAULTS = {
    'whitelist' : os.environ.get('GITHUB_WEBHOOK_WEBHOOK_WHITELIST', '.json;files'),
}

"""
This module is responsible for doing operations in JSON data received
from a given GitHub respository.
"""

def get_branch(commit):
    branch = u'Could not decode branch'
    try:
        branch = commit['ref'].split('/')
        branch = branch[-1]
    except KeyError as e:
        print e
    return branch

def get_author(commit):
    author =  u'Could not decode author'
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
    # We are getting {URL}/commit/{HASH} and base url is {URL}
    base_url = u'Could not decode base url' 
    print commit['commits'][0]['url']
    try:
        base_url = commit['commits'][0]['url'].split('commit')[0]
    except KeyError as e:
        print e
    return base_url

def get_serving_url(base_url):
    # Mounting URL with RAW content to download from
    # e.g:https://raw.githubusercontent.com/opendesk/collection/master/
    prefix = u'https://raw.githubusercontent.com/'
    branch = u'{0}'.format(os.environ.get('GITHUB_WEBHOOK_GIT_BRANCH'))

    # opendesk/collection/
    len_to_jump = len('https://github.com/')
    relevant_data = base_url[len_to_jump:]
    # mounting serving URL 
    serving_url = prefix + relevant_data + branch + '/'
    return serving_url

def _get_dict_w_last_commits(commits_list):
    candidate_added_dict = {}
    candidate_modified_dict = {}
    candidate_removed_dict = {}

    # Reverse commits list so we can have the last changes
    commits_history = reversed(commits_list)

    last_modified_commit = 0

    for commit in commits_history:
        last_modified_commit = last_modified_commit + 1

        # XXXX REFACTOR TO A FUNCTION LATER
        candidate_to_add = _whitelist(commit['added'])
        if candidate_to_add:
            for item in candidate_to_add:
                to_str_key = ''.join(item)
                candidate_added_dict[to_str_key] = (to_str_key, last_modified_commit)

        candidate_to_modify = _whitelist(commit['modified'])
        if candidate_to_modify:
            for item in candidate_to_modify:
                to_str_key = ''.join(item)
                candidate_modified_dict[to_str_key] = (to_str_key, last_modified_commit)

        candidate_to_remove = _whitelist(commit['removed'])
        if candidate_to_remove:
            for item in candidate_to_remove:
                to_str_key = ''.join(item)
                candidate_removed_dict[to_str_key] = (to_str_key, last_modified_commit)
    return (candidate_added_dict, candidate_modified_dict, candidate_removed_dict)

def get_changes(commit):
    # Dummy object for non resolved webhooks
    commits_list = {}
    commits_list['added'] = []
    commits_list['modified'] = []
    commits_list['removed'] = []
    try:
        commits_list = commit['commits']
    except KeyError as e:
        print e

    #
    added_list = []
    modified_list = []
    removed_list = []

    # Resolve all commits history to a single dict
    add_dict, mod_dict, rm_dict = _get_dict_w_last_commits(commits_list)

    # Removing items from dict if last change was a remove
    for key in rm_dict.keys():
        removed_timestamp = rm_dict[key][1]
        key_deleted = False
        if key in add_dict:
            if removed_timestamp >= add_dict[key][1]:
                del add_dict[key]
            else:
                del rm_dict[key]
                key_deleted = True

        if key in mod_dict:
            if removed_timestamp >= mod_dict[key][1]:
                del mod_dict[key]
            else:
                if not key_deleted:
                    del rm_dict[key]

    for key in add_dict.keys():
        added_list.append(add_dict[key][0])
    for key in mod_dict.keys():
        modified_list.append(mod_dict[key][0])
    for key in rm_dict.keys():
        removed_list.append(rm_dict[key][0])
 
    return (added_list, modified_list, removed_list)

def get_github_json(data):
    json_data = data.json()
    content_from_github = json_data['content']
    sha1_from_github = json_data['sha']
    json_raw_data = base64.b64decode(content_from_github)
    json_object = json.loads(json_raw_data)
    return json_object

