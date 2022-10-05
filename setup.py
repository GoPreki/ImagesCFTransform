#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='image_transform',
    version='1.0.0',
    author='Preki',
    author_email='david@preki.com',
    packages=['image_transform'],
    url='https://preki.com',
    download_url='https://github.com/GoPreki/ImagesCFTransform',
    license='MIT',
    description='Python library for transforming images (resizing, changing extension). Built on top of Pillow',
    long_description='Python library for transforming images (resizing, changing extension). Built on top of Pillow',
    install_requires=[
        'Pillow==9.2.0',
        'pillow-avif-plugin==1.2.2',
    ],
)
