import engine
import gevent
import os

import logging
logger = logging.getLogger(__name__)

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

    def push_to_api(self, push_url, url, headers):
        """Sending concurrently the URLs received for the API"""

        requests_status = {'status' : u'Ok'}

        # Unpack data
        git_url = DEFAULTS['git_url']
        git_branch = DEFAULTS['git_branch']

        # Get content from github concurrently
        request = self.api.get(git_url + git_branch + '/' + url)

        # Looking for status in request
        if (request.status_code - 300) > 0:
            logger.warn(('GET Github API failed for', request.url))
            requests_status.update({'status' : u'error'})
        requests_status.update({request.url : request.status_code})

        # Decode contents in github
        json_data = request.json()

        json_data.update({'path'   : url, 
                         'source' : headers['source'],
                         'base'   : headers['base']})

        # Removing .../path/{file.json} when posting
        patched_url = '/'.join(url.split('/')[:-1])

        # Put to API 
        request = self.api.put(push_url + '/' +''.join(patched_url), json_data, headers=headers)

        # Looking for status in request
        if (request.status_code - 300) > 0:
            logger.warn(('PUT to API failed for', request.url))
            requests_status.update({'status' : u'error'})
        requests_status.update({request.url : request.status_code})

        return requests_status

    def send_data(self, push_url, git_info):
        """This method formats and sends data to our API."""

        # Requests status dict
        list_of_status = []

        # Unpacking data
        data        = git_info['changes']
        source_url  = git_info['source_url']
        serving_url = git_info['serving_url']

        # Getting a bearer token for our API
        bearer_token = engine.get_bearer_token(push_url)

        # Adding information regarding where the data came from
        headers = {'content-type'   : u'application/json',
                   'source'         : source_url,
                   'authorization'  : u'Bearer {0}'.format(bearer_token),
                   'base'           : serving_url,
                  }

        # Added and modified concatenated
        has_changes_to_add = data[0] or data[1]
        if has_changes_to_add:
            new_changes = engine.create_async_lists_by_structure(data[0]+data[1])

            # Do the requests concurrently
            for changes in new_changes:
                # One depth at a time
                jobs = [gevent.spawn(self.push_to_api, push_url, change, headers) for change in changes]
                gevent.joinall(jobs, timeout=2)
                list_of_status = [job.value for job in jobs]
        # Delete data
        if data[2]:
            for delete_data in data[2]:
                self.api.delete(push_url+'/'+delete_data)

        return list_of_status

    @view_config(route_name='root', request_method='POST', renderer='json')
    def default_view(self):
        """Main view, receives webhooks from github and sends to configured API."""

        # check for ENV variables
        if DEFAULTS['git_url'] == None:
            self.request.response.status = '400'
            return {u'error' : u'GITHUB_WEBHOOK_GIT_URL not set'}
        if DEFAULTS['git_branch'] == None:
            self.request.response.status = '400'
            return {u'error' : u'GITHUB_WEBHOOK_GIT_BRANCH not set'}
        if DEFAULTS['push_url'] == None:
            self.request.response.status = '400'
            return {u'error' : u'GITHUB_WEBHOOK_PUSH_URL not set'}

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
                self.request.response.status = '401'
                logger.error((e, 'Invalid webhook secret key'))
                return {u'error' : u'Invalid webhook secret key'}
            else:
                if engine.validate_signature(self.request.body, secret_received) is False:
                    self.request.response.status = '401'
                    return {u'error' : u'Invalid webhook secret key'}

        # A dict to hold information received from github
        git_info = {}

        # Getting information from the JSON we received
        git_info['source_url']  = engine.get_base_url(data)
        git_info['serving_url'] = engine.get_serving_url(git_info['source_url'])
        git_info['author']      = engine.get_author(data)
        git_info['changes']     = engine.get_changes(data)

        # Checking if the branch is right and checking if the API answers
        if git_branch == engine.get_branch(data):
            # Everything is OK, trying to sending data to API
            status = self.send_data(push_url, git_info)
            # If one of the requests fails we return a 400
            if filter(lambda dict_: dict_['status'] == 'error', status):
                self.request.response.status = '400'
            return status
        else:
            response_msg = u'{0} wrong branch!\nOnly accepting commits to {1} branch.'.format(git_info['author'], git_branch)
            self.request.response.status = '403'
            return {u'error' : response_msg}

@notfound_view_config(request_method='GET')
def not_found_view(self):
    return Response(u'This is a github webhook, see: <a href="https://github.com/opendesk/github-webhook">Visit Our Github</a>')
           
    
