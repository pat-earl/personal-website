from setuptools import setup 

setup(
    name='personal-website',
    packages=['personal-website'],
    include_package_data=True,
    install_requires=[
        'flask',
        'pymongo',
        'beautifulsoup4'
    ]
)