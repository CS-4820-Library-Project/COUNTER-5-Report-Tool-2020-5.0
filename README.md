# Libly

This project is written is Python 3.7. Anaconda is used to manage the packages and environment used in this project, everything is up to date.
The required packages are PyQt5 and requests.

The project's UI is developed using PyQt

# Setup Instructions
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



# Developer Setup (using Anaconda and Pycharm)
- Download and install Anaconda: https://www.anaconda.com/distribution/#download-section
- Download and install PyCharm: https://www.jetbrains.com/pycharm/download/

## Using Anaconda
- Launch Anaconda Navigator (Anaconda GUI)
- Go to Environments on the left pane
- Search for and ensure that pyqt and requests packages are installed

## Using PyCharm
- Download and open the project using PyCharm
- Go to File->Settings
- On the left pane, select Project->Project Interpreter
- Click the cog wheel on the right of the project interpreter drop down, click add
- Choose Existing environment and set the location to anaconda_install_location/python.exe, OK, OK
- Allow the IDE to complete set up then launch the program from MainDriver.py. There should be a play icon next to the line "if __name__ == "__main__":"
- We Good To Go!


