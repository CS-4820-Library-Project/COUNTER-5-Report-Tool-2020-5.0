import PyInstaller.__main__
from os import path

if __name__ == "__main__":
    PyInstaller.__main__.run([
        '--name=Counter 5 Report Tool',
        '--onefile',
        '--console',
        '--icon=%s' % path.join('main_icon.ico'),
        path.join('MainDriver.py'),
    ])
