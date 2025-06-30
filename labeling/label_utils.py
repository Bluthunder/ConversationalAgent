def get_text_from_message(message_block, role='user'):
    for m in message_block.get("messages", []):
        if m.get("role") == role:
            return m.get("content", "")
    return ""

def add_label(convo, key, value):
    convo[key] = value
    return convo

def flatten_messages(messages):
    """Combine user and assistant messages into a single string."""
    try:
        return {
            "message": " ".join([msg["content"] for msg in messages["messages"]])
        }
    except Exception as e:
        return {"message": ""}
    


def flatten_user_messages(data):
    """
    Flatten the list of user-assistant chat exchanges for labeling.

    Args:
        data (list): List of dicts with a 'messages' key.

    Returns:
        user_inputs (list): List of dicts with a 'message' key.
        index_map (list): Indices to trace back the original position.
    """
    user_inputs = []
    index_map = []

    for idx, row in enumerate(data):
        flattened = flatten_messages(row)
        if flattened["message"]:  # Avoid appending empty ones
            user_inputs.append(flattened)
            index_map.append(idx)

    return user_inputs, index_map
    
