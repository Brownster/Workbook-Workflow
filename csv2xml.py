import os
import sys
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import csv

def prettify_xml(element):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def get_friendly_name_mapping(csv_path):
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return {row['filename'].strip(): row['friendly_name'].strip() for row in reader}

def generate_putty_sessions_xml(df, group_name, match_value):
    root = ET.Element('ArrayOfSessionData')
    root.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

    # Define the folder mapping based on the match_value
    folder_mapping = {
        'exporter_linux': 'Linux Servers',
        'exporter_gateway': 'Media Gateways',
        'exporter_windows': 'Windows Servers',
        'exporter_verint': 'Verint Servers',
        
    }
    
    # Determine the subfolder name based on the match_value
    subfolder = folder_mapping.get(match_value, 'Other')

    for index, row in df.iterrows():
        session_data = ET.SubElement(root, 'SessionData')

        # Set common session data
        session_id = f"{group_name}/{subfolder}/{row['Country']}/{row['Location']}/{row['Hostnames']}"
        session_data.set('SessionId', session_id)
        session_data.set('SessionName', row['Hostnames'])
        session_data.set('ImageKey', 'computer')
        session_data.set('Host', row['IP Address'])

        # Set protocol-specific session data
        if match_value in ['exporter_windows', 'exporter_verint']:
            # Default RDP port is 3389
            session_data.set('Port', '3389')
            session_data.set('Proto', 'RDP')
            # Username is not available for Windows servers
        else:
            # Default SSH port is 22
            session_data.set('Port', '22')
            session_data.set('Proto', 'SSH')
            session_data.set('PuttySession', 'Default Settings')
            if pd.notna(row['ssh_username']) and str(row['ssh_username']).strip():
                session_data.set('Username', str(row['ssh_username']))

    return prettify_xml(root)

def convert_csv_to_xml(csv_file_path, xml_file_path, group_name, column_name, match_value):
    df = pd.read_csv(csv_file_path)

    matched_df = df[df[column_name].astype(str).str.strip() == match_value.strip()]
    xml_content = generate_putty_sessions_xml(matched_df, group_name, match_value)

    with open(xml_file_path, 'w') as xml_file:
        xml_file.write(xml_content)

def bulk_csv_to_xml(csv_folder, output_folder, mapping_csv_path):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Load the friendly name mapping
    friendly_name_mapping = get_friendly_name_mapping(mapping_csv_path)

    # The options for match_value and corresponding suffixes
    options = [
        ("exporter_linux", "Linux"),
        ("exporter_windows", "Windows"),
        ("exporter_gateway", "Gateway"),
        ("exporter_verint", "Verint")
    ]

    success_count = 0
    failure_count = 0
    failed_files = []

    for filename in os.listdir(csv_folder):
        if filename.endswith('.csv'):
            csv_file_path = os.path.join(csv_folder, filename)
            base_filename = os.path.splitext(filename)[0]
            friendly_name = friendly_name_mapping.get(base_filename, base_filename)


            for match_value, suffix in options:
                column_name = 'Exporter_name_os' if 'linux' in match_value or 'windows' in match_value or 'verint' in match_value else 'Exporter_name_app'
                group_name = friendly_name
                xml_file_name = f"{friendly_name}-{suffix}.xml"
                xml_file_path = os.path.join(output_folder, xml_file_name)

                try:
                    print(f"Converting {csv_file_path} to {xml_file_path} with match value '{match_value}'")
                    convert_csv_to_xml(csv_file_path, xml_file_path, group_name, column_name, match_value)
                    success_count += 1
                except Exception as e:
                    print(f"Failed to convert {csv_file_path} with match value '{match_value}': {e}")
                    failure_count += 1
                    failed_files.append((csv_file_path, match_value))

    print(f"Conversion completed with {success_count} successes and {failure_count} failures.")
    if failed_files:
        print("Failed files:")
        for file, match_value in failed_files:
            print(f"{file} with match value '{match_value}'")

if __name__ == '__main__':

    if len(sys.argv) < 4:
        print("Usage: python script.py <csv_folder> <output_folder> <mapping_csv_path>")
    else:
        csv_folder = sys.argv[1]
        output_folder = sys.argv[2]
        mapping_csv_path = sys.argv[3]
        bulk_csv_to_xml(csv_folder, output_folder, mapping_csv_path)
