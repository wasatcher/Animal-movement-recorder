import sys
from cx_Freeze import setup, Executable
 
include_files = ['delete.png', 'leave.png', 'others.png', 'pause.png', 'preparing.png', 'touch.png']
 
build_exe_options = {'packages': ['Pmw'], 
                     'excludes': [],
                     'include_files':include_files
                     }

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = 'timecounter',
        version = '1.0',
        description = 'Pig-ball interation timecounter',
        options = {'build_exe': build_exe_options},
        executables = [Executable('timecounter_escape_enter.py')])