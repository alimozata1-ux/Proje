from setuptools import find_packages, setup

setup(
    name="super3d",
    version="0.2.0",
    description="Pygame tabanlı modüler 3D wireframe grafik kütüphanesi",
    author="Super3D Contributors",
    packages=find_packages(),
    install_requires=["pygame>=2.5.0"],
    python_requires=">=3.9",
)
