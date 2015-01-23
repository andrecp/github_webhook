import engine
import gevent
import os

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import notfound_view_config
from restapi import RESTAPIService

DEFAULTS = {
    'git_url'         : os.environ.get('GITHUB_WEBHOOK_GIT_URL'),
    'git_branch'      : os.environ.get('GITHUB_WEBHOOK_GIT_BRANCH'),
    'push_url'        : os.environ.get('GITHUB_WEBHOOK_opendesk_collection__API_URL'),
    'use_github_auth' : os.environ.get('GITHUB_WEBHOOK_GIT_USE_AUTH'),
    'env_true_values' : ['1', 'True', 'true'],
}

class RootView(object):
    def __init__(self, request, api_service=None):
        self.request = request
        if api_service is None:
            self.api = RESTAPIService()
        else:
            self.api = api_service

    def _push_to_api(self, push_url, url_list, headers):
        """"""

        # Unpack data
        git_url = DEFAULTS['git_url']
        git_branch = DEFAULTS['git_branch']

        # Get content from github concurrently
        requests =  self.api.get(git_url, urls=url_list, params=git_branch)

        # Decode contents concurrently with Gevent
        jobs = [gevent.spawn(engine.get_github_json, r) for r in requests]
        gevent.joinall(jobs, timeout=2)

        json_list = [job.value for job in jobs]
        
        # Put to API concurrently 
        self.api.put(push_url, url_list, json_list, headers=headers)

    def send_data(self, push_url, git_info):
        """This method formats and sends data to our API."""

        # Unpacking data
        data        = git_info['changes']
        base_url    = git_info['base_url']
        serving_url = git_info['serving_url']

        # Getting a bearer token for our API
        bearer_token = engine.get_bearer_token(push_url)

        # Adding information regarding where the data came from
        headers = {'content-type'   : u'application/json',
                   'repository_url' : base_url,
                   'authorization'  : bearer_token,
                   'serving_url'    : serving_url,
                  }
        # Add Data
        if data[0]:
            add_urls = engine.create_async_lists_by_structure(data[0])
            self._push_to_api(push_url, add_urls, headers)
        # Update data
        if data[1]:
            update_urls = engine.create_async_lists_by_structure(data[1])
            headers['info'] = u'updated'
            self._push_to_api(push_url, update_urls, headers)
        # Delete data
        if data[2]:
            for delete_data in data[2]:
                self.api.delete(push_url+delete_data)

    @view_config(route_name='root', request_method='POST')
    def default_view(self):
        """Main view, receives webhooks from github and sends to configured API."""

        # check for ENV variables
        if DEFAULTS['git_url'] == None:
            return Response(u'GITHUB_WEBHOOK_GIT_URL not set', status=400)
        if DEFAULTS['git_branch'] == None:
            return Response(u'GITHUB_WEBHOOK_GIT_BRANCH not set', status=400)
        if DEFAULTS['push_url'] == None:
            return Response(u'GITHUB_WEBHOOK_PUSH_URL not set', status=400)

        # We have all the env variables, unpack data
        git_branch      = DEFAULTS['git_branch']
        push_url        = DEFAULTS['push_url']
        use_github_auth = DEFAULTS['use_github_auth']
        env_true_values = DEFAULTS['env_true_values']

        # get data from the github event
        data = self.request.json_body

        # Validate the webhook secret key if is a secured webhook
        if use_github_auth in env_true_values:
            try:
                secret_received = self.request.headers['x-hub-signature']
            except KeyError, e:
                print e
                return Response(u'Invalid webhook secret key', status=401)
            else:
                if engine.validate_signature(self.request.body, secret_received) is False:
                    return Response(u'Invalid webhook secret key', status=401)


        # A dict to hold information received from github
        git_info = {}

        # Getting information from the JSON we received
        git_info['base_url']    = engine.get_base_url(data)
        git_info['serving_url'] = engine.get_serving_url(git_info['base_url'])
        git_info['author']      = engine.get_author(data)
        git_info['changes']     = engine.get_changes(data)

        # Checking if the branch is right and checking if the API answers
        if git_branch == engine.get_branch(data):
            r = self.api.get(push_url)
            if r.status_code == 200:
                # Everything is OK, sending data to API
                self.send_data(push_url, git_info)
                return Response(u'{0}\nSuccessfuly commited to {1}'.format(git_info['author'],git_branch))
            else:
                return Response(u'Failed to connect to API\nStatus:' + str(r.status_code), status=504)
        else:
            response_msg = u'{0} wrong branch!\nOnly accepting commits to {1} branch.'.format(git_info['author'], git_branch)
            return Response(response_msg, status=403)

@notfound_view_config(request_method='GET')
def not_found_view(self):
    return Response(u'This is a github webhook, see: <a href="https://github.com/opendesk/github-webhook">Visit Our Github</a>')
           
    
