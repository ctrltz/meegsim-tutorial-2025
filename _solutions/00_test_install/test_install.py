import matplotlib.pyplot as plt
import mne
import os

from mne.datasets import sample

from meegsim.location import select_random
from meegsim.simulate import SourceSimulator
from meegsim.waveform import narrowband_oscillation

from meegsim_tutorial.utils import print_emoji


def main():
    ###
    # Set the path to the data
    # ========================
    #
    # During the workshop, we will use the
    # [sample dataset](https://mne.tools/stable/generated/mne.datasets.sample.data_path.html)
    # provided by MNE-Python. In the cell below, you can set the path to the directory where
    # the data should be downloaded to use `None` to proceed with the default location
    # (typically, `~/mne_data/`).
    #
    # **NOTE:** the cell below contains a `FILL_ME` placeholder - it is used through all
    # scripts/notebooks to mark places where you are expected to modify the code.
    #
    ###

    download_path = None

    ###
    # Download the dataset
    # ====================
    ###

    print_emoji(":down_arrow:  Downloading and testing the template head model")

    data_path = sample.data_path(path=download_path)
    subjects_dir = data_path / "subjects"
    src = mne.read_source_spaces(
        subjects_dir / "fsaverage" / "bem" / "fsaverage-ico-5-src.fif"
    )

    print_emoji(":check_mark_button: Download complete!")

    ###
    # Test the MEEGsim installation
    # =============================
    ###

    # Basic functionality
    print_emoji(":gear:  Testing basic functionality of MEEGsim")

    sim = SourceSimulator(src)
    sim.add_noise_sources(location=select_random, location_params=dict(n=10))
    sim.add_point_sources(
        location=select_random,
        location_params=dict(n=3),
        waveform=narrowband_oscillation,
        waveform_params=dict(fmin=8, fmax=12),
    )

    sc = sim.simulate(sfreq=250, duration=120)

    print_emoji(":check_mark_button: Basic functionality is fine!")

    # Advanced functionality
    print_emoji(":gear:  Testing advanced functionality of MEEGsim")

    sim = SourceSimulator(src)
    sim.add_noise_sources(location=select_random, location_params=dict(n=10))
    sim.add_patch_sources(
        location=select_random,
        location_params=dict(n=3),
        waveform=narrowband_oscillation,
        waveform_params=dict(fmin=8, fmax=12),
        extents=[10, 20, 50],
        subject="fsaverage",
        subjects_dir=subjects_dir,
    )

    sc = sim.simulate(sfreq=250, duration=120, random_state=1234)

    print_emoji(":check_mark_button: Advanced functionality is fine!")

    # Plotting
    print_emoji(":gear:  Testing that plotting works")

    if os.environ.get("BUILD_ENV", None) != "ci":
        brain = sc.plot(
            subject="fsaverage",
            subjects_dir=subjects_dir,
            hemi="split",
            views=["lat", "med"],
        )
        screenshot = brain.screenshot()
        brain.close()

        fig, ax = plt.subplots()
        ax.imshow(screenshot)
        ax.axis("off")

    print_emoji(":check_mark_button: Plotting is fine!")

    # Happy end!
    print_emoji(":check_mark_button: Everything seems to work!")


if __name__ == "__main__":
    main()
