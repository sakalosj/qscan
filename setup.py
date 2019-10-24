from setuptools import setup, find_packages
setup(
    name="qualys",
    version="0.7",
    package_dir={"": "src"},
    # packages=find_packages(),
    packages=['qualys'],
    # scripts=['say_hello.py'],
    # scripts=['say_hello.py'],
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['atomicwrites >= 1.2.1',
                      'attrs >= 18.2.0',
                      'certifi >= 2018.11.29',
                      'chardet >= 3.0.4',
                      'colorama >= 0.4.1',
                      'coverage >= 4.5.2',
                      'idna >= 2.8',
                      'mock >= 2.0.0',
                      'more-itertools >= 5.0.0',
                      'pbr >= 5.1.1',
                      'pluggy >= 0.8.1',
                      'py >= 1.7.0',
                      'PyMySQL >= 0.9.3',
                      'pytest >= 4.1.1',
                      'pytest-cov >= 2.6.1',
                      'requests >= 2.21.0',
                      'six >= 1.12.0',
                      'urllib3 >= 1.24.1',
                      ],


    # metadata to display on PyPI
    author="Jan Sakalos",
    author_email="jan.sakalos@dhl.com",
    description="QualysScan app",
    license="to be determined",
    keywords="qualys patch security",
    # url="http://example.com/HelloWorld/",   # project home page, if any
    # project_urls={
    #     "Bug Tracker": "https://bugs.example.com/HelloWorld/",
    #     "Documentation": "https://docs.example.com/HelloWorld/",
    #     "Source Code": "https://code.example.com/HelloWorld/",
    # }

    # could also include long_description, download_url, classifiers, etc.
)