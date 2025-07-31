# Written by ChatGPT with minor editing
# Show all current values
#       python change3mf.py my_model.3mf --show
# Show one field (e.g., printer_model)
#       python change3mf.py my_model.3mf --show --element printer_model
# Modify values
#       python change3mf.py your_model.3mf --modifications "printer_model=My Printer,printer_settings_id=MyID"
# Modify a list field
#       python change3mf.py your_model.3mf --modifications "filament_settings_id=[\"PLA\",\"PLA\",\"ABS\"]"
# Bulk modify based on a .json file
#       python change3mf.py your_model.3mf --config-from-file my_config.json

import zipfile
import json
import xml.etree.ElementTree as ET
import argparse
import os
# import re
import shutil

CONFIG_PATH = 'Metadata/project_settings.config'
MODEL_SETTINGS = 'Metadata/model_settings.config'

def read_config_json(three_mf_path):
    with zipfile.ZipFile(three_mf_path, 'r') as zf:
        if CONFIG_PATH not in zf.namelist():
            raise FileNotFoundError(f"{CONFIG_PATH} not found in the .3mf file.")
        raw = zf.read(CONFIG_PATH).decode('utf-8-sig')
        model_xml = zf.read(MODEL_SETTINGS).decode('utf-8-sig')
        return json.loads(raw),model_xml

def parse_modifications(mod_str):
    modifications = {}
    for pair in mod_str.split(','):
        if '=' not in pair:
            raise ValueError(f"Invalid format in modification: {pair}")
        key, value = pair.split('=', 1)
        key = key.strip()
        value = value.strip()

        if value.startswith("[") and value.endswith("]"):
            try:
                parts = ['"' + p.strip().strip('"').strip("'") + '"' for p in value.strip("[]").split(",")]
                value_fixed = "[" + ",".join(parts) + "]"
                value = json.loads(value_fixed)
            except json.JSONDecodeError:
                print(f"⚠️  Could not parse list: {value}, using raw string.")
        modifications[key] = value
    return modifications

def modify_config(config, modifications, enable_log=False):
    changes = []
    for key, value in modifications.items():
        old = config.get(key, "<not set>")
        if key not in config:
            print(f"⚠️  Key '{key}' not found in config. It will be added.")
        config[key] = value
        if enable_log:
            changes.append((key, old, value))
    return config, changes

def show_config(config, element_name=None):
    if element_name:
        value = config.get(element_name, None)
        if value is not None:
            print(f"{element_name}: {value}")
        else:
            print(f"{element_name} not found in config.")
    else:
        print(json.dumps(config, indent=2))

# Function to parse the XML and return an ElementTree object
def parse_config_xml(config_data):
    return ET.ElementTree(ET.fromstring(config_data))

def update_xml_metadata(root, key, value):

    for item in root:
        for elem in item:
            if elem.tag == 'metadata':
#   Replace the original name in the XML with the name of the 3MF file
                if elem.attrib.get('key') == 'name':
                    elem.attrib['value'] = value

def save_modified_3mf(original_path, config_data, xml, create_backup=True, namechange=True):
    if create_backup:
        backup_path = original_path + ".bak"
        shutil.copy2(original_path, backup_path)
        print(f"🛡️  Backup saved as: {backup_path}")

    with zipfile.ZipFile(original_path, 'r') as original_zip:
        temp_path = original_path + ".tmp"
        with zipfile.ZipFile(temp_path, 'w') as new_zip:

            for item in original_zip.namelist():
                if item == CONFIG_PATH:
                    new_zip.writestr(CONFIG_PATH, json.dumps(config_data))
                else:
                    if item == MODEL_SETTINGS and namechange:
                        tree = parse_config_xml(xml)
                        root = tree.getroot()
                        update_xml_metadata(root,'name',os.path.splitext(os.path.basename(original_path))[0])
                        xml_bytes = ET.tostring(root, encoding='utf-8', method='xml')
                        new_zip.writestr(item, xml_bytes.decode('utf-8'))
                    else:
                        new_zip.writestr(item, original_zip.read(item))

    os.replace(temp_path, original_path)
    print(f"✅ Changes saved to: {original_path}")

def main():
    parser = argparse.ArgumentParser(description="Modify JSON-based .3mf Metadata/project_settings.config.")
    parser.add_argument('three_mf_file', help="Path to the .3mf file.")
    parser.add_argument('--modifications', help='Comma-separated key=value pairs. Values can be JSON lists.')
    parser.add_argument('--config-from-file', help='Path to JSON config file with desired modifications.')
    parser.add_argument('--show', action='store_true', help="Show the config or a specific element.")
    parser.add_argument('--element', help="Specific element to show.")
    parser.add_argument('--log', action='store_true', help="Log changes made to the config.")
    parser.add_argument('--nobackup', action='store_true', help="Do not create a .bak backup of the original file.")
    parser.add_argument('--nonamechange', action='store_true', help="Do not change the name in the XML metadata to match the filename.")

    args = parser.parse_args()

    try:
        config,xml = read_config_json(args.three_mf_file)

        if args.show:
            show_config(config, args.element)
        else:
            if args.config_from_file:
                with open(args.config_from_file, 'r', encoding='utf-8') as f:
                    modifications = json.load(f)
            elif args.modifications:
                modifications = parse_modifications(args.modifications)
            else:
                raise ValueError("You must provide either --modifications or --config-from-file")

            config, changes = modify_config(config, modifications, enable_log=args.log)
            save_modified_3mf(args.three_mf_file, config, xml, create_backup=not args.nobackup, namechange=not args.nonamechange)

            if args.log:
                print("\n🔧 Changes made:")
                for key, old, new in changes:
                    print(f" - {key}: {old} → {new}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
