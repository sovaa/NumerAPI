from setuptools import setup, find_packages

numerapi_version = '0.3.0'

setup(
    name="numerapi",
    version=numerapi_version,
    description="Wrapper for the Numerai API",
    url='https://github.com/numerai/NumerAPI',
    license='Apache 2',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "requests",
        "zope.interface",
    ],
    test_requires=[
        "pytest",
    ]
)
