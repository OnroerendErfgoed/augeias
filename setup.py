import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'HISTORY.rst')) as f:
    HISTORY = f.read()

requires = [
    'pyramid',
    'pairtree',
    'python-magic',
    'pyramid_rewrite'
    ]

setup(name='augeias',
      version='0.3.0',
      description='Augeias. Stores your files.',
      long_description=README + '\n\n' + HISTORY,
      classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Programming Language :: Python :: 2.7",
      ],
      author='Flanders Heritage Agency',
      author_email='ict@onroerenderfgoed.be',
      url='https://augeias.readthedocs.org',
      keywords='web pyramid digital object storage',
      license='GPLv3',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="augeias",
      entry_points="""\
      [pyramid.scaffold]
      augeias = augeias.scaffolds:AugeiasTemplate
      [paste.app_factory]
      main = augeias:main
      """,
      )
