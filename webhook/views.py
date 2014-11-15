from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='root')
def root_view(request):
    return Response('Hello s!' % request.matchdict)

