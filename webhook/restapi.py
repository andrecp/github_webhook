import requests
import grequests as async

class RESTAPIService:
    """REST API Service"""
    def get(self, base_url, urls=None, params=None):
        if urls:
            r = [async.get(base_url + ''.join(url), params=params) for url in urls]
            return async.map(r)
        else:
            return requests.get(base_url, params=params)
    def post(self, base_url, urls, data):
        return async.map([async.post(base_url + ''.join(url), json=data) for url in urls])
    def put(self, base_url, urls, json_container, headers=None):
        if headers is None:
            return async.map([async.put(base_url + ''.join(url), json=json_) 
                                for json_, url in zip(json_container, urls)])
        else:
            return async.map([async.put(base_url + ''.join(url), json=json_, headers=headers) 
                                for json_, url in zip(json_container, urls)])
    def delete(self, base_url, url):
        return requests.delete(base_url + url)