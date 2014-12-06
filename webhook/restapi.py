import requests

class RESTAPIService:
    """REST API Service"""
    def get(self, url, params=None):
        return requests.get(url, params=params)
    def post(self, url, data):
        return requests.post(url, json=data)
    def put(self, url,data):
        return requests.put(url, json=data)
    def delete(self, url):
        return requests.delete(url)
