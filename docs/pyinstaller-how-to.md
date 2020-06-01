# How to create COUNTER 5 Report Tool's executable

* Install python
* Install pip
* Install pyinstaller (pip install pyinstaller)


Before starting the process below, make sure to delete your alldata folder as anything included in it will be included in the EXE file.


### Creating the executable in terminal
1. Open terminal/Command Prompt
2. cd to your projectDirectory
3. Run: *pip install -r requirements.txt* 
4. Run: *pip show validators*
This will show the validators package location.
5. Run: pyi-makespec --paths=DirectoryWithValidatorsPackage maindriver.py

6. Run pyinstaller
* Windows: Run: pyinstaller --onefile MainDriver.py -n "Counter 5 Report Tool" -i main_icon.ico
* macOS: Run: pyinstaller --onefile MainDriver.py --windowed -n "Counter 5 Report Tool" -i main_icon.ico
* UNIX: Run:  pyinstaller --onefile MainDriver.py -n "Counter 5 Report Tool" -i main_icon.ico

Check in the project directory, under the folder named dist. There should now be an .exe or .app file. Double click the file to open.

If you receive an error about missing modules make sure that you ran pyi-makespec and gave the right path. If there are other modules other than validators that the exe says it is missing you will need to include their paths as well.
