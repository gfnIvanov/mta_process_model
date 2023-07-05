from setuptools import find_packages, setup

with open("README.md") as file:
    read_me_description = file.read()

setup(
    name="symptom-recognition-package",
    version="0.1",
    author="Igor Ivanov",
    author_email="gfn.ivanov@gmail.com",
    long_description=read_me_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gfnIvanov/symptom_recognition",
    python_requires=">=3.9",
    license="MIT",
    packages=find_packages(),
)
