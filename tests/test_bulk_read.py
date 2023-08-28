from tests.test_utils import sample_file_path
from xcproj_resources.xcproject import XcProject


def test_read_project_settings_rendered():
    project = XcProject(filename=sample_file_path("Wire-iOS/Wire-iOS.xcodeproj/project.pbxproj"))
    targets = project.targets

    for target in targets:
        configurations = project.target_configurations(target.name)
        for configuration in configurations:
            config = project.target_configuration(target.name, configuration.name)
            assert config['PRODUCT_BUNDLE_IDENTIFIER'].startswith('com.wearezeta.')

            entitlements = project.target_entitlements(target.name, configuration.name)
            assert entitlements is not None
