from flask import Flask, request, send_file, redirect, url_for, render_template, flash, session
import os
import pandas as pd
import io
from superputty_xml_creator import generate_putty_sessions_xml
from workbook_exporter import process_exporter
from yaml_format_fixer import process_yaml_file, process_diff_to_html
from html_bookmark_generator import filter_exporters, generate_bookmarks_html
from workbook_importer import yaml_to_csv
from werkzeug.utils import secure_filename

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
                group_name = request.form['group-name']
                column_name = request.form['column-name']
                match_value = request.form['match-value']
                df = pd.read_excel(filepath)
                xml_content = generate_putty_sessions_xml(df, group_name, column_name, match_value)
                mem = io.BytesIO()
                mem.write(xml_content.encode('utf-8'))
                mem.seek(0)
                return send_file(mem, as_attachment=True, filename="putty_sessions.xml")

            elif operation == 'workbook-export':
                # Logic for Workbook Export
                existing_yaml = request.files.get('existing_yaml')
                default_listen_port = request.form.get('default_listen_port')
                output = process_exporter(filepath, existing_yaml, default_listen_port)
                return output

            elif operation == 'workbook-import':
                # Process YAML to CSV
                output_filename = filename.rsplit('.', 1)[0] + '.csv'
                output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
                yaml_to_csv(filepath, output_filepath)
                return send_file(output_filepath, as_attachment=True)

            elif operation == 'rdp-man':
                # Logic for RDPMan RDG Generation
                group_name = request.form['group_name']
                column_name = request.form['column_name']
                match_value = request.form['match_value']

                wb = load_workbook(filename=filepath)
                sheet = wb.active
                df = pd.read_excel(filepath, engine='openpyxl')

                # Check if the column exists
                if column_name not in df.columns:
                    flash(f"The column '{column_name}' does not exist in the Excel file.")
                    return redirect(url_for('index'))

                # Additional processing based on the RDPMan script...
                matched_df = df[df[column_name].astype(str).str.strip() == match_value.strip()]
                rdg_content = generate_rdg(matched_df, group_name)

                # Send the RDG content as a downloadable file
                mem = io.BytesIO()
                mem.write(rdg_content.encode('utf-8'))
                mem.seek(0)
                processed_filename = f"processed_{filename.rsplit('.', 1)[0]}.rdg"
                return send_file(mem, as_attachment=True, filename=processed_filename)

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

               # Additional operations can be handled here...

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
