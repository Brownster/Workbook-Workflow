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

def generate_rdg(df, group_name):
    root = ET.Element('RDCMan', programVersion="2.93", schemaVersion="3")
    file_node = ET.SubElement(root, 'file')
    group_node = ET.SubElement(file_node, 'group')
    properties_node = ET.SubElement(group_node, 'properties')
    ET.SubElement(properties_node, 'expanded').text = 'True'
    ET.SubElement(properties_node, 'name').text = group_name

    for index, row in df.iterrows():
        server_node = ET.SubElement(group_node, 'server')
        properties_node = ET.SubElement(server_node, 'properties')
        ET.SubElement(properties_node, 'displayName').text = str(row['FQDN'])
        ET.SubElement(properties_node, 'name').text = str(row['IP Address'])
        comment_text = f"Configuration Item :{row['Configuration Item Name']}"

        if 'Secret Server URL' in df.columns and pd.notnull(row['Secret Server URL']):
            secret_url = row['Secret Server URL']
        else:
            secret_url = "URL Not Available"

        comment_text += f"\nSS URL:{secret_url}"
        ET.SubElement(properties_node, 'comment').text = comment_text

    return prettify_xml(root)

def convert_csv_to_rdg(csv_file_path, rdg_file_path, group_name):
    df = pd.read_csv(csv_file_path)
    rdg_content = generate_rdg(df, group_name)

    with open(rdg_file_path, 'w') as rdg_file:
        rdg_file.write(rdg_content)

def bulk_csv_to_rdg(csv_folder, output_folder, mapping_csv_path):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Load the friendly name mapping
    friendly_name_mapping = get_friendly_name_mapping(mapping_csv_path)

    for filename in os.listdir(csv_folder):
        if filename.endswith('.csv'):
            csv_file_path = os.path.join(csv_folder, filename)
            base_filename = os.path.splitext(filename)[0]
            friendly_name = friendly_name_mapping.get(base_filename, base_filename)
            group_name = friendly_name
            rdg_file_name = f"{friendly_name}.rdg"
            rdg_file_path = os.path.join(output_folder, rdg_file_name)

            print(f"Converting {csv_file_path} to {rdg_file_path} with group name '{group_name}'")
            try:
                convert_csv_to_rdg(csv_file_path, rdg_file_path, group_name)
            except Exception as e:
                print(f"Failed to convert {csv_file_path}: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python script.py <csv_folder> <output_folder> <mapping_csv_path>")
        sys.exit(1)

    csv_folder = sys.argv[1]
    output_folder = sys.argv[2]
    mapping_csv_path = sys.argv[3]
    bulk_csv_to_rdg(csv_folder, output_folder, mapping_csv_path)
