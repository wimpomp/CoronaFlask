import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='coronaflask',
    version='2022.5.0',
    author='Wim Pomp',
    author_email='wimpomp@gmail',
    description='Flask for a corona graph plotting website.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=['waitress', 'flask', 'markupsafe', 'pandas', 'numpy', 'matplotlib', 'requests', 'mpld3'],
)
