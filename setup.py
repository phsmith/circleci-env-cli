from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name='circleci-env-cli',
    version='0.1.0',
    author = "Phillipe Smith",
    author_email = "phsmithcc@gmail.com",
    description = "CLI tool for manage CircleCI contexts and environment vars",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    license = "MIT",
    keywords = "circleci cli api",
    url = "https://github.com/phsmith/circleci-env-cli",
    py_modules=['circleci_env_cli'],
    python_requires='>=3.7',
    install_requires=[requirements],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'circleci-env-cli = circleci_env_cli:cli',
        ],
    },
)
