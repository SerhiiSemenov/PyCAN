import cantools

def get_all_messages(can_db):
    messagess_name = set()
    for name in can_db._name_to_message:
        messagess_name.add(name)
    return messagess_name

def get_message_by_id(can_db):
    return can_db._frame_id_to_message[frame_id]