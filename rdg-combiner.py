import os
import xml.etree.ElementTree as ET

def combine_rdg_files(folder_path, output_file_path):
    # Create the root element for the combined file
    root = ET.Element('RDCMan', programVersion="2.93", schemaVersion="3")
    file_node = ET.SubElement(root, 'file')

    for filename in os.listdir(folder_path):
        if filename.endswith('.rdg'):
            file_path = os.path.join(folder_path, filename)
            tree = ET.parse(file_path)
            root_element = tree.getroot()

            # Extract the group element and append it to the file node
            group_element = root_element.find('./file/group')
            if group_element is not None:
                file_node.append(group_element)

    # Write the combined XML to a file
    tree = ET.ElementTree(root)
    tree.write(output_file_path, encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    folder_path = '/home/marc/Downloads/nodes/script/output/'
    output_file_path = '/home/marc/Downloads/nodes/script/combined.rdg'
    combine_rdg_files(folder_path, output_file_path)

