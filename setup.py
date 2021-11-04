try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

import re
import os
from typing import List

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(CURRENT_DIR, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


def parse_requirements(path: str) -> List[str]:
    with open(os.path.join(CURRENT_DIR, path)) as f:
        return [
            line.rstrip() for line in f if not (line.isspace() or line.startswith("#"))
        ]


VERSIONFILE = "mle_monitor/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))
git_tar = f"https://github.com/mle-infrastructure/mle-monitor/archive/v{verstr}.tar.gz"


setup(
    name="mle_monitor",
    version=verstr,
    author="Robert Tjarko Lange",
    author_email="robertlange0@gmail.com",
    description="Machine Learning Experiment Resource Monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mle-infrastructure/mle-monitor",
    download_url=git_tar,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    python_requires=">=3.6",
    install_requires=parse_requirements(os.path.join(CURRENT_DIR, "requirements.txt")),
)
