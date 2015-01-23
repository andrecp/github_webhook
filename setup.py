from setuptools import setup

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_tm',
    'gunicorn',
    'gevent',
    'grequests',
]

setup(name='webhook',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = webhook.main:main
      """,
)
