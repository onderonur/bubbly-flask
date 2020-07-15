import os
from flask import Flask, request, session, send_from_directory, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
from nanoid import generate
from time import time
import utils
import notifications
import jwt
import datetime

# TODO: Compared to the Node.js version, Flask implementation of Bubbly API has some missing points.
# When a user edits their info, Node.js version emits to all the rooms the user is connected to.
# But this version just emits to only one room.
# It may be implemented in the future, but in Flask-SocketIO obtaining info of sockets/rooms
# is a little bit more complex than the Node.js version.

jwt_secret_key = 'veryverysecret'

app = Flask(__name__, static_folder="../client/build")
app.config["SECRET_KEY"] = "secret!"

themed_rooms = [
    {"title": 'Random Chat', "slug": 'random-chat'},
    {"title": 'Music', "slug": 'music'},
    {"title": 'Movies', "slug": 'movies'},
    {"title": 'Comics', "slug": 'comics'},
    {"title": 'Games', "slug": 'games'},
    {"title": 'Books', "slug": 'books'},
    {"title": 'Anime & Manga', "slug": 'anime-and-manga'},
    {"title": 'Arts & Creativity', "slug": 'arts-and-creativity'},
    {"title": 'Technology', "slug": 'technology'},
]


@app.route("/api/rooms/themed")
def themed_rooms_list():
    return jsonify(themed_rooms)


socketio = SocketIO(app, cors_allowed_origins="*")

app_users = {}

socket_ids_by_room = {}


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
# Serve React App
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@socketio.on("connect")
def handle_connect():
    token = request.args.get("token", None)
    socket_id = request.sid
    user = None
    try:
        if token:
            decoded_token = jwt.decode(token, jwt_secret_key)
            id = decoded_token["id"]
            user = app_users[id]
            if user == None:
                raise Exception("User not found")
            else:
                user["socket_ids"].append(socket_id)
        else:
            raise Exception("Token not found")
    except:
        user = utils.create_new_user(socket_id)

    app_users[user["id"]] = user

    session["current_user"] = user


@socketio.on("who am i")
def handle_who_am_i():
    user = session["current_user"]
    token = jwt.encode({
        "id": user["id"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(weeks=1)
    }, jwt_secret_key)
    # Converting the token into a string
    token = token.decode('UTF-8')
    return user, token


@socketio.on("create room")
def handle_create_room():
    room_id = generate()
    return room_id


@socketio.on('join room')
def handle_my_custom_event(room_id):
    join_room(room_id)
    socket_id = request.sid
    if room_id in socket_ids_by_room:
        socket_ids_by_room[room_id].append(socket_id)
    else:
        socket_ids_by_room[room_id] = [socket_id]

    if utils.is_user_already_in_room(app_users, room_id, socket_ids_by_room, socket_id) == False:
        current_user = session["current_user"]
        emit("joined to room", current_user, room=room_id)
        notifications.notify_joined_to_room(room_id, current_user["username"])

    room_users = utils.get_room_users(socket_ids_by_room, app_users, room_id)
    return room_users


@socketio.on("leave room")
def handle_leave_room(room_id):
    leave_room(room_id)
    socket_id = request.sid
    utils.handle_user_leaving_the_room(
        app_users, socket_ids_by_room, socket_id, room_id)


@socketio.on("chat message")
def handle_chat_message(room_id, message_input):
    trimmed_body = message_input["body"]
    if trimmed_body:
        trimmed_body = utils.trim_spaces(trimmed_body)

    file = message_input["file"]
    if not trimmed_body and not file:
        return

    if file:
        is_image = utils.is_image_file(file)
        if not is_image:
            return

    current_user = session["current_user"]

    message = {
        "id": generate(),
        "author": current_user,
        "body": trimmed_body,
        "file": file,
        "timestamp": time() * 1000
    }
    emit("chat message", message, room=room_id, include_self=False)
    return message


@socketio.on("started typing")
def handle_started_typing(room_id, user_id):
    current_user = session["current_user"]
    emit("started typing", current_user, room=room_id, include_self=False)


@socketio.on("finished typing")
def handle_finished_typing(room_id, user_id):
    current_user = session["current_user"]
    emit("finished typing", current_user, room=room_id, include_self=False)


@socketio.on("edit user")
def handle_edit_user(room_id, user_input):
    edited_user = session["current_user"]
    if edited_user:
        new_username = user_input["username"]
        if new_username:
            old_username = edited_user["username"]
            new_username = utils.trim_spaces(new_username)
            if new_username and old_username != new_username:
                edited_user["username"] = new_username
                notifications.notify_edited_username(
                    room_id, old_username, new_username)

        new_color = user_input["color"]
        if new_color:
            old_color = edited_user["color"]
            if old_color != new_color:
                edited_user["color"] = new_color
                notifications.notify_edited_color(
                    room_id, edited_user["username"], new_color)

        session["current_user"] = edited_user
        app_users[edited_user["id"]] = edited_user
        emit("edit user", edited_user, room=room_id)


@socketio.on("disconnect")
def handle_disconnect():
    room_ids = utils.get_socket_room_ids()
    leaving_socket_id = request.sid
    for room_id in room_ids:
        utils.handle_user_leaving_the_room(
            app_users, socket_ids_by_room, leaving_socket_id, room_id)
    current_user = session["current_user"]
    current_user_socket_ids = current_user["socket_ids"]
    current_user["socket_ids"] = [
        socket_id for socket_id in current_user_socket_ids if socket_id != leaving_socket_id]

    app_users[current_user["id"]] = current_user


if __name__ == '__main__':
    socketio.run(app, port=8080)
