from setuptools import setup, find_packages

setup(
    name="atmosync-jillani",
    version="0.1.0",
    description="AtmoSync: Micro-Climate Arbitrage Analytics Pipeline",
    author="jillani",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
)