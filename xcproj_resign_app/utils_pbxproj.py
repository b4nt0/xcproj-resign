import os

from pbxproj import PBXFileReference, PBXGroup


def get_full_pbx_file_reference_path(node: PBXFileReference or PBXGroup) -> str:
    if node is None:
        return ''

    result = getattr(node, 'path', getattr(node, 'name', None))
    if result is None:
        return ''

    node_id = node.get_id()
    parent = node.get_parent()

    for group in parent.get_objects_in_section('PBXGroup'):
        if node_id in group.children:
            parent_path = get_full_pbx_file_reference_path(group)
            if parent_path is not None and parent_path != '':
                result = os.path.join(parent_path, result)
            break

    return result
