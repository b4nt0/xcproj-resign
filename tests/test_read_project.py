import os

from pbxproj import XcodeProject, PBXGenericObject, PBXNativeTarget, XCConfigurationList, XCBuildConfiguration, \
    PBXFileReference
from pbxproj.PBXKey import PBXKey

from test_utils import sample_file_path

from xcproj_resources.utils_pbxproj import get_full_pbx_file_reference_path
from xcproj_resources.xcconfig import XcConfig
from xcproj_resources.xcproject import XcProject


def test_read_project():
    project = XcodeProject.load(sample_file_path("Wire-iOS/Wire-iOS.xcodeproj/project.pbxproj"))
    assert project is not None

    assert isinstance(project.rootObject, PBXKey)

    root = project.objects[project.rootObject]
    assert root is not None
    assert isinstance(root, PBXGenericObject)
    assert len(root.targets) == 5

    wire_ios_key = root.targets[0]
    assert isinstance(wire_ios_key, PBXKey)

    wire_ios = project.objects[wire_ios_key]
    assert isinstance(wire_ios, PBXNativeTarget)

    wire_ios_configurations_key = wire_ios.buildConfigurationList
    assert isinstance(wire_ios_configurations_key, PBXKey)

    wire_ios_configurations = project.objects[wire_ios_configurations_key]
    assert isinstance(wire_ios_configurations, XCConfigurationList)
    assert len(wire_ios_configurations.buildConfigurations) == 2

    wire_os_debug_configuration_key = wire_ios_configurations.buildConfigurations[0]
    assert isinstance(wire_os_debug_configuration_key, PBXKey)
    assert wire_os_debug_configuration_key._get_comment() == 'Debug'

    wire_os_debug_configuration = project.objects[wire_os_debug_configuration_key]
    assert isinstance(wire_os_debug_configuration, XCBuildConfiguration)
    assert isinstance(wire_os_debug_configuration.buildSettings, PBXGenericObject)
    assert wire_os_debug_configuration.buildSettings['ALWAYS_EMBED_SWIFT_STANDARD_LIBRARIES'] == 'YES'

    assert wire_os_debug_configuration.buildSettings['__TEST_NON_EXISTING_OPTION'] is None
    wire_os_debug_configuration.buildSettings['__TEST_NON_EXISTING_OPTION'] = '123'
    assert wire_os_debug_configuration.buildSettings['__TEST_NON_EXISTING_OPTION'] == '123'


def test_read_target_settings():
    project = XcodeProject.load(sample_file_path("Wire-iOS/Wire-iOS.xcodeproj/project.pbxproj"))
    assert project is not None

    targets = project.objects.get_targets(None)
    wire_ios_target = next(filter(lambda x: x.name == 'Wire-iOS', targets))

    assert wire_ios_target.name == 'Wire-iOS'
    assert wire_ios_target.productName == 'ZClient iOS'
    print(wire_ios_target)

    wire_ios_configurations = project.objects[wire_ios_target.buildConfigurationList]
    assert isinstance(wire_ios_configurations, XCConfigurationList)

    wire_ios_release_configuration = project.objects[next(filter(lambda c: c._get_comment() == 'Release', wire_ios_configurations.buildConfigurations))]
    assert isinstance(wire_ios_release_configuration, XCBuildConfiguration)

    wire_ios_release_base_configuration = project.objects[wire_ios_release_configuration.baseConfigurationReference]
    assert isinstance(wire_ios_release_base_configuration, PBXFileReference)

    full_config_path = get_full_pbx_file_reference_path(wire_ios_release_base_configuration)
    assert full_config_path == 'Wire-iOS/Resources/Configuration/Wire-iOS/Wire-iOS-Release.xcconfig'

    config = XcConfig(filename=sample_file_path(os.path.join('Wire-iOS', full_config_path)))
    assert len(config.values) == 100
    assert config.values['PRODUCT_BUNDLE_IDENTIFIER'] == 'com.wearezeta.zclient.ios'
    assert config.values['CODE_SIGN_ENTITLEMENTS'] == 'Wire-iOS/Entitlements-Prod.entitlements'


def test_read_project_settings_rendered():
    project = XcProject(filename=sample_file_path("Wire-iOS/Wire-iOS.xcodeproj/project.pbxproj"))
    config = project.target_configuration('Wire-iOS', 'Release')
    assert config['PRODUCT_BUNDLE_IDENTIFIER'] == 'com.wearezeta.zclient.ios'
    assert config['CODE_SIGN_ENTITLEMENTS'] == 'Wire-iOS/Entitlements-Prod.entitlements'
    entitlements = project.target_entitlements('Wire-iOS', 'Release')
    assert len(entitlements) == 10
    assert entitlements['com.apple.developer.ubiquity-kvstore-identifier'] == '$(TeamIdentifierPrefix)$(CFBundleIdentifier)'


def test_refer_to_xcodeproj():
    project = XcProject(filename=sample_file_path("Wire-iOS/Wire-iOS.xcodeproj"))
    config = project.target_configuration('Wire-iOS', 'Release')
    assert config['PRODUCT_BUNDLE_IDENTIFIER'] == 'com.wearezeta.zclient.ios'


def test_set_configuration_setting():
    project = XcProject(filename=sample_file_path("Wire-iOS/Wire-iOS.xcodeproj/project.pbxproj"))
    config = project.target_configuration('Wire-iOS', 'Release')
    assert config['PRODUCT_BUNDLE_IDENTIFIER'] == 'com.wearezeta.zclient.ios'
    project.set_target_configuration('Wire-iOS', 'Release', 'PRODUCT_BUNDLE_IDENTIFIER', 'com.test.dummy')
    config = project.target_configuration('Wire-iOS', 'Release')
    assert config['PRODUCT_BUNDLE_IDENTIFIER'] == 'com.test.dummy'
