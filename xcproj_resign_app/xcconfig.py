import os
import re
from typing import Dict

from .utils_path import relative_to_absolute_path


class XcConfig:
    def __init__(self, **kwargs):
        super(XcConfig, self).__init__()

        self.values = dict()
        self.filename = kwargs.pop('filename', None)
        if self.filename is not None:
            self.load()

    @staticmethod
    def render_variables_from(line: str, config_values: Dict[str, str]) -> str:
        def replace_variables(match):
            variable_name = match.group(1)  # Extract the VARIABLE_NAME

            return config_values.get(variable_name, match.group(0))

        pattern = r'\$\((\w+)\)'  # Regular expression pattern to match $(VARIABLE_NAME)
        result = re.sub(pattern, replace_variables, line)
        return result

    def render_variables(self, line: str) -> str:
        return XcConfig.render_variables_from(line, self.values)

    def render_variables_in_values(self):
        for key in self.values:
            self.values[key] = self.render_variables(self.values[key])

    @staticmethod
    def load_config_file(filename: str) -> Dict[str, str]:
        if filename is None:
            raise ValueError('Cannot load .xcconfig, file name is not specified')

        filedir = os.path.dirname(filename)

        values = dict()

        config_lines = [line.strip() for line in open(filename)]

        for line in config_lines:
            # There can be four cases:
            # 1. Value assignment
            # 2. #include
            # 3. // Comment
            # 4. Empty line

            if line.startswith('#include'):
                include_pattern = r'#include\s*["\']?(.*?)["\']?\s*$'
                match = re.match(include_pattern, line)
                if match:
                    try:
                        included_values = XcConfig.load_config_file(relative_to_absolute_path(match.group(1), filedir))
                        values.update(included_values)
                    except:
                        pass

            elif line.startswith('//') or len(line) == 0:
                pass

            else:
                pattern = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*?)\s*$'
                match = re.match(pattern, line)

                if match:
                    identifier = match.group(1)
                    value = match.group(2)
                    values[identifier] = value

        return values

    def load(self, filename: str = None, render: bool = True) -> Dict[str, str]:
        if filename is None:
            filename = self.filename
        else:
            self.filename = filename

        self.values = XcConfig.load_config_file(filename)

        if render:
            self.render_variables_in_values()

        return self.values
