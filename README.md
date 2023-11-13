SM3 Monitoring Configurator
Overview

This Flask application serves as a unified interface for various tasks related to excel workbooks containing ip address, fqdn and server what monitoring exporters are to be setup for monitoring configuration im prometheus. It combines multiple functionalities like creating bookmarks HTML from a workbook, converting between YAML and CSV formats, formatting YAML files, and generating SuperPutty XML configurations.
Features

    File Upload: Users can upload Excel workbooks, CSV, or YAML files.
    Multiple Processing Options: Including YAML to CSV conversion, CSV to YAML conversion, YAML file formatting, bookmarks HTML generation, and SuperPutty XML generation.
    User-friendly Interface: Easy-to-navigate web interface for seamless user experience.

Installation

To set up this application, follow these steps:

    Clone the Repository

    bash

git clone https://github.com/Brownster/prometheus-configurator.git

Navigate to the Project Directory

bash

cd prometheus-configurator

Install Required Packages

bash

    pip install -r requirements.txt

Usage

    Run the Flask App

    bash

flask run

or

bash

    python app.py

    Access the Application
        Open a web browser and navigate to http://127.0.0.1:5000.

    Using the Application
        Upload the desired file (Excel workbook, CSV, or YAML).
        Select the process you want to perform from the dropdown menu.
        Click on "Upload and Process" to initiate the processing.

Contributing

Contributions to this project are welcome. To contribute:

    Fork the repository.
    Create a new branch for your feature (git checkout -b feature/AmazingFeature).
    Commit your changes (git commit -m 'Add some AmazingFeature').
    Push to the branch (git push origin feature/AmazingFeature).
    Open a pull request.

License

Distributed under the MIT License. See LICENSE for more information.
