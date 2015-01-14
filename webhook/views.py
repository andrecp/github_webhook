from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import notfound_view_config
import os
import engine
from restapi import RESTAPIService

class RootView(object):
    def __init__(self, request, api_service=None):
        self.request = request
        if api_service is None:
            self.api = RESTAPIService()
        else:
            self.api = api_service

    def send_data(self, git_url, git_branch, push_url, data):
        # add data
        for add_data in data[0]:
            raw_data_from_github = self.api.get(git_url+add_data, params=git_branch)
            github_json = engine.get_github_json(raw_data_from_github)
            self.api.put(push_url+add_data, github_json)
        # update data
        for update_data in data[1]:
            raw_data_from_github = self.api.get(git_url+update_data, params=git_branch)
            github_json = engine.get_github_json(raw_data_from_github)
            headers = {'content-type':'application/json','info':'updated'}
            self.api.put(push_url+update_data, github_json, headers=headers)
        # remove data
        for delete_data in data[2]:
            self.api.delete(push_url+delete_data)

    @view_config(route_name='root', request_method='POST')
    def default_view(self):
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
        data = self.request.json_body

        print data

        author = engine.get_author(data)
        push_branch = engine.get_branch(data)
        changes = engine.get_changes(data)

        if git_branch == push_branch:
            r = self.api.get(push_to)
            if r.status_code == 200:
                self.send_data(git_url, git_branch, push_to, changes)
                response_msg = '{0}\nSuccessfuly commited to {1}'.format(author,git_branch)
            else:
                response_msg = 'Failed to connect to Database\nStatus:' + str(r.status_code)
        else:
            response_msg = '{0} wrong branch!\nYou commited to {1}.\nOnly accepting commits to {2} branch.'.format(author, push_branch, git_branch)
        return Response(response_msg)
            
    @notfound_view_config(request_method='GET')
    def not_found_view(self):
        return Response('Only accepting POST')
          
    
