from setuptools import setup

setup(
    name='JestingLang',
    version='0.0.0a9',
    author='itrufat',
    description='A compiler for the minimalist spreadsheet language Jesting',
    long_description='A compiler + a few node navigators (including an interpreter) for a minimalist language intended to copy the most basic functionalities found in spreadsheet-applications called JestingLang. It was created to be used with Jesting, a spreadsheet terminal tool.',
    long_description_content_type='text/markdown',
    url='https://github.com/itruffat/JestingLang',
    packages=['JestingLang',
              'JestingLang.Core',
                  'JestingLang.Core.JParsing', 'JestingLang.Core.JVisitors', 'JestingLang.Core.JDereferencer',
              'JestingLang.JestingScript',
                  'JestingLang.JestingScript.JParsing', 'JestingLang.JestingScript.JVisitors',
                  'JestingLang.JestingScript.JDereferencer',
              'JestingLang.Misc',
                  'JestingLang.Misc.JLogic', 'JestingLang.Misc.JTesting'],
    package_dir={'': 'src'},
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
