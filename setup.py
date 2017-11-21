from setuptools import setup

setup(name='BBMQ',
      version='1.0.0',
      author='Rajdeep Mukherjee',
      author_email='rajdeep.mukherjee295@gmail.com',
      description='Message queuing for noobs',
      packages=['bbmq'],
      entry_points={
          'console_scripts': [
              'bbmq = bbmq.__main__:main'
          ]
      },
      )