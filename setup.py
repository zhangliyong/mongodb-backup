from setuptools import setup

setup(
        name='mongodb-backup',
        version='0.1.3',
        py_modules=['backup', 'utils'],
        entry_points={
            'console_scripts': [
                'mongodbbackup=backup:main',
                ]
            },
        url='http://github.com/zhangliyong/mongodb-backup',
        license='BSD',
        author='Lyon Zhang',
        author_email='lyzhang87@gmail.com',
        install_requires=['click >= 3.0', 'pymongo >= 2.3'],
        description='A tool to backup mongodb',
        long_description=open('README.rst').read(),
)
