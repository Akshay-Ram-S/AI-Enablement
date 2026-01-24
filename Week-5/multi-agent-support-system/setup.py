"""Setup configuration for the multi-agent support system."""

from setuptools import setup, find_packages

setup(
    name="multi-agent-support-system",
    version="1.0.0",
    description="A dynamic multi-agent support system with intelligent routing",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "python-dotenv",
        "langchain",
        "langgraph", 
        "langchain-aws",
        "langchain-tavily",
        "langchain-community",
        "langchain-text-splitters",
        "langchain-chroma",
        "pypdf",
        "tavily-python",
        "chromadb",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-mock>=3.12.0",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "unittest-mock>=1.0.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "multi-agent-support=main:main_loop",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
