github_webhook
==============
# Intro
playing around with github webhooks and Pyramid.

# Develop
$VENV/bin/python setup.py develop

$VENV/bin/pserve development.ini
# Testing
Setting webhook to callback to your requestb.in
```
curl -u "USERNAME" -i   https://api.github.com/hub   -F "hub.mode=subscribe"   -F "hub.topic=https://github.com/REPO/PATH/events/push.json"   -F "hub.callback=PATH/TO/YOUR/REUESTB.IN"
```
At command line:

```
http POST http://127.0.0.1:6547 < testing_commits/body.json
```
