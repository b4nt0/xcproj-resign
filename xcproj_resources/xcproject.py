import os.path
import plistlib
from typing import List, Dict

from pbxproj import XcodeProject, PBXGenericTarget, PBXGenericObject, XCBuildConfiguration

from xcproj_resources.utils_path import relative_to_absolute_path
from xcproj_resources.utils_pbxproj import get_full_pbx_file_reference_path
from xcproj_resources.xcconfig import XcConfig


class XcProject:
    def __init__(self, **kwargs):
        super(XcProject, self).__init__()

        self.project = None

        self.filename = kwargs.pop('filename', None)
        if self.filename is not None:
            self.load()

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, value: str):
        if value.endswith('.xcodeproj'):
            value = os.path.join(value, 'project.pbxproj')

        self._filename = value
        file_path = os.path.dirname(self._filename)
        self.project_directory = relative_to_absolute_path('..', file_path)

    @property
    def project(self) -> XcodeProject:
        if self._project is not None:
            return self._project
        raise ValueError('Project is not loaded yet')

    @project.setter
    def project(self, value):
        self._project = value

    def load(self, filename: str = None):
        if filename is None:
            filename = self.filename
        else:
            self.filename = filename

        self.project = XcodeProject.load(filename)

    @property
    def objects(self):
        return self.project.objects

    @property
    def targets(self) -> List[PBXGenericTarget]:
        return self.project.objects.get_targets(None)

    def project_file_path(self, relative_path: str) -> str:
        return relative_to_absolute_path(relative_path, self.project_directory)

    def target_configurations(self, target_name: str) -> List[XCBuildConfiguration]:
        target = next(filter(lambda x: x.name == target_name, self.targets))
        result = list()

        if target.buildConfigurationList is None:
            return result

        configurations = self.objects[target.buildConfigurationList]
        for configuration in configurations.buildConfigurations:
            config = self.objects[configuration]
            result.append(config)

        return result

    def target_configuration(self, target_name: str, configuration_name: str = 'Release') -> Dict[str, str]:
        target = next(filter(lambda x: x.name == target_name, self.targets))
        configurations = self.project.objects[target.buildConfigurationList]
        configuration = self.project.objects[next(filter(lambda c: c._get_comment() == configuration_name, configurations.buildConfigurations))]

        result = dict()

        # Load a base configuration
        if configuration.baseConfigurationReference is not None:
            configuration_file_reference = self.project.objects[configuration.baseConfigurationReference]
            configuration_file_path = get_full_pbx_file_reference_path(configuration_file_reference)
            full_configuration_file_path = self.project_file_path(configuration_file_path)
            base_configuration = XcConfig(filename=full_configuration_file_path)
            result = base_configuration.values.copy()

        # Get configuration values and render variables
        settings: PBXGenericObject = configuration.buildSettings
        for setting_key in settings.get_keys():
            setting = settings[setting_key]
            if isinstance(setting, list):
                result[setting_key] = list()
                for el in setting:
                    result[setting_key].append(XcConfig.render_variables_from(el, result))
            else:
                result[setting_key] = XcConfig.render_variables_from(setting, result)

        return result

    def set_target_configuration(self, target_name: str, configuration_name: str, key: str, value: str):
        target = next(filter(lambda x: x.name == target_name, self.targets))
        configurations = self.project.objects[target.buildConfigurationList]
        configuration = self.project.objects[next(filter(lambda c: c._get_comment() == configuration_name, configurations.buildConfigurations))]
        configuration.buildSettings[key] = value

    def target_entitlements(self, target_name: str, configuration_name: str = 'Release') -> Dict[str, str]:
        config = self.target_configuration(target_name, configuration_name)
        entitlements_file = config.get('CODE_SIGN_ENTITLEMENTS', None)
        if entitlements_file is None:
            return dict()

        ef = open(self.project_file_path(entitlements_file), "r+b")
        try:
            entitlements = plistlib.load(ef)
        finally:
            ef.close()

        return entitlements

    def set_target_entitlements(self, target_name: str, configuration_name: str, entitlements: Dict):
        config = self.target_configuration(target_name, configuration_name)
        entitlements_file = config['CODE_SIGN_ENTITLEMENTS']

        ef = open(self.project_file_path(entitlements_file), "w+b")
        try:
            plistlib.dump(entitlements, ef)
        finally:
            ef.close()
