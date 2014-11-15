from pyramid.response import Response
from pyramid.view import view_config
import json

@view_config(route_name='root')
def root_view(request):
    if request.method == 'GET':
        print 'Hello world!'
        return Response('Hello world!')
    elif request.method == 'POST':
        print 'Hello post world!\n'
        data = request.json_body
        print 'New commit by: {0} '.format(data['commits'][0]['author']['name'])
        return Response('Hello post world!')

