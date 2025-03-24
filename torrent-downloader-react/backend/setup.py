from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="torrent-downloader-react",
    version="1.1.9",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.0.0",
        "libtorrent>=2.0.0",
        "pytest>=8.0.0",
        "httpx>=0.27.0"
    ],
    entry_points={
        "console_scripts": [
            "torrent-downloader-react=torrent_downloader.server:main",
        ],
    },
    author="Steven Yan",
    author_email="yulong.yan@uqconnect.edu.au",
    description="A high-performance, React-based BitTorrent client with an intuitive interface for seamless file downloading",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="torrent, downloader, p2p, bittorrent, libtorrent",
    url="https://github.com/stevenbtc/torrent-downloader",
    project_urls={
        "Bug Tracker": "https://github.com/stevenbtc/torrent-downloader/issues",
        "Documentation": "https://github.com/stevenbtc/torrent-downloader#readme",
        "Source Code": "https://github.com/stevenbtc/torrent-downloader",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: FastAPI",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "torrent_downloader": ["static/*", "static/**/*"],
    },
) 