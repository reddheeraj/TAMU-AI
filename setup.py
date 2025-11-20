"""Setup configuration for TAMU Chat API Python Library."""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="tamu-chat",
    version="0.1.0",
    author="Dheeraj Mudireddy",
    description="A Python library for interacting with the TAMU Chat AI API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/reddheeraj/TAMU-AI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=[
        "requests>=2.32.5",
        "python-dotenv>=1.2.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
    },
    keywords="tamu chat api llm openai chatgpt",
    project_urls={
        "Bug Reports": "https://github.com/reddheeraj/TAMU-AI/issues",
        "Source": "https://github.com/reddheeraj/TAMU-AI",
        "Documentation": "https://github.com/reddheeraj/TAMU-AI#readme",
    },
)

