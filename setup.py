from setuptools import setup
from setuptools import find_packages


setup(name='sort-big-json',
      version='0.0.2',
      description='Sort a big json file (based on a specifc key or subkey) that does not fit in memory',
      author='YaYaB',
      author_email='bezzayassine@gmail.com',
      url='https://github.com/YaYaB/sort-big-json',
      download_url='https://github.com/YaYaB/sort-big-json',
      license='MIT',
      classifiers=['License :: MIT License',
                   'Programming Language :: Python',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX',
                   'Operating System :: Unix',
                   'Operating System :: MacOS',
                   'Programming Language :: Python :: 3.5',
                   ],
      install_requires=[],
      extras_require={},
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'sort-big-json=sort_big_json.sort_big_json:sort_big_json_cli',
              'generate-random-json-file=sort_big_json.sort_big_json:generate_random_json_file_cli'
          ]},

)