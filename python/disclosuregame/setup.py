from setuptools import setup

setup(name='disclosuregame',
        version='0.1.4',
        description='Simulator for the disclosure game between midwives and women.',
        entry_points={'console_scripts': ['disclosure-game=disclosuregame.run:main']},
        url='https://github.com/greenape/disclosure-game',
        author='Jonathan Gray',
        author_email='j.gray@soton.ac.uk',
        license='MPL',
        packages=['disclosuregame', 'disclosuregame.Agents', 'disclosuregame.Measures', 'disclosuregame.Games', 'disclosuregame.Util'],
        include_package_data=True,
        zip_safe=False
)