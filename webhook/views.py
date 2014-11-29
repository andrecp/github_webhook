from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import notfound_view_config
import json
import os
import requests

from engine import get_branch, get_author, get_changes

def sendData(url, data):
    # send add data
    data_from_file = open(''.join(data[0]))
    json_from_file = json.load(data_from_file)
    for new_data in data[0]:
        requests.post(url+'desk_list.json', json=json_from_file)
    # send update data
    # send remove data

@view_config(route_name='root', request_method='POST')
def root_view(request):
    branch = os.getenv('WEBHOOK_BRANCH','WEBHOOK_BRANCH ENV VARIABLE NOT SET')
    push_to = os.getenv('PUSH_URL','PUSH_URL ENV VARIABLE NOT SET')

    data = request.json_body
    author = get_author(data)
    push_branch = get_branch(data)
    changes = get_changes(data)

    if branch == push_branch:
        try:
            r = requests.get(push_to)
        except requests.exceptions.ConnectionError as e:
            return Response('Domain does not exist.')

        if r.status_code == 200:
            sendData(push_to, changes)
            response_msg = '{0}\nSuccessfuly commited to {1}'.format(author,branch)
        else:
            response_msg = 'Failed to connect to Firebase\nStatus:' + str(r.status_code)
    else:
        response_msg = '{0} wrong branch!\nYou commited to {1}.\nOnly accepting commits to {2} branch.'.format(author, push_branch, branch)
    return Response(response_msg)
        
@notfound_view_config(request_method='GET')
def not_found_view(request):
    return Response('Only accepting POST')
      

