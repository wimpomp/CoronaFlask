import os
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='coronaflask',
    version='2022.1.0',
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
    scripts=[os.path.join('bin', script) for script in
             os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin'))],
)
