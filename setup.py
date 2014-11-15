from setuptools import setup

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_tm',
    'waitress',
]

setup(name='webhook',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = webhook.main:main
      """,
)
