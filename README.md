# xcproj-resign

An tool to bulk update package names, entitlements, and signing information in sample repositories. 

## Setting up

### Create a Python virtual environment

```sh
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

### Run tests

```sh
source ./venv/bin/activate
pytest .
```

## Running

```sh
source ./venv/bin/activate
python xcproj_resign.py [-h] [--bundleprefix BUNDLEPREFIX] [--team TEAM] [--config CONFIG] [--fastlanescript FASTLANESCRIPT] [--bundle_template BUNDLE_TEMPLATE] pbxproj_file
```

where:

- `-h` show the help text
- `--bundleprefix BUNDLEPREFIX` rename all bundles by giving them a prefix. For example, `--bundleprefix com.test` will rename the bundle `com.sample.app` to `com.test.app`
- `--team TEAM` will update signing information to the specified team. For example, `--team ABCDE` will set the signing to `Automatic` and the team to `ABCDE`. A special value of `None` will remove signing
- `--fastlanescript FASTLANESCRIPT` will output a fastlane script to request provisioning profiles. The script will be generated from a template file where `<bundle_id>` is replaced with an actual bundle id.
- `--bundletemplate BUNDLE_TEMPLATE` defines a file for the fastlane script template. By default this is set to `./.xcproj_resign/create-bundle-template.sh`.
