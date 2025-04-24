#!/usr/bin/env python3
"""
Setup script for AI Hub Content System.
"""

from setuptools import setup, find_packages

setup(
    name="ai-hub-content",
    version="0.1.0",
    description="AI Hub Content Creation System",
    author="AI Vibe Collective",
    author_email="monem.naifer@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "supabase",
        "python-dotenv",
        "google-generativeai",
        "pandas",
        "matplotlib",
        "seaborn",
    ],
    entry_points={
        "console_scripts": [
            "ai-hub=main:main",
        ],
    },
)
