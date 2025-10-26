import matplotlib.pyplot as plt
import mne
import numpy as np

from pathlib import Path

from meegsim_tutorial.ext import get_leadfield
from meegsim_tutorial.utils import prepare_head_model
from meegsim_tutorial.viz import make_cropped_screenshot


from meegsim.simulate import SourceSimulator
from meegsim.waveform import one_over_f_noise


download_path = "~/mne_data"
subjects_dir = Path(download_path).expanduser().absolute() / "MNE-fsaverage-data"


def simulate_point(fwd, hemi_idx, vertno):
    src = fwd["src"]
    sim = SourceSimulator(src)
    sim.add_patch_sources(
        location=[(hemi_idx, vertno)],
        waveform=one_over_f_noise,
        names=["target"],
    )

    sc = sim.simulate(sfreq=250, duration=10)

    return sc


def simulate_patch(fwd, hemi_idx, vertno, patch_extent_mm, subjects_dir):
    src = fwd["src"]
    sim = SourceSimulator(src)
    sim.add_patch_sources(
        location=[(hemi_idx, vertno)],
        waveform=one_over_f_noise,
        extents=patch_extent_mm,
        subjects_dir=subjects_dir,
        names=["target"],
    )

    sc = sim.simulate(sfreq=250, duration=10)

    return sc


def main():
    fwd, info = prepare_head_model(subjects_dir)

    hemi_idx = 0
    vertno = 76290
    patch_areas_cm2 = [None, 4, 16, 64]

    n_areas = len(patch_areas_cm2)
    fig, axes = plt.subplots(
        nrows=3,
        ncols=n_areas,
        figsize=(3 * n_areas, 6),
        layout="constrained",
        gridspec_kw=dict(height_ratios=[1, 1, 0.1]),
    )

    for i_area, patch_area_cm2 in enumerate(patch_areas_cm2):
        # Simulate a point or a patch source
        if patch_area_cm2 is None:
            sc = simulate_point(fwd, hemi_idx, vertno)
            plot_title = "point-like"
        else:
            patch_extent_mm = np.sqrt(patch_area_cm2 * 100 / np.pi)
            sc = simulate_patch(fwd, hemi_idx, vertno, patch_extent_mm, subjects_dir)
            plot_title = f"area = {patch_area_cm2} cm$^2$"

        # Brain plot
        ax_brain = axes[0, i_area]
        brain = sc.plot(subject="fsaverage", subjects_dir=subjects_dir)
        make_cropped_screenshot(brain, ax=ax_brain)
        ax_brain.set_title(plot_title)

        # Plot the leadfield
        ax_leadfield = axes[1, i_area]
        leadfield = get_leadfield(fwd, sc["target"])
        im, _ = mne.viz.plot_topomap(
            leadfield, info, sphere="eeglab", axes=ax_leadfield, show=False
        )

        # Colorbar
        ax_cbar = axes[2, i_area]
        fig.colorbar(im, cax=ax_cbar, orientation="horizontal")

    plt.show(block=True)


if __name__ == "__main__":
    main()
