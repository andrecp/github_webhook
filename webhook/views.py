from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import notfound_view_config
import json
import os

from engine import get_branch, get_author, get_changes

@view_config(route_name='root', request_method='POST')
def root_view(request):
    branch = os.getenv('WEBHOOK_BRANCH','WEBHOOK_BRANCH ENV VARIABLE NOT SET')
    push_to = os.getenv('PUSH_URL','PUSH_URL ENV VARIABLE NOT SET')
    data = request.json_body
    author = get_author(data)
    push_branch = get_branch(data)
    changes = get_changes(data)
    print 'What has changed' + str(changes)
    if branch == push_branch:
        response_msg = '{0}\nSuccessfuly commited to {1}'.format(author,branch)
    else:
        response_msg = '{0} wrong branch!\nYou commited to {1}.\nOnly accepting commits to {2} branch.'.format(author, push_branch, branch)
    return Response(response_msg)
        
@notfound_view_config(request_method='GET')
def not_found_view(request):
    return Response('Only accepting POST')
      

