import os


class JsonModel:
    def from_json(self, json_dict: dict):
        raise NotImplementedError("from_json method is not implemented")


def save_json_file(file_dir: str, file_name: str, json_string: str):
    try:
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        file = open(file_dir + file_name, 'w')
        file.write(json_string)
        file.close()
    except IOError as e:
        print(e)


def read_json_file(file_path: str) -> str:
    json_string = "[]"
    try:
        file = open(file_path, 'r', encoding='utf-8-sig')
        json_string = file.read()
        file.close()
    except IOError as e:
        print(e)
    finally:
        return json_string

