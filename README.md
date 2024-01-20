# COUNTER 5 Report Tool
[Note, this was developed in 2020. A new version that will support both 5.0 and 5.1 is under development, expected to be released in May 2024. - Melissa Belvadi]

This project uses the SUSHI API to request usage reports from library vendors. The JSON data received is used to generate TSV reports that follow the COUNTER 5 standards.
The project is written with Python 3.7. The PyQt GUI framework is used to create a user friendly (hopefully) GUI.

March 2022 Note: This code is still supported by librarian Melissa Belvadi at UPEI, mbelvadi@upei.ca. 
However, the executables may not be updated to match code changes that have taken place - check the last modified dates on them versus the code. I'm looking for volunteers to help me update those executables. In particular, I don't have access to a Mac to rebuild that one. Please contact me if you can help with that.

## License
 It is released with permission of all students involved under the MIT License for open source software. https://opensource.org/licenses/MIT

## Features
- Manage library vendor credentials
- Fetch reports that strictly adhere to the COUNTER 5 standards
- Fetch customized reports using the available parameters in the SUSHI API
- Import COUNTER 5 reports into the local directories and database and some COUNTER 4 reports into the database
- Specify the costs of subscribed items (user can input)
- Search the sqlite database of fetched and imported reports
- Generate charts using the data in the database

## Developer Contact Info - original developers
- Adam McGuigan apmcguigan@upei.ca
- Chandler Acorn cjacorn@upei.ca
- Samuel Esan sesan@upei.ca
- Urvesh Boodhun uboodhun@upei.ca
- Ziheng Huang Zihhuang@upei.ca

## Future developer contact info
- Melissa Belvadi, mbelvadi@upei.ca

## Download Project 
https://github.com/CS-4820-Library-Project/COUNTER-5-Report-Tool/releases

## Developer Documentation
https://counter-5-report-tool.readthedocs.io/en/latest/

## How to use pyinstaller for executables
https://github.com/CS-4820-Library-Project/COUNTER-5-Report-Tool/blob/master/docs/pyinstaller-how-to.md

## Setup Instructions (Windows)
- Install Python 3.8.2 [https://www.python.org/ftp/python/3.8.2/python-3.8.2-amd64.exe]
### Add Python to environment variables [https://datatofish.com/add-python-to-windows-path/]
- Open control panel
- System and Security -> System -> Advanced System Settings -> Advanced -> Environment Variables
- System Variables: Click on Path, Click Edit...
- Click Browse
- Browse to where python is downloaded, by default: C:\Users\USER_NAME\AppData\Local\Programs\Python\Python38

- Add another variable in the same way that we just did. 
- Except this time set the filepath to C:\Users\apjm4\AppData\Local\Programs\Python\Python38\Scripts
Python should now be accessible in Windows Command Prompt. 
Open command prompt and type Python --version. This should return the version of python that is installed.
If not the path may be wrong or python was not installed correctly.

type pip -v into command prompt, this should return the version of PIP that is installed with Python.

### Download the project from Github
- Close and re-open command prompt
- type cd
- Open the location you downloaded the project to and drag the folder into the command prompt window
- Your command prompt window should now show "C:\Users\NAME>cd C:\Users\NAME\DOWNLOAD_LOCATION
- Hit ENTER
- type: pip install -r requirements.txt
- This installs all the neccessary packages to run the project.

### Run the project
- Type: python maindriver.py
- A User-Interface window should open with the project working
- To run the project from now on, you only need to double click or right click and open MainDriver.py and the project should open



## Developer Setup (using Anaconda and Pycharm)
- Download and install Anaconda: https://www.anaconda.com/distribution/#download-section
- Download and install PyCharm: https://www.jetbrains.com/pycharm/download/

### Using Anaconda
- Launch Anaconda Navigator (Anaconda GUI)
- Go to Environments on the left pane
- Search for and ensure that pyqt and requests packages are installed

### Using PyCharm
- Download and open the project using PyCharm
- Go to File->Settings
- On the left pane, select Project->Project Interpreter
- Click the cog wheel on the right of the project interpreter drop down, click add
- Choose Existing environment and set the location to anaconda_install_location/python.exe, OK, OK
- Allow the IDE to complete set up then launch the program from MainDriver.py. There should be a play icon next to the line "if __name__ == "__main__":"
- We Good To Go!


