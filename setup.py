from setuptools import setup

setup(
    name='pubkeeper.brew.google_cloud_pubsub',
    version='0.1.0',
    url='https://pubkeeper.com',
    description='Brew, Consume',
    keywords=['pubkeeper', 'python-brew-google-cloud-pubsub'],
    packages=[
        'pubkeeper.brew.google_cloud_pubsub'
    ],
    package_dir={'': 'src'},
    install_requires=[
        'pubkeeper.client~=1.0',
        'google-cloud-pubsub~=0.33',
    ],
    author='Matt Dodge',
    author_email='mdodge@n.io',
)
