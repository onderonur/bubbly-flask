from flask_socketio import emit


def notify(room_id, notification):
    emit("notification", notification, room=room_id, include_self=False)


def notify_joined_to_room(room_id, username):
    notify(room_id, username + " has joined to the conversation.")


def notify_left_the_room(room_id, username):
    notify(room_id, username + " has left the conversation.")


def notify_edited_username(room_id, old_username, new_username):
    notify(room_id, old_username + " has changed their name as " + new_username)


def notify_edited_color(room_id, username, new_color):
    notify(room_id, username + " has changed their color as " + new_color)
