import setuptools

setuptools.setup(
    name="czfacsautomation",
    version="0.0.1",
    author="Diane M. Wiener",
    author_email="diane.wiener@czbiohub.org",
    description="Automated control of the Sony SH800S",
    url="https://github.com/czbiohub/2023-facs-automation-pub",
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*","tests.*", "tests"]
    ),
    python_requires='==3.7.8',
    install_requires=[
        'matplotlib==3.4.2',
        'numpy>=1.20.3',
        'opencv-python>=4.5.2.54',
        'pandas>=1.2.4',
        'Pillow>=8.2.0',
        'psutil>=5.8.0',
        'pyautogui>=0.9.52',
        'pyinstrument>=3.4.2',
        'pynput==1.7.3',
        'pyperclip>=1.8.2',
        'pyserial>=3.5',
        'pytesseract>=0.3.8',
        'scikit-image>=0.18.1',
        'seaborn>=0.11.1',
        'slack_sdk>=3.8.0',
        'zaber_motion>=2.3.2'
    ],
    test_suite="tests",
    classifiers=[
        "CZ Biohub :: Bioengineering",
    ],
)
