# Canteen_Management

## Table of Contents
- [Create Virtual Environment](#create-virtual-environment)
- [Activate Virtual Environment](#activate-virtual-environment)
- [Install all Requirements](#install-all-requirements)
- [Run the Django Application](#run-the-pyqt5-application)
 
## Create Virtual Environment (Optional)

1. Open your command prompt or terminal.

2. Navigate to your project directory (if you haven't already) where you want to create the virtual environment.

3. Run the following command to create a virtual environment. 

    python -m venv "Virtual_Environment_Name"

4. Replace "Virtual_Environment_Name" with your desired name.



## Activate Virtual Environment:

1. Navigate to the virtual environment's "Scripts" directory.

2. Run the following command to activate a virtual environment. 

    -cd "Virtual_Environment_Name"\Scripts

    -activate       (for cmd)

    -Activate.ps1   (for powershell)

3. Replace "Virtual_Environment_Name" with your created virtural environment.



## Install all Requirements

1. Activate the virtural Environment if created.

2. Navigate to the "Canteen_Management" Directory.

3. Run the following command to install all requirements:
    
    -pip install -r requirements.txt
   


## Run the Django Application

1. Activate the virtural Environment if created.

2. Navigate to the "Canteen_Management" Directory

3. Run the following code in terminal to run Python code

   -python .\manage.py runserver
