import os
import glob
import shutil

from .test_utils import sample_file_path
from xcproj_resources.xcproject import XcProject


def test_update_project_bundle_id():
    project = XcProject(filename=sample_file_path("Wire-iOS/Wire-iOS.xcodeproj/project.pbxproj"))

    backup_files = glob.glob(os.path.join(project.xcodeproj, '*.backup.pbxproj'))
    assert len(backup_files) == 0

    config = project.target_configuration('Wire-iOS', 'Release')
    assert config['PRODUCT_BUNDLE_IDENTIFIER'] == 'com.wearezeta.zclient.ios'
    project.set_target_configuration('Wire-iOS', 'Release', 'PRODUCT_BUNDLE_IDENTIFIER', 'com.test.dummy')
    config = project.target_configuration('Wire-iOS', 'Release')
    assert config['PRODUCT_BUNDLE_IDENTIFIER'] == 'com.test.dummy'

    project.save()

    backup_files = glob.glob(os.path.join(project.xcodeproj, '*.backup.pbxproj'))
    assert len(backup_files) == 1

    shutil.move(backup_files[0], project.filename)
    backup_files = glob.glob(os.path.join(project.xcodeproj, '*.backup.pbxproj'))
    assert len(backup_files) == 0
