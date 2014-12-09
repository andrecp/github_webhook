import requests

class RESTAPIService:
    """REST API Service"""
    def get(self, url, params=None):
        return requests.get(url, params=params)
    def post(self, url, data):
        return requests.post(url, json=data)
    def put(self, url, data, headers=None):
        if headers is None:
            return requests.put(url, json=data)
        else:
            return requests.put(url, json=data, headers=headers)
    def delete(self, url):
        return requests.delete(url)
