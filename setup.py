from setuptools import setup, find_packages

p  = find_packages("src")

setup(
    name='JestingLang',
    version='0.0.0a3',
    author='itrufat',
    description='A compiler for the minimalist spreadsheet language Jesting',
    long_description='A compiler + a few node navigators (including an interpreter) for a minimalist language intended to copy the most basic functionalities found in spreadsheet-applications called JestingLang. It was created to be used with Jesting, a spreadsheet terminal tool.',
    long_description_content_type='text/markdown',
    #url='https://github.com/your-username/your-repo',
    #packages=['src'],
    packages=['JestingLang', 'JestingLang.JParsing', 'JestingLang.JVisitors', 'JestingLang.Misc',
              'JestingLang.Misc.JLogic', 'JestingLang.Misc.JContext', 'JestingLang.Misc.JExample'],
    package_dir={'': 'src'},
    #packages=find_packages('src'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=[
        'ply',
    ],
)
