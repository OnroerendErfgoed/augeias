import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'HISTORY.rst')) as f:
    HISTORY = f.read()

requires = [
    'pyramid',
    'pairtree'
    ]

setup(name='augeias',
      version='0.1.0',
      description='augeias',
      long_description=README + '\n\n' + HISTORY,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="augeias",
      entry_points="""\
      [paste.app_factory]
      main = augeias:main
      """,
      )
