import os


def save_json_file(file_dir: str, file_name: str, json_string: str):
    try:
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        file = open(file_dir + file_name, 'w')
        file.write(json_string)
        file.close()
    except IOError as e:
        print(e)


def read_json_file(file_path: str):
    json_string = "[]"
    try:
        file = open(file_path, 'r')
        json_string = file.read()
        file.read()
        file.close()
    except IOError as e:
        print(e)
    finally:
        return json_string

