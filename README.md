github_webhook
==============
# Intro
This is a github webhook under development. 

The goal is to have a database represented as JSON documents and managed through github. The github_webhook listens to push events at a github repository and sends the modifications to a webservice hosting the database.

# Using
First set some env variables:

Edit startmeup.sh and then
```
source startmeup.sh
```

or

```
export GITHUB_WEBHOOK_GIT_URL = repo to look for
export GITHUB_WEBHOOK_GIT_BRANCH = branch to accept requests from (ex: master)
export GITHUB_WEBHOOK_GIT_PUSH_URL = URL to push modifications to (ex: https://random.firebaseio.com)
```
Then install Pyramid requirements:

```
$VENV/bin/python setup.py develop
```
And start the server:

```
$VENV/bin/pserve development.ini
```

# Testing
### Unittesting
```
source startmeup.sh
$VENV/nosetests -v tests
```

### Manual testing
Using HTTPie at command line:

```
http POST http://127.0.0.1:6547 < testing_commits/body.json
```
```
http POST http://127.0.0.1:6547 < testing_commits/body_another_branch.json
```

There a few examples of JSONs comming from github at testing_commits folder, if you want to create more using requestb.in service:

Setting webhook to callback to your requestb.in
```
curl -u "USERNAME" -i   https://api.github.com/hub   -F "hub.mode=subscribe"   -F "hub.topic=https://github.com/REPO/PATH/events/push.json"   -F "hub.callback=PATH/TO/YOUR/REUESTB.IN"
```
