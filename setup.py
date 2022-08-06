import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scada_data_analysis",
    version="1.0.3",
    author="Abiodun Olaoye",
    author_email="abiodunolaoye8@gmail.com",
    description="A set of tools for enabling wind energy data analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abbey2017/wind-energy-analytics",
    project_urls={
        "Bug Tracker": "https://github.com/abbey2017/wind-energy-analytics/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(exclude=["test"]),
    python_requires=">=3.6",
    install_requires=['pandas', 'matplotlib'],
    keywords = ['power-curve-filtering', 'scada-data-analytics', 'wind-energy'],
)