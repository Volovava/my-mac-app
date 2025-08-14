from setuptools import setup

APP = ['gui.py']  # указываем твой скрипт
OPTIONS = {
    'argv_emulation': True,
    'iconfile': None,
    'arch': 'universal2',  # поддержка Intel и ARM
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
