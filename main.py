from flask import Flask, request, send_file, redirect, url_for, render_template, flash, session
import os
import pandas as pd
import io
from superputty_xml_creator import generate_putty_sessions_xml
from workbook_exporter import process_exporter
from yaml_format_fixer import process_yaml_file, process_diff_to_html
from html_bookmark_generator import filter_exporters, generate_bookmarks_html
from workbook_importer import yaml_to_csv

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls', 'yaml', 'yml', 'eyaml', 'csv', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        operation = request.form['process-type']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            if operation == 'super-putty':
                # Process for SuperPutty XML Generation
                group_name = request.form['group-name']
                column_name = request.form['column-name']
                match_value = request.form['match-value']
                df = pd.read_excel(filepath)
                xml_content = generate_putty_sessions_xml(df, group_name, column_name, match_value)

                # Send the XML content as a downloadable file
                mem = io.BytesIO()
                mem.write(xml_content.encode('utf-8'))
                mem.seek(0)
                return send_file(mem, as_attachment=True, filename="putty_sessions.xml")

            elif operation == 'yaml-to-csv':
                # Process YAML to CSV
                output_filename = filename.rsplit('.', 1)[0] + '.csv'
                output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
                yaml_to_csv(filepath, output_filepath)
                return send_file(output_filepath, as_attachment=True)

            elif operation == 'bookmark':
                # Process for HTML Bookmark Generation
                group_name = request.form['group-name']
                filtered_data = filter_exporters(filepath, group_name)
                bookmarks_html = generate_bookmarks_html(filtered_data)

                # Send the HTML content as a downloadable file
                mem = io.BytesIO()
                mem.write(bookmarks_html.encode('utf-8'))
                mem.seek(0)
                return send_file(mem, as_attachment=True, filename="bookmarks.html")

            # Add additional elif blocks for other operations...
        
        else:
            flash('Invalid file format')
            return redirect(request.url)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(file_path):
        return "File not found.", 404
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
