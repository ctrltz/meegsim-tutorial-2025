# Intro to MEEGsim

This repository contains the materials of the workshop on how to use the MEEGsim package for simulating ground-truth M/EEG activity and connectivity patterns.

## Folder structure

The following folders contain the materials of the workshop:

* `00_test_install`: small notebook/script for testing that all packages were installed properly when [preparing for the workshop](#preparing-for-the-workshop)
* `01_demo`: notebook/script that will be discussed during the demo part of the workshop
* `02_hands_on`: notebooks/scripts with exercises for the hands-on part of the workshop (**WIP**):
    * `patch_cancellation`: investigate and visualize how the leadfield of a patch source changes depending on its area
* `_solutions`: suggested solutions for the `FILL_ME` parts of the scripts (sometimes, just one of the many possible options)
* `src/meegsim_tutorial`: helper functions that are used in the notebooks/scripts (feel free to check their code if you want to understand them better but this should not be necessary to follow)

## Preparing for the workshop

1. [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)/[fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo?versionId=free-pro-team%40latest&productId=repositories&restPage=creating-and-managing-repositories%2Ccloning-a-repository) the repository to your PC or download its contents ("Download ZIP" in the screenshot below). If you decide to clone the repository and want to commit your changes, consider doing that in a separate branch to always be able to pull the latest changes (e.g., bugfixes).

![Screenshot of the "Code" button which allows one to clone or download the repository](assets/clone_or_download.png)

2. Change your current working directory to the directory of this repository, e.g., via the command below right after cloning the repo:

    ```
    cd meegsim-tutorial-2025
    ```

3. [Optional, but recommended] Create an **empty** environment of your preference (
    [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) |
    [venv](https://docs.python.org/3/library/venv.html) |
    [uv](https://docs.astral.sh/uv/) |
    etc.) to have no conflicts with other packages installed on your system. Activate the environment.

4. Use the following command to install all prerequisites for the workshop:

    ```bash
    pip install -e .
    ```

5. Depending on your selection in step 2, open either the Python script
`00_test_install/test_install.py` or the `00_test_install/test_install.ipynb` notebook. Both the script and the notebook require you to set the path to the directory where the sample data should be stored. In this and all other scripts, parts of the script where your input is expected are marked with `FILL_ME`. Set the path and run the script / all cells of the notebook.

    **NOTE:** On Windows, you might need to run the Python script using `python -X utf8 00_test_install/test_install.py` to ensure that all symbols are displayed correctly.

6. If you see "✅ Everything seems to work!" in the output, all necessary packages were installed correctly, and you're well prepared for the main part of the workshop! If any errors occurred, feel free to contact the workshop instructors.
