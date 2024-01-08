from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': [], 'include_files': ['REE_data.csv']}

import sys
base = 'Win32GUI' if sys.platform=='win32' else None



executables = [
    Executable('ree.py', base=base, target_name = 'reesearch', icon='crystal.ico'),
]




setup(name='REEsearch',
      version = '1.0',
      description = 'Searches REE minerals from webmineral database given the composition data',
      options = {
        'build_exe': build_options
        },
      executables = executables,
      )
