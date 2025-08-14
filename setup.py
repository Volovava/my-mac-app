from setuptools import setup

APP = ['myscript.py']
OPTIONS = {
    'argv_emulation': True,
    # 'iconfile': 'myicon.icns',  # если хочешь иконку
    'arch': 'universal2',  # создаст приложение для Intel + ARM
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
