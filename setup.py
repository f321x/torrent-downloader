from setuptools import setup

setup(
    name='TorrentDownloader',
    version='1.0.0',
    description='A Torrent Downloader with a graphical user interface built using Tkinter and libtorrent',
    author='Your Name',
    author_email='your_email@example.com',
    py_modules=['torrent_downloader_gui'],
    install_requires=[
        'python-libtorrent'
    ],
    entry_points={
        'console_scripts': [
            'torrent-downloader = torrent_downloader_gui:main'
        ]
    }
) 