from setuptools import setup, find_packages

setup(
    name="wit-cli",
    version="0.1",
    py_modules=["cli", "core", "ui"],  # חובה להוסיף כאן את ui
    packages=find_packages(),
    install_requires=[
        "click",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "wit=cli:main",
        ],
    },
)