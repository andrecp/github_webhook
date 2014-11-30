from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import notfound_view_config
import json
import os
import requests

from engine import get_branch, get_author, get_changes

def sendData(git_url, git_branch, push_url, data):
    # send add data
    for new_data in data[0]:
        data_from_github = requests.get(git_url+new_data, params=git_branch)
        print data_from_github.json()
        #data_from_file = open(''.join(data[0]))
        #json_from_file = json.load(data_from_file)
        #requests.post(push_url, json=json_from_file)
    # send update data
    # send remove data

@view_config(route_name='root', request_method='POST')
def root_view(request):
    # check for ENV variables
    git_url = os.environ.get('GIT_URL')
    if git_url == None:
        return Response('GIT_URL not set')
    git_branch = os.environ.get('GIT_BRANCH')
    if git_branch == None:
        return Response('GIT_BRANCH not set')
    push_to = os.environ.get('PUSH_URL')
    if push_to == None:
        return Response('PUSH_URL not set')

    # get data from the github event
    data = request.json_body
    author = get_author(data)
    push_branch = get_branch(data)
    changes = get_changes(data)

    if git_branch == push_branch:
        try:
            r = requests.get(push_to)
        except requests.exceptions.ConnectionError as e:
            return Response('Domain does not exist.')

        if r.status_code == 200:
            sendData(git_url, git_branch, push_to, changes)
            response_msg = '{0}\nSuccessfuly commited to {1}'.format(author,git_branch)
        else:
            response_msg = 'Failed to connect to Firebase\nStatus:' + str(r.status_code)
    else:
        response_msg = '{0} wrong branch!\nYou commited to {1}.\nOnly accepting commits to {2} branch.'.format(author, push_branch, git_branch)
    return Response(response_msg)
        
@notfound_view_config(request_method='GET')
def not_found_view(request):
    return Response('Only accepting POST')
      

