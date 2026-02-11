from setuptools import find_packages, setup
from typing import List

gsg = '-e .'

def get_requirements(file_path: str) -> List[str]:
    """Read requirements from file and return as list."""
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.replace("\n", "").strip() for req in requirements]
        if gsg in requirements:
            requirements.remove(gsg)
    return requirements


setup(
    name='credit_card_fraud_detection',
    version='0.0.2',
    author='Ganesh',
    author_email='tarigondaganesh1234@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
)