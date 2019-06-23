'''
Text
'''
import json
import ast
from matrix_client.api import MatrixHttpApi, MatrixRequestError
from flask import Flask, render_template, request
from flask.logging import create_logger
import settings

app = Flask(__name__)
LOG = create_logger(app)
LOG.setLevel(settings.LOG_LEVEL)

LOG.info('Matrix server: %s', settings.MATRIX_SERVER)
LOG.info('Matrix rooms: %s', settings.MATRIX_ROOMS)


def validate_token(token):
    '''
    validate_token function
    '''
    if token in settings.ACCESS_TOKENS.values():
        return True
    return False


def validate_room(room):
    '''
    validate_room function
    '''

    if room in settings.MATRIX_ROOMS.keys():
        return settings.MATRIX_ROOMS[room]
    return False


def send_message(matrix_room, message_plain, message):
    '''
    One day
    '''
    # Init matrix API
    matrix = MatrixHttpApi(settings.MATRIX_SERVER, token=settings.MATRIX_TOKEN)

    try:
        response = matrix.send_message_event(
            room_id=matrix_room,
            event_type="m.room.message",
            content={
                "msgtype": "m.text",
                "format": "org.matrix.custom.html",
                "body": message_plain,
                "formatted_body": message,
            }
        )
    except MatrixRequestError as ex:
        LOG.error('send_message_event failure %s', ex)
        return json.dumps({'success': False}), 417, {'ContentType': 'application/json'}

    LOG.debug('Matrix Response: %s', response)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


def update_name(ansible_tower_payload):
    '''
    One day
    '''
    try:
        key = ansible_tower_payload['name']
        return key
    except KeyError:
        return ""


def prepare_message(matrix_room):
    '''
    One day
    '''
    ansible_tower_payload = request.json
    status = ansible_tower_payload.get('status', 'none')

    if 'failed' in status:
        ansible_tower_payload.update({"state": "failed",
                                      "color": "#ff0000",
                                      "name": update_name(ansible_tower_payload)})
    elif 'successful' in status:
        ansible_tower_payload.update({"state": "successful",
                                      "color": "#33cc33",
                                      "name": update_name(ansible_tower_payload)})
    else:
        ansible_tower_payload.update({"color": "#0056e2",
                                      "friendly_name": "unrecognized payload",
                                      "name": update_name(ansible_tower_payload),
                                      "status": ""})
        LOG.info('Got and unrecognized status')

    message_plain = "Ansible Tower {friendly_name} {name} {status}".format(**ansible_tower_payload)
    message = render_template('message.html.j2', ansible_tower_payload=ansible_tower_payload)

    return send_message(matrix_room, message_plain, message)


# Normalizing dictionary when comes from an environment variable
if isinstance(settings.ACCESS_TOKENS, str):
    ACCESS_TOKENS = ast.literal_eval(settings.ACCESS_TOKENS)
else:
    ACCESS_TOKENS = settings.ACCESS_TOKENS

# Normalizing dictionary when comes from an environment variable
if isinstance(settings.MATRIX_ROOMS, str):
    MATRIX_ROOMS = ast.literal_eval(settings.MATRIX_ROOMS)
else:
    MATRIX_ROOMS = settings.MATRIX_ROOMS


@app.route("/", methods=['GET', 'POST'])
def main_route():
    '''
    Other
    '''

    # Validating token
    token = request.args.get('token')
    if token:
        is_valid_token = validate_token(token)

        if not is_valid_token:
            return json.dumps({'success': False, 'reason': 'token not valid'}), 403, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False, 'reason': 'token not provided'}), 403, {'ContentType': 'application/json'}

    # Validating room
    room = request.args.get('room')

    if room:
        matrix_room = validate_room(room)

        if not matrix_room:
            return json.dumps({'success': False, 'reason': 'room not valid'}), 403, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False, 'reason': 'room not provided'}), 403, {'ContentType': 'application/json'}

    if request.method == 'POST':

        return prepare_message(matrix_room)

    return json.dumps({'success': False}), 405, {'ContentType': 'application/json'}


if __name__ == "__main__":
    app.run(host='0.0.0.0',
            port=8090,
            debug=settings.debug_enabled,
            threaded=True)
