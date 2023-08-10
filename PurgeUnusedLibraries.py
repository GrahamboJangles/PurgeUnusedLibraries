import os
import time
import subprocess
from tqdm import tqdm

# The time in seconds after which a package is considered unused
UNUSED_THRESHOLD = 30 * 24 * 60 * 60

# Get the current time in seconds
current_time = int(time.time())

# Get the output of the `pip list` command
installed_packages = subprocess.check_output(['pip', 'list']).decode().strip().split('\n')

# Strip the header and footer from the output to get a list of packages
installed_packages = [package.split()[0] for package in installed_packages[2:-3]]

for package in tqdm(installed_packages, desc='Checking packages', unit='package'):
    # Get the location of the package using the `pip show` command
    try:
        package_location = subprocess.check_output(['pip', 'show', package]).decode().strip().split('\n')
        package_location = [line.split(': ')[1].strip() for line in package_location if line.startswith('Location:')][0]
    except subprocess.CalledProcessError:
        print(f'Package {package} not found!')
        continue

    # Check the modification time of the package
    try:
        package_time = int(os.path.getmtime(package_location))
    except OSError:
        print(f'Error accessing location of package {package}: {package_location}')
        continue

    # If the package hasn't been used in the past UNUSED_THRESHOLD seconds, ask the user if they want to uninstall it
    if current_time - package_time > UNUSED_THRESHOLD:
        response = input(f'The package {package} has not been used in the past {UNUSED_THRESHOLD // (24 * 60 * 60)} days. Do you want to uninstall it? (y/n): ')
        if response.lower() == 'y':
            subprocess.call(['pip', 'uninstall', '-y', package])
