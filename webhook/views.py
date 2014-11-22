from pyramid.response import Response
from pyramid.view import view_config
import json
import os

@view_config(route_name='root')
def root_view(request):
    branch = os.environ['WEBHOOK_BRANCH']
    if request.method == 'POST':
        data = request.json_body
        print 'New commit by: {0} '.format(data['commits'][0]['author']['name'])
        push_branch = data['ref'].split('/')
        push_branch = push_branch[-1]
        if branch == push_branch:
            response_msg = 'Successfuly commited to {0}'.format(branch)
            return Response(response_msg)
        else:
            response_msg = 'Wrong Branch!\nYou commited to {0}, we are only accepting commits to {1} branch'.format(push_branch, branch)
            return Response(response_msg)
    else:
        return Response('Not a post!')
      

