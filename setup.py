from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in omniflo_lead/__init__.py
from omniflo_lead import __version__ as version

setup(
	name="omniflo_lead",
	version=version,
	description="Omniflo Lead",
	author="Omniflo",
	author_email="vivekchole@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
