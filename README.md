# Intro to MEEGsim

This repository contains the materials of the workshop on how to use the MEEGsim package for simulating ground-truth M/EEG activity and connectivity patterns.

## Preparing for the workshop

1. [Optional, but recommended] Create an environment of your preference (
    [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)|
    [venv](https://docs.python.org/3/library/venv.html)|
    [uv](https://docs.astral.sh/uv/)|
    etc.
) to have no conflicts with other packages installed on your system.

2. Activate the environment and install the prerequisites. If you plan to use
Jupyter Notebook during the tutorial, use the following command:

    ```bash
    pip install -e .[jupyter]
    ```

    Otherwise, the command below should suffice if you plan to work with plain Python files:

    ```bash
    pip install -e .
    ```

3. Depending on your selection in step 2, either launch the Python script
`00_test_install/test_install.py` or run all steps in the `00_test_install/test_install.ipynb` notebook.

    **NOTE:** On Windows, you might need to run the Python script using `python -X utf8 00_test_install/test_install.py` to ensure that all symbols are displayed correctly.

4. If you see "✅ Everything seems to work!" in the output, all necessary packages were installed correctly, and you're well prepared for the main part of the workshop! If any errors occurred, feel free to contact the workshop instructors.
