"""
Upon importing loads configurations from the files that are provided as
commandline argument with `--config`.
"""
import argparse
import warnings
from pathlib import Path
from conf.parsers import parse_from_yaml, parse_from_json, parse_from_ini


get = globals().get  # Capture the `get` method from `dict`.


def load(*file_names, override=True):
    """
    Read the given file_names and load their content into this configuration
    module.
    :param file_names: a varg that contains paths (str) to the conf files
    that need to be read.
    :param override: determines whether previously known configurations need to
    be overridden.
    :return: None.
    """
    for filename in file_names:
        if not filename:
            warnings.warn('an empty filename is not allowed')
            return
        file_path = Path(filename)
        suffix = file_path.suffix or 'default'
        if not file_path.exists():
            warnings.warn('conf file "%s" not found' % filename)
            return
        parser = _supported_types.get(suffix.lower(), None)
        if not parser:
            warnings.warn('cannot parse files of type "%s"' % suffix)
            return
        with open(filename) as file:
            try:
                configurations = parser(file)
            except Exception as err:
                warnings.warn('failed to parse "%s". Reason: %s' %
                              (filename, err))
                return
        for key in configurations:
            if override or not get(key):
                globals()[key] = configurations[key]


_supported_types = {
    '.yml': parse_from_yaml,
    '.yaml': parse_from_yaml,
    '.json': parse_from_json,
    '.ini': parse_from_ini,
    'default': parse_from_ini
}
_help_msg = 'conf file(s) to load. Supported types are: %s' % \
            ', '.join(_supported_types)
_parser = argparse.ArgumentParser()
_parser.add_argument('--config', metavar='conf-file',
                     nargs='+', type=str, help=_help_msg)
_parsed_config = _parser.parse_known_args()[0]

if _parsed_config.config:
    load(*_parsed_config.config, override=True)