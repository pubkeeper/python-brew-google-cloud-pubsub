from setuptools import setup

setup(
    name='pubkeeper.brew.<yourbrew>',
    version='0.0.0',
    url='<yoururl>',
    description='Brew, Consume',
    keywords=['pubkeeper', 'python-brew-<yourbrew>'],
    packages=[
        'pubkeeper.brew.<yourbrew>'
    ],
    package_dir={'': 'src'},
    install_requires=[
        'pubkeeper.client~=1.0',
    ],
    author='<yourname>',
    author_email='<youremail>',
)
