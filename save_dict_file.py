import json
import io
import json

def save_config_to_json(config_data: dict) -> io.BytesIO:
    """
    Serializes a dictionary into a BytesIO object.
    
    Args:
        d (dict): The dictionary to serialize.
    
    Returns:
        io.BytesIO: A byte stream containing the serialized dictionary.
    """
    json_str = json.dumps(config_data, indent=4, sort_keys=True)
    byte_stream = io.BytesIO(json_str.encode('utf-8'))
    return byte_stream

# Example usage
data = {"name": "Alice", "age": 25, "city": "New York"}
byte_stream = save_config_to_json(data)

# Writing to a file outside the function
with open("output.json", "wb") as file:
    file.write(byte_stream.getvalue())

