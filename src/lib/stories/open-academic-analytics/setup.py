from setuptools import find_packages, setup

setup(
    name="open_academic_analytics",
    packages=find_packages(exclude=["open_academic_analytics_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
