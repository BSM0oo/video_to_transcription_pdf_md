from setuptools import setup

APP = ['gui.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tkinter'],
    'plist': {
        'CFBundleName': 'Video to PDF',
        'CFBundleDisplayName': 'Video to PDF',
        'CFBundleGetInfoString': "Converting videos to PDF",
        'CFBundleIdentifier': "com.yourname.videopdf",
        'CFBundleVersion': "0.1.0",
        'CFBundleShortVersionString': "0.1.0",
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
