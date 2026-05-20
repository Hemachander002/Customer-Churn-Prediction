from setuptools import setup, find_packages

HYPHEN_E_DOT = '-e .'

def get_requirements(file_path) -> list[str]:
    with open(file_path, 'r') as file:
        requirements = file.read().splitlines() 
    if HYPHEN_E_DOT in requirements:
        requirements.remove(HYPHEN_E_DOT)
    return requirements

setup(
    name='Customer Churn Prediction Report Engine',
    version='1.0.0',
    description='A report engine for customer churn prediction using machine learning models.',
    author='Hemachander002',
    author_email= "sathyameena75@gmail.com",
    packages=find_packages(),
    install_requires= get_requirements("requirements.txt"),)