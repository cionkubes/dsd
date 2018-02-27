from setuptools import setup, find_packages

setup(name='dsd',
      version='0.1',
      description='Yaml profiles for docker stack deploy',
      url='https://github.com/cionkubes/dsd',
      author='Erlend Tobiassen',
      author_email='erlentob@stud.ntnu.no',
      license='GPL-3.0',
      install_requires=[
          'PyYaml',
      ],
      packages=find_packages(),
      entry_points = {
          'console_scripts': ['dsd=dsd.command_line:main'],
      }
)