from setuptools import setup

setup(
        name='mongodb-backup',
        version='0.1',
        py_modules=['backup'],
        entry_points={
            'console_scripts': [
                'mongodbbackup=backup:main',
                ]
            },
        url='http://github.com/zhangliyong/mongodb-backup',
        license='BSD',
        author='Liyong Zhang',
        author_email='lyzhang87@gmail.com',
        description='A tool to backup mongodb',
)
