from distutils.core import setup
setup(
    name='stargazing',         # How you named your package folder (MyLib)
    packages=['stargazing'],   # Chose the same as "name"
    version='0.1.4',      # Start with a small number and increase it with every change you make
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    license='MIT',
    # Give a short description about your library
    description='A terminal user interface study/work app',
    author='mtu2',                   # Type in your name
    # author_email='',      # Type in your E-Mail
    # Provide either the link to your github or to your website
    url='https://github.com/mtu2/stargazing',
    # I explain this later on
    download_url='https://github.com/mtu2/stargazing/archive/refs/tags/v0.1.4.tar.gz',
    # Keywords that define your package best
    keywords=['terminal', 'python', 'study', 'work', 'pomodoro'],
    install_requires=[            # I get to this in a second
        'ansicon',
        'blessed',
        'jinxed',
        'pafy',
        'python-vlc',
        'six',
        'toml',
        'ujson',
        'wcwidth',
        'youtube-dl',
    ],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 3 - Alpha',
        # Define that your audience are developers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': [
            'stargazing=stargazing.main:run_app',
        ],
    },
)
