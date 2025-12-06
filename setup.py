from setuptools import setup, find_packages

setup(
    name="sump",  # Name used for import (e.g., "import my_package")
    version="0.0.1",
    packages=find_packages(where="src"),  # Finds packages under src/
    package_dir={"": "src"},  # Tells setuptools packages are in src/
    install_requires=[
        "blinkt == 0.1.2",
        "buttonshim == 0.0.2",
        "filelock == 3.20.0",
        "paho-mqtt == 2.1.0",
        "pyserial == 3.5",
        "python-dotenv == 1.1.1",
        "RPi.GPIO == 0.7.1",
        "SecretStorage == 3.5.0",
        "keyring == 25.7.0"
    ],  # Add dependencies here (e.g., "requests>=2.25.0")
)