import os
import sys


def sample_file_path(file_name: str) -> str:
    sys_path = sys.path[0]
    sys_path_components = sys_path.split('/')
    file_name_components = os.path.join('tests/data', file_name).split('/')

    for i in range(len(sys_path_components) - 1, 0, -1):
        p = sys_path_components[i]
        if len(file_name_components) > 0 and p in file_name_components:
            file_name_components.remove(p)
        else:
            break

    full_path_components = sys_path_components + file_name_components
    full_path = '/'.join(full_path_components)
    return full_path
