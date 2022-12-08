from setuptools import setup, find_packages


setup(
    name="slack",
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'aiohttp==3.6.2',
        'async-timeout==3.0.1',
        'attrs==19.3.0',
        'certifi==2022.12.7',
        'chardet==3.0.4',
        'Click==7.0',
        'colorama==0.4.3',
        'idna==2.8',
        'multidict==4.7.4',
        'Pillow==7.0.0',
        'pyfiglet==0.8.post1',
        'reportlab==3.5.34',
        'slackclient==2.5.0',
        'typing-extensions==3.7.4.1',
        'urllib3==1.25.8',
        'yarl==1.4.2'
        ],
    entry_points='''
        [console_scripts]
        slack=slackcli.cli:cli
    ''',
)