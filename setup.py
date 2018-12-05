import os

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

this = os.path.dirname(os.path.realpath(__file__))

def read(name):
    with open(os.path.join(this, name)) as f:
        return f.read()
setup(
    name='quickstart',
    version='1.1',
    description='description',
    long_description=readme,
    author='Krzysztof Kosman',
    author_email='krzysztof.kosman@gmail.com',
    url='https://github.com/kkosman/quickstart.git',
    packages=['sensormodules'],
    install_requires=read('requirements.txt'),
    include_package_data=True,
    zip_safe=True,
    licence='BSD - 3',
    keywords='example app snap linux ubuntu',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English'
    ],
    scripts=['src/writetest.py','src/synchronize.py']
)