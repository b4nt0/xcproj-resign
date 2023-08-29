import os.path
from argparse import ArgumentParser

from xcproj_resources.utils_string import random_string
from xcproj_resources.xcproject import XcProject


def main():
    ap = ArgumentParser(
        prog='xcproj_resign',
        description="""This utility prepares an Xcode project to be used as Guardsquare test example.
What it means is that the tool:
1. Renames all bundle IDs to com.guardsquare.ixguard.allentitlements.*
2. Updates the signing team + sets automated signing
3. Generates a fastlane script to get signing keys
4. Generates a fastlane script to register entitlements""")

    ap.add_argument('pbxproj_file', help='path to the .pbxproj file or to the .xcodeproj directory')
    ap.add_argument('--bundleprefix', help='rename all bundles to force a certain bundle prefix', required=False)
    ap.add_argument('--team', help='signing team identifier', required=False)
    ap.add_argument('--config', default='Release', help='configuration name (Release is the default)')
    ap.add_argument('--fastlanescript', help='fastlane script file name', required=False)
    ap.add_argument('--bundle_template', default='./.xcproj_resign/create-bundle-template.sh', help='fastlane tempalte to create a bundle')

    args = ap.parse_args()

    if args.pbxproj_file.endswith('.xcodeproj'):
        xcproj_file = args.pbxproj_file
    else:
        xcproj_file = os.path.dirname(args.pbxproj_file)

    project = XcProject(filename=args.pbxproj_file)

    print(f'Generating names for Project {os.path.basename(xcproj_file)}')

    targets = project.targets
    print(f'...found {len(targets)} targets\n')

    used_bundle_ids = list()
    for target in targets:
        print(f'Target {target.name}')
        config = project.target_configuration(target.name, args.config)
        print(f"..Bundle {config['PRODUCT_BUNDLE_IDENTIFIER']}")

        if args.bundleprefix is not None:
            # Rename the bundle through adding prefix
            bundle_id_components = config['PRODUCT_BUNDLE_IDENTIFIER'].split('.')
            last_bundle_id_component = bundle_id_components[-1]

            # Eliminate variables
            if last_bundle_id_component.startswith('$('):
                last_bundle_id_component = random_string()

            # Try bundle ID candidates until one fits
            new_bundle_id = f'{args.bundleprefix}.{last_bundle_id_component}'
            attempt = 1
            while new_bundle_id in used_bundle_ids:
                new_bundle_id = f'{args.bundleprefix}.{last_bundle_id_component}{attempt}'
                attempt += 1

            used_bundle_ids.append(new_bundle_id)
            project.set_target_configuration(target.name, args.config, 'PRODUCT_BUNDLE_IDENTIFIER', new_bundle_id)

            print(f"...set to {new_bundle_id}")

            if args.team:
                print(f'...setting signing information to team {args.team}')

                project.set_target_configuration(target.name, args.config, 'CODE_SIGN_IDENTITY', 'iPhone Developer')
                project.set_target_configuration(target.name, args.config, 'CODE_SIGN_STYLE', 'Automatic')
                project.set_target_configuration(target.name, args.config, 'DEVELOPMENT_TEAM', args.team)
                project.set_target_configuration(target.name, args.config, 'PROVISIONING_PROFILE', '')
                project.set_target_configuration(target.name, args.config, 'PROVISIONING_PROFILE_SPECIFIER', '')

    if args.fastlanescript:
        print('Writing out a fastlane script')
        with open(args.bundle_template, 'r') as bundle_template_file:
            bundle_template_script = bundle_template_file.read()

        with open(args.fastlanescript, 'w') as fastlane_script_file:
            for bundle in used_bundle_ids:
                bundle_line = bundle_template_script.replace('<bundle_id>', bundle)
                fastlane_script_file.write(bundle_line + '\n')
                print(f'..{bundle_line}')


if __name__ == "__main__":
    main()
