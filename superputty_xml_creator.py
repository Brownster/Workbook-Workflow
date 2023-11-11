# Importing necessary libraries
from flask import Flask, request, send_file, render_template, redirect, url_for, jsonify
import os
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import base64
from io import BytesIO

# Initialize the Flask application
app = Flask(__name__)
# Configure the folder for uploading files
app.config['UPLOAD_FOLDER'] = '/tmp/'

# Function to check if the uploaded file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx'}

# Route for the main index page
@app.route('/', methods=['GET'])
def index():
    # Render and return the index.html template
    return render_template('index.html')

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    # Process POST request for file upload
    if request.method == 'POST':
        # Check if a file is part of the upload
        if 'file' not in request.files:
            return redirect(request.url)

        # Get the uploaded file
        file = request.files['file']
        # Get form data
        group_name = request.form['group_name']
        column_name = request.form['column_name']
        match_value = request.form['match_value']

        # Validate file name and extension
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)

        # Save the uploaded file
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # Read the Excel file using Pandas
        df = pd.read_excel(filename, engine='openpyxl')

        # Check if the specified column exists in the data
        if column_name not in df.columns:
            return f"The column '{column_name}' does not exist in the Excel file.", 400

        # Filter DataFrame based on column value
        matched_df = df[df[column_name].astype(str).str.strip() == match_value.strip()]
        # Generate XML content for Putty sessions
        putty_xml_content = generate_putty_sessions_xml(matched_df, group_name, match_value)

        # Prepare and save the processed XML file
        processed_filename = f"processed_{file.filename.rsplit('.', 1)[0]}.xml"
        processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        with open(processed_filepath, 'w') as putty_file:
            putty_file.write(putty_xml_content)

        # Redirect to the download route
        return redirect(url_for('download_file', filename=processed_filename))

    # Return an error message if there's an upload issue
    return 'File upload error'

# API Endpoint to handle file upload and processing via JSON
@app.route('/api/upload', methods=['POST'])
def api_upload_file():
    if request.method == 'POST':
        # Expecting JSON data
        if not request.is_json:
            return jsonify({'error': 'Invalid data format, JSON expected'}), 400
        
        # Extract data from JSON
        json_data = request.get_json()
        group_name = json_data.get('group_name')
        column_name = json_data.get('column_name')
        match_value = json_data.get('match_value')
        file_data = json_data.get('file_data')

        if not file_data:
            return jsonify({'error': 'No file data provided'}), 400

        # Decode base64 file data and process
        try:
            decoded_file = base64.b64decode(file_data)
            excel_file = BytesIO(decoded_file)
            df = pd.read_excel(excel_file, engine='openpyxl')
        except Exception as e:
            return jsonify({'error': f'Error processing file: {e}'}), 500

        if column_name not in df.columns:
            return jsonify({'error': f"The column '{column_name}' does not exist."}), 400

        matched_df = df[df[column_name].astype(str).str.strip() == match_value.strip()]

        try:
            putty_xml_content = generate_putty_sessions_xml(matched_df, group_name, match_value)
            xml_string = putty_xml_content
        except Exception as e:
            return jsonify({'error': f'Error generating XML: {e}'}), 500

        return jsonify({'message': 'File processed successfully', 'xml_content': xml_string})

# Function to pretty-print XML content
def prettify_xml(element):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# Function to generate Putty sessions XML from DataFrame
def generate_putty_sessions_xml(df, group_name, match_value):
    # Create XML root element
    root = ET.Element('ArrayOfSessionData')
    root.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

    # Define folder mappings for sessions
    folder_mapping = {
        'exporter_linux': 'Linux Server',
        'exporter_gateway': 'Media Gateway',
        'exporter_windows': 'Windows Server',
        'exporter_verint': 'Verint Server',
    }
    
    # Determine subfolder name based on match_value
    subfolder = folder_mapping.get(match_value, 'Other')

    for index, row in df.iterrows():
        # Create a session data element for each row
        session_data = ET.SubElement(root, 'SessionData')

        # Set common session data attributes
        session_id = f"{group_name}/{subfolder}/{row['Country']}/{row['Location']}/{row['Hostnames']}"
        session_data.set('SessionId', session_id)
        session_data.set('SessionName', row['Hostnames'])
        session_data.set('ImageKey', 'computer')
        session_data.set('Host', row['IP Address'])

        # Set protocol-specific data based on match_value
        if match_value in ['exporter_windows', 'exporter_verint']:
            session_data.set('Port', '3389')  # Default RDP port
            session_data.set('Proto', 'RDP')
        else:
            session_data.set('Port', '22')  # Default SSH port
            session_data.set('Proto', 'SSH')
            session_data.set('PuttySession', 'Default Settings')
            if pd.notna(row['ssh_username']) and str(row['ssh_username']).strip():
                session_data.set('Username', str(row['ssh_username']))

    # Return the pretty-printed XML string
    return prettify_xml(root)

# Route for downloading the XML file
@app.route('/downloads/<filename>', methods=['GET'])
def download_file(filename):
    # Set the download folder path
    download_folder = app.config['UPLOAD_FOLDER']
    file_path = os.path.join(download_folder, filename)
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        return "File not found.", 404

    # Send the file to the client
    response = send_file(file_path, as_attachment=True, download_name=filename)
    # Remove the file after sending
    os.remove(file_path)
    
    return response

# Main function to run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

