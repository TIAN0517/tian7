from setuptools import setup, find_packages

setup(
    name="bingo_game",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytest>=8.3.5",
        "pytest-qt>=4.4.0",
        "PyQt5>=5.15.9",
        "PyJWT>=2.8.0",
        "SQLAlchemy>=2.0.27",
        "python-dotenv>=1.0.1",
    ],
    python_requires=">=3.8",
) 