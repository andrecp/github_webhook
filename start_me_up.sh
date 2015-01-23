export VENV=../venv/bin
export GITHUB_WEBHOOK_GIT_URL=https://api.github.com/repos/opendesk/collection/contents/
export GITHUB_WEBHOOK_GIT_BRANCH=master
# export GITHUB_WEBHOOK_WEBHOOK_WHITELIST=".json;files;"
export GITHUB_WEBHOOK_WHITELIST="product.json;fileset.json"
export GITHUB_WEBHOOK_BLACKLIST="_"
# get from github anything else that doesnt start with an _"
export GITHUB_WEBHOOK_GIT_USE_AUTH=false
# WIP
export GITHUB_WEBHOOK_opendesk_collection__API_URL=https://fiery-inferno-4391.firebaseio.com/desks/
export GITHUB_WEBHOOK_opendesk_collection__SECRET_TOKEN=test