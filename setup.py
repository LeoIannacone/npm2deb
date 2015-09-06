#!/usr/bin/python3

from distutils.core import setup
from distutils.command.install_scripts import install_scripts
from npm2deb import VERSION
import shutil


class remove_extension(install_scripts):
    def run(self):
        install_scripts.run(self)
        for script in self.get_outputs():
            if script.endswith(".py"):
                shutil.move(script, script[:-3])

setup(name='npm2deb',
      version=VERSION,
      author='Leo Iannacone',
      author_email='l3on@ubuntu.com',
      description='A script to make faster and easier packaging nodejs modules',
      url='https://github.com/LeoIannacone/npm2deb',
      license='GNU GPL-3',
      scripts=['npm2deb.py'],
      packages=['npm2deb'],
      data_files=[
          ('share/man/man1', ['man/npm2deb.1']),
          ('share/doc/npm2deb', ['README.md', 'AUTHORS']),
          ('share/bash-completion/completions', [
              'etc/bash_completion.d/npm2deb'
          ])
      ],
      cmdclass={"install_scripts": remove_extension},
      )
