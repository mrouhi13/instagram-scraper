import os


def file_repetition_count(base_name, target_dir):
    i = 0
    for file in os.listdir(target_dir):
        if file.startswith(base_name):
            file_name, _ = file.split('.jpg')
            i = int(file_name.split('_')[-1])

    return i + 1


def generate_file_name(name, target_dir):
    base_name = name.replace(' ', '_').lower()
    i = file_repetition_count(base_name, target_dir)
    file_name = f'{base_name}_{i}.jpg'
    return file_name
