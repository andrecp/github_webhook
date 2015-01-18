from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import notfound_view_config
import os
import engine
from restapi import RESTAPIService

DEFAULTS = {
    'git_url'    : os.environ.get('GITHUB_WEBHOOK_GIT_URL'),
    'git_branch' : os.environ.get('GITHUB_WEBHOOK_GIT_BRANCH'),
    'push_url'   : os.environ.get('GITHUB_WEBHOOK_GIT_PUSH_URL'),
}

class RootView(object):
    def __init__(self, request, api_service=None):
        self.request = request
        if api_service is None:
            self.api = RESTAPIService()
        else:
            self.api = api_service

    def send_data(self, git_url, push_url, git_info):
        """This method formats and sends data to our API."""
        # Unpacking data
        data        = git_info['changes']
        git_branch  = git_info['push_branch']
        base_url    = git_info['base_url']
        serving_url = git_info['serving_url']

        # Adding information regarding where the data came from
        headers = {'content-type'   : u'application/json',
                   'REPOSITORY_URL' : base_url,
                   'SERVING_URL'    : serving_url,
                  }

        # add data
        for add_data in data[0]:
            raw_data_from_github = self.api.get(git_url+add_data, params=git_branch)
            github_json = engine.get_github_json(raw_data_from_github)
            self.api.put(push_url+add_data, github_json, headers=headers)
        # update data
        for update_data in data[1]:
            raw_data_from_github = self.api.get(git_url+update_data, params=git_branch)
            github_json = engine.get_github_json(raw_data_from_github)
            headers['info'] = u'updated'
            self.api.put(push_url+update_data, github_json, headers=headers)
        # remove data
        for delete_data in data[2]:
            self.api.delete(push_url+delete_data)

    @view_config(route_name='root', request_method='POST')
    def default_view(self):
        """Main view, receives webhooks from github and sends to configured API."""
        # check for ENV variables
        if DEFAULTS['git_url'] == None:
            return Response(u'GITHUB_WEBHOOK_GIT_URL not set')
        if DEFAULTS['git_branch'] == None:
            return Response(u'GITHUB_WEBHOOK_GIT_BRANCH not set')
        if DEFAULTS['push_url'] == None:
            return Response(u'GITHUB_WEBHOOK_PUSH_URL not set')

        # We have all the env variables, unpack data
        git_url    = DEFAULTS['git_url']
        git_branch = DEFAULTS['git_branch']
        push_url   = DEFAULTS['push_url']

        # get data from the github event
        data = self.request.json_body

        # A dict to hold information received from github
        git_info = {}

        # Getting information from the JSON we received
        git_info['base_url']    = engine.get_base_url(data)
        git_info['serving_url'] = engine.get_serving_url(git_info['base_url'])
        git_info['author']      = engine.get_author(data)
        git_info['push_branch'] = engine.get_branch(data)
        git_info['changes']     = engine.get_changes(data)

        # Checking if the branch is right and checking if the API answers
        if git_branch == git_info['push_branch']:
            r = self.api.get(push_url)
            if r.status_code == 200:
                # Everything is OK, sending data to API
                self.send_data(git_url, push_url, git_info)
                response_msg = u'{0}\nSuccessfuly commited to {1}'.format(git_info['author'],git_branch)
            else:
                response_msg = u'Failed to connect to API\nStatus:' + str(r.status_code)
        else:
            response_msg = u'{0} wrong branch!\nYou commited to {1}.\nOnly accepting commits to {2} branch.'.format(git_info['author'], git_info['push_branch'], git_branch)
        return Response(response_msg)

@notfound_view_config(request_method='GET')
def not_found_view(self):
    return_msg = Response(u'This is a github webhook, see: <a href="https://github.com/opendesk/github-webhook">Visit Our Github</a>')
    return_msg.content_type = u'text/html'
    return return_msg
           
    
