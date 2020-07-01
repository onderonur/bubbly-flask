import re
import random
import filetype
from flask_socketio import rooms, emit
from nanoid import generate
import notifications


def find_user_by_socket_id(app_users, socket_id):
    for user in app_users.values():
        user_socket_ids = user["socket_ids"]
        if socket_id in user_socket_ids:
            return user


def get_room_socket_ids(socket_ids_by_room, room_id):
    return socket_ids_by_room.get(room_id, [])


def get_room_users(socket_ids_by_room, app_users, room_id):
    socket_ids = get_room_socket_ids(socket_ids_by_room, room_id)
    users = []
    for socket_id in socket_ids:
        socket_user = find_user_by_socket_id(app_users, socket_id)
        if any(user["id"] == socket_user["id"] for user in users):
            break
        users.append(socket_user)
    return users


def is_user_already_in_room(app_users, room_id, socket_ids_by_room, joining_socket_id):
    user = find_user_by_socket_id(app_users, joining_socket_id)
    user_socket_ids = user["socket_ids"]
    other_user_socket_ids = list(
        filter(lambda socket_id: socket_id != joining_socket_id, user_socket_ids))
    if len(other_user_socket_ids) == 0:
        return False
    room_socket_ids = get_room_socket_ids(socket_ids_by_room, room_id)
    for user_socket_id in other_user_socket_ids:
        if user_socket_id in room_socket_ids:
            return True
    return False


def get_socket_room_ids():
    return rooms()


def did_user_leave_the_room_completely(app_users, socket_ids_by_room, room_id, leaving_socket_id):
    leaving_user = find_user_by_socket_id(app_users, leaving_socket_id)
    user_socket_ids = leaving_user["socket_ids"]
    # Getting user's socket ids other than the current one
    # leaving the room.
    remaining_user_socket_ids = list(
        filter(lambda socket_id: socket_id != leaving_socket_id, user_socket_ids))
    # If user has no other socket id, it means they
    # completely disconnecting.
    if(len(remaining_user_socket_ids) == 0):
        return True

    room_socket_ids = get_room_socket_ids(socket_ids_by_room, room_id)
    for user_socket_id in remaining_user_socket_ids:
        if user_socket_id in room_socket_ids:
            return False
    return True


def handle_user_leaving_the_room(app_users, socket_ids_by_room, leaving_socket_id, room_id):
    # Removing the "leaving_socket_id" from
    # the socket_id list of the room
    room_socket_ids = get_room_socket_ids(socket_ids_by_room, room_id)
    room_socket_ids = list(
        filter(lambda socket_id: socket_id != leaving_socket_id, room_socket_ids))
    socket_ids_by_room[room_id] = room_socket_ids

    socket_user = find_user_by_socket_id(app_users, leaving_socket_id)
    emit("finished typing", socket_user, room=room_id, include_self=False)

    if did_user_leave_the_room_completely(app_users, socket_ids_by_room, room_id, leaving_socket_id) == True:
        emit("left the room", socket_user, room=room_id, include_self=False)
        notifications.notify_left_the_room(room_id, socket_user["username"])


def trim_spaces(str):
    return re.sub(r'/^\s+|\s+$/g', "", str)


def is_image_file(file):
    mimetype = filetype.guess_mime(file)
    return mimetype.startswith(mimetype)


def generate_random_hex_color():
    random_number = random.randint(0, 16777215)
    hex_number = str(hex(random_number))
    hex_number = '#' + hex_number[2:]
    return hex_number


def create_new_user(socket_id):
    user = {
        "id": generate(),
        "username": "User-" + generate(size=6),
        "socket_ids": [socket_id],
        "color": generate_random_hex_color()
    }
    return user
