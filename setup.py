from setuptools import setup, find_packages

setup(
    name='vino',
    version='0.1.0',
    description='A validation library',
    url='http://github.com/ekoka/vino',
    author='Michael Ekoka',
    author_email='verysimple@gmail.com',
    license='MIT',
    #packages=['vino', 'vino.api', 'vino.processors']
    packages=find_packages(exclude=['tests*']),
)
