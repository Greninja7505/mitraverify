"""
Setup script for MitraVerify
"""
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mitraverify",
    version="0.1.0",
    author="MitraVerify Team",
    author_email="team@mitraverify.com",
    description="AI-powered misinformation detection system for Indian digital ecosystem",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mitraverify/mitraverify",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest", "black", "flake8", "mypy"],
        "docs": ["sphinx", "sphinx-rtd-theme"],
    },
    entry_points={
        "console_scripts": [
            "mitraverify=src.api.main:main",
        ],
    },
)