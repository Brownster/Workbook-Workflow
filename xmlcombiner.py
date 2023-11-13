import os
import xml.etree.ElementTree as ET

def combine_xml_files(input_folder, output_file):
    # Create the root element for the combined XML
    combined_root = ET.Element('ArrayOfSessionData')
    combined_root.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
    combined_root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

    # Iterate over all XML files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.xml'):
            file_path = os.path.join(input_folder, file_name)
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Append each 'SessionData' element from the current file to the combined root
            for session_data in root.findall('SessionData'):
                combined_root.append(session_data)

    # Create a new XML tree with the combined root and write to the output file
    tree = ET.ElementTree(combined_root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    input_folder = '/home/marc/Downloads/nodes/script/output'  # Replace with the path to your XML files
    output_file = '/home/marc/Downloads/nodes/script/combined.xml'  # Replace with your desired output file path
    combine_xml_files(input_folder, output_file)

