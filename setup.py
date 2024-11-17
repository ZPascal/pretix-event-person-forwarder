import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    coverage_string: str = "![Coverage report](https://github.com/ZPascal/pretix_event_person_forwarder/blob/main/docs/coverage.svg)"
    long_description: str = fh.read()

long_description = long_description.replace(coverage_string, "")

setuptools.setup(
    name="pretix-event-person-forwarder",
    version="0.1.0",
    author="Pascal Zimmermann",
    author_email="info@theiotstudio.com",
    description="A Pretix event person forwarder functionality",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZPascal/pretix-event-person-forwarder",
    project_urls={
        "Source": "https://github.com/ZPascal/pretix-event-person-forwarder",
        "Bug Tracker": "https://github.com/ZPascal/pretix-event-person-forwarder/issues",
        "Documentation": "https://zpascal.github.io/pretix-event-person-forwarder/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
    ],
    license="Apache-2.0 License",
    packages=["pretix_event_person_forwarder"],
    install_requires=["httpx"],
    extras_require={
        "http2": ["httpx[http2]"],
    },
    tests_require=["pytest-httpx", "pytest"],
    python_requires=">=3.8",
)
