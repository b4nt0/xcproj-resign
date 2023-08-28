import os


def relative_to_absolute_path(relative_path: str, reference_directory: str = None) -> str:
    if reference_directory is None:
        reference_directory = os.getcwd()

    reference_absolute_path = os.path.abspath(reference_directory)
    absolute_path = os.path.normpath(os.path.join(reference_absolute_path, relative_path))

    return absolute_path
