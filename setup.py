from setuptools import setup, find_packages

setup(
    name="predictive_maintenance_project",
    version="0.1.0",
    # Explicitly treat "src" as a package, map it to the src directory
    #packages=["src"] + find_packages(where="src"),
    packages=find_packages(include=["src", "src.*"]),
    package_dir={"src": "src"},  # Tell setuptools "the package src lives in ./src"
    py_modules=["extract_features", "train"],  # Top-level .py modules
    python_requires=">=3.8",
    install_requires=[
        "mlflow",
        "prefect",
        
    ],
)
