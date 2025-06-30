#!/usr/bin/env python3
"""
Setup script for Simple Bitcoin Wallet Recovery
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simple-bitcoin-wallet-recovery",
    version="1.0.0",
    author="Josh",
    description="Recover Bitcoin from old wallet.dat files - successfully recovered $13k+!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/simple-bitcoin-wallet-recovery",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "bsddb3>=6.2.9",
        "ecdsa>=0.19.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "secure": ["cryptography>=3.4.8"],
        "qr": ["qrcode[pil]>=7.3"],
        "dev": ["pytest>=7.0.0", "black>=22.0.0", "flake8>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "bitcoin-recovery=recovery_wizard:main",
            "wallet-detect=lib.wallet_detector:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)