import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()

setup(
    name = "ReCaptchaBreaker",
    version = "0.1.0",
    author = "Hackear",
    description = ("An easy tool to automatically crack Google's ReCaptcha, with near-human performance."),
    license = "MIT",
    keywords = "python recaptcha google captcha bot captchabreak",
    package_dir={'recaptchabreaker': 'src'},
    packages=['recaptchabreaker'],
    long_description=read('README.md'),
)