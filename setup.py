from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in enci/__init__.py
from enci import __version__ as version

setup(
	name='enci',
	version=version,
	description='This App will add to your ErpNext platform custom integrations and will make your ErpNext white label',
	author='Artyk Basarov',
	author_email='info@artyk.co.uk',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
