# Canteen_Management

## Table of Contents
- [Create Virtual Environment](#create-virtual-environment)
- [Activate Virtual Environment](#activate-virtual-environment)
- [Install all Requirements](#install-all-requirements)
- [Run the Django Application](#run-the-django-application)
- [Run the Django Application in LAN](#run-the-django-application-in-lan)
- [Create Run Server .bat file](#create-run-server-bat-file)
 
## Create Virtual Environment:

1. Open your command prompt or terminal.

2. Navigate to your project directory (if you haven't already) where you want to create the virtual environment.

3. Run the following command to create a virtual environment. 

    - python -m venv "Virtual_Environment_Name"

Note: Replace "Virtual_Environment_Name" with your desired name.



## Activate Virtual Environment:

1. Navigate to the virtual environment's "Scripts" directory.

    - cd "Virtual_Environment_Name"\Scripts

2. Run the following command to activate a virtual environment. 

    - activate       (for cmd)

    - Activate.ps1   (for powershell)

Note: Replace "Virtual_Environment_Name" with your created virtural environment.



## Install all Requirements:

1. Activate the virtural Environment if created.

2. Navigate to the "Canteen_Management" Directory.

3. Run the following command to install all requirements:
    
    - pip install -r requirements.txt
   


## Run the Django Application:

1. Activate the virtural Environment if created.

2. Navigate to the "Canteen_Management" Directory

3. Run the following code in terminal to run Python code

   - python .\manage.py runserver
   


## Run the Django Application in LAN:

1. Activate the virtural Environment if created.

2. Navigate to the "Canteen_Management" Directory

3. Get the IPv4 Address from terminal

   - ipconfig

4. Add the IPv4 address to ALLOWED_HOSTS in 29th line of Canteen_Management\settings.py file.

5. Run the following code in terminal to run Python code

   - python .\manage.py runserver "IPv4 Address":8000

Note: Replace the "IPv4 Address" with actual IPv4 address without quotes. 



## Create Run Server .bat file:

1. Navigate to the "Canteen_Management" Directory

2. Add a .txt file and rename to .bat file

3. Edit the .bat file as following:

   - cd "Your path of Canteen_Management Folder"
     
   - if you have virtual env, copy and paste the entire content in activate file from "Your virtual env"\Scripts
  
   - python .\manage.py runserver

   - python .\manage.py runserver "IPv4 Address":8000 (for LAN)

4. Run the .bat file
