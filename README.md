[![Build Status](https://travis-ci.org/daniego/matrix_ansible_tower_bot.svg?branch=master)](https://travis-ci.org/daniego/matrix_ansible_tower_bot)

# matrix_ansible_tower_bot

This is a bot that receives messages from pingdom and sends it to matrix

# Settings
Depending on your environment set:
- `.docker_env` based on `.docker_env_sample` if you run via docker compose
- exporting the environment variables if you run it from source

# ENV definition
```
MATRIX_SERVER=https://matrix.example.org
MATRIX_TOKEN=matrix_token
ACCESS_TOKENS={ 'Identifier name': 'thisISaSAMPLEtoken', 'Identifier name2': 'abc',}
MATRIX_ROOMS={ 'test_room': '!room_id:example.org', 'test_room2': '!room_id2:example.org',}
LOG_LEVEL=DEBUG
debug_enabled=False
```

# Pingdom setup
Set the webhook to your instance

Example: `https://matrix.example.org/ansible?token=thisISaSAMPLEtoken&room=test_room`

# Home server integration via nginx
Add your nginx or whatever is your termination an ACL that forwards the request to the bot

nginx example:
```
server {
  ...

  location /ansible {
    proxy_pass        http://127.0.0.1:8090;
    proxy_redirect    off;
    proxy_set_header  X-Real-IP        $remote_addr;
    proxy_set_header  X-Forwarded-For  $proxy_add_x_forwarded_for;
    proxy_set_header  Host             $http_host;

    client_body_buffer_size 1M;
    client_max_body_size 1M;
  }

}
```
# Usage
Docker environment
------------------
Create the .docker_env file based on .docker_env_sample and run the composer
```
git clone https://github.com/daniego/matrix_ansible_tower_bot.git
cd matrix_ansible_tower_bot
cp .docker_env_sample .docker_env
vi .docker_env
# and customize your settings
docker-compose pull && docker-compose up -d
```
From source
-----------
```
python3 -m venv ~/.venv/matrix_ansible_tower_bot
source ~/.venv/matrix_ansible_tower_bot/bin/activate
git clone git@github.com:daniego/matrix_ansible_tower_bot.git
cd matrix_ansible_tower_bot
pip install -r requirements.txt
python matrix_ansible_tower_bot/matrix_ansible_tower_bot.py
```
From pypi packege
-----------
Coming soon

# Tests
This is a quick and dirty way to test that all ansible payloads
```
for payload in $(ls ansible_samples); do curl -XPOST -d "@ansible_samples/${payload}" -H "Content-Type: application/json" 127.0.0.1:8090?token=abc\&room=test_room; done
```

# ToDo
- Unit tests
- Fill doc string
- Set timeout on 'send_message_event'
- auto join room

# Contributions
Feel free to fork, create a branch and send a PR
