from pyramid.response import Response
from pyramid.view import view_config
import json
import os

from engine import get_branch, get_author

@view_config(route_name='root')
def root_view(request):
    branch = os.environ['WEBHOOK_BRANCH']
    if request.method == 'POST':
        data = request.json_body
        author = get_author(data)
        push_branch = get_branch(data)
        if branch == push_branch:
            response_msg = '{0}\nSuccessfuly commited to {1}'.format(author,branch)
            return Response(response_msg)
        else:
            response_msg = '{0} wrong branch!\nYou commited to {1}.\nOnly accepting commits to {2} branch.'.format(author, push_branch, branch)
            return Response(response_msg)
    else:
        return Response('Not a post!')
      

