from setuptools import setup, find_packages
import sys

setup(
    name="torrent-downloader-python",
    version="1.1.6",
    description='A Torrent Downloader with a graphical user interface built using Tkinter and libtorrent',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Steven Yan',
    author_email='yulong.yan@uqconnect.edu.au',
    url='https://github.com/stevenbtc/torrent-downloader',
    packages=find_packages(),
    py_modules=['torrent_downloader_gui'],
    install_requires=[
        'libtorrent>=2.0.0'
    ],
    entry_points={
        'console_scripts': [
            'torrent-downloader-python = torrent_downloader_gui:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Topic :: Internet :: File Transfer Protocol (FTP)',
    ],
    python_requires='>=3.8',
) 