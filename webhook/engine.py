import base64
import hashlib
import hmac
import json
import os
import re

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'get_branch',
    'get_author',
    'get_base_url',
    'get_serving_url',
    'get_changes',
    'get_github_json',
    'validate_signature',
]

DEFAULTS = {
    'whitelist'        : os.environ.get('GITHUB_WEBHOOK_WHITELIST', 'product.json;fileset.json'),
    'blacklist'        : os.environ.get('GITHUB_WEBHOOK_BLACKLIST', '_'),
    'git_secret_token' : os.environ.get(b'GITHUB_WEBHOOK_opendesk_collection__SECRET_TOKEN', None),
}

"""
This module has utilities regarding operations in JSON data received
from a given GitHub respository and auxiliary tools.
"""

def get_branch(commit):
    branch = u'Could not decode branch'
    try:
        branch = commit['ref'].split('/')
        branch = branch[-1]
    except KeyError, e:
        logger.error((e, branch))
    else:
        return branch

def get_author(commit):
    author =  u'Could not decode author'
    try:
        author = commit['commits'][0]['author']['name']
    except KeyError, e:
        logger.error((e, author))
    else:
        return author

def _whitelist(candidate_list):
    allowed     = DEFAULTS['whitelist'].split(';')
    not_allowed = DEFAULTS['blacklist'].split(';')
    json_list = []
    print 'ALOWED  : '+ ' '.join(allowed)
    print 'NOT ALOWED  : '+ ' '.join(not_allowed)

    print 'RECEIVED: ' + ' '.join(candidate_list)

    # Check if it's whitelisted
    for item in candidate_list:
        item_path = item.split('/')
        print 'debugging... Item Path'
        print item_path
        print 'debugging... Last /'
        print item_path[-1]
        is_whitelisted = item_path[-1] in allowed
        print 'is_whitelisted'
        print is_whitelisted
        is_blacklisted = True in [sub_path[0] in not_allowed
                             for sub_path in item_path]
        print 'is_blacklisted'
        print is_blacklisted
        if is_whitelisted and not is_blacklisted:
            json_list.append(item)
        #elif not is_blacklisted:
        # Items that are not blacklisted are regular files
        # Can have a different behaviour in the future, just appending for now
            # json_list.append(item)

    print 'WHITELIST: ' + ' '.join(json_list)
    return json_list

def get_base_url(commit):
    # We are getting {URL}/commit/{HASH} and base url is {URL}
    base_url = u'Could not decode base url' 
    try:
        base_url = commit['commits'][0]['url'].split('commit')[0]
    except KeyError, e:
        logger.error((e, base_url))
    else:
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
    except KeyError, e:
        logger.error((e, 'no commits in github JSON'))

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
    size = 0

    # If its bigger than 1MB we will post an empty dict
    try:
        size = json_data['size']
    except KeyError, e:
        logger.error((e, size))
        logger.warn(json_data)
    else:
        if size > 1000000:
            return json.loads('{}')

    # Smaller than 1MB, retrieving content 
    try:
        content_from_github = json_data['content']
    except KeyError, e:
        logger.error((e, json_data))
        logger.warn(json_data)
    else:
        json_raw_data = base64.b64decode(content_from_github)
        json_object = json.loads(json_raw_data)
        return json_object

def validate_signature(data, signature_received):
    sha_name, signature = signature_received.split('=')
    if sha_name != 'sha1':
        return False

    # HMAC requires its key to be bytes, but data is strings.
    mac = hmac.new(DEFAULTS['git_secret_token'], msg=data, digestmod=hashlib.sha1)
    # Should exist in Python 2.7.7
    if hasattr(mac, 'compare_digest'):
        return hmac.compare_digest(mac.hexdigest(), signature)
    else:
        return mac.hexdigest() == b'{0}'.format(signature)

def get_bearer_token(api):
    api_env = os.environ.keys()[os.environ.values().index(api)]
    api_token = api_env.split('__')[0]
    return os.environ.get('{0}__SECRET_TOKEN'.format(api_token))

def create_async_lists_by_structure(list_of_requests):
    """    
    Create lists of data to be pushed to an API by order of resources
    """
    # Create a dict entry for each depth that can be requested concurrently
    unique_dict = {}
    for item in list_of_requests:
        depth = item.count('/')
        if depth not in unique_dict:
            unique_dict[depth] = [item]
        else:
            unique_dict[depth].append(item)

    # Create a list for each depth
    lists = [[]]*len(unique_dict.keys())

    # Order the keys to do begin by the lower depths
    # make a list for each depth
    sorted_keys = []
    i = 0
    for key in sorted(unique_dict):
        lists[i] = unique_dict[key]
        i = i + 1
    return lists
