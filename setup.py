import os

from setuptools import setup, find_packages

here =      os.path.abspath(os.path.dirname(__file__))
readme =    open(os.path.join(here, 'README.rst')).read()
changes =   open(os.path.join(here, 'CHANGES.rst')).read()

requires = []

setup(
    name='mdx_sections',
    version='0.1',
    description="Python-Markdown extension to add a small amount of structure to Markdown documents.",
    long_description="{readme}\n\n{changes}".format(readme=readme, changes=changes),
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Jesse Dhillon',
    author_email='jesse@dhillon.com',
    url='http://github.com/jessedhillon/mdx_sections',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='mdx_sections',
    install_requires = requires,
)
