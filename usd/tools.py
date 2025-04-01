import os

def get_highest_version(folder):
    files = os.listdir(folder)
    default = 1
    for file in files:
        print(file)
        file_name = file.split(".")[0]
        version = file_name.split("_v")[-1]
        print(version)
        if int(version) > default:
            default = int(version)
            file_path = file
    file_path = os.path.join(folder, file_path)
    return file_path, default

