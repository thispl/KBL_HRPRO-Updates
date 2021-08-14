from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in kbl/__init__.py
from kbl import __version__ as version

setup(
	name="kbl",
	version=version,
	description="Customizations for KBL",
	author="TEAMPRO",
	author_email="abdulla.pi@groupteampro.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
