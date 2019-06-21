FROM python:3.6-slim

ENV DEBIAN_FRONTEND noninteractive

COPY ["requirements.txt", "/srv/matrix_ansible_tower_bot/"]
WORKDIR /srv/matrix_ansible_tower_bot/matrix_ansible_tower_bot
RUN python3 -m venv /opt/matrix_ansible_tower_bot && \
    /opt/matrix_ansible_tower_bot/bin/pip install --upgrade pip && \
    /opt/matrix_ansible_tower_bot/bin/pip install -r /srv/matrix_ansible_tower_bot/requirements.txt && \
#
    apt-get update && \
    apt-get install --no-install-recommends -y \
      nginx \
      curl && \
#
    rm -f /etc/nginx/sites-enabled/default && \
#
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/* && \
#
    echo "source /opt/matrix_ansible_tower_bot/bin/activate" >> /root/.bashrc && \
    echo 'PS1="\u@\h::\W# "' >> ~/.bashrc

COPY container_fs /
COPY ["matrix_ansible_tower_bot", "/srv/matrix_ansible_tower_bot/matrix_ansible_tower_bot"]

ENTRYPOINT ["/opt/matrix_ansible_tower_bot/bin/supervisord", "-c", "/etc/supervisord.conf", "-n"]
