import matplotlib.pyplot as plt
import mne
import numpy as np

from scipy.signal import welch

from meegsim_tutorial.utils import vertno_to_index


def fsaverage_brain(subjects_dir, **kwargs):
    brain_kwargs = dict(
        subject="fsaverage",
        subjects_dir=subjects_dir,
        background="w",
        cortex="low_contrast",
        surf="inflated",
        hemi="split",
        views=["lat", "med"],
        size=600,
    )
    brain_kwargs.update(kwargs)

    Brain = mne.viz.get_brain_class()
    brain = Brain(**brain_kwargs)
    return brain


def show_sources(src, sources, subjects_dir, **kwargs):
    """
    Show one source on the brain surface.

    Parameters
    ----------
    hemi_idx : {0, 1}
        Index of the source space (0 - left hemisphere, 1 - right hemisphere).
    vertno : int
        Index of the vertex within the hemisphere.
    """
    brain = fsaverage_brain(subjects_dir, **kwargs)

    for hemi_idx, vertno in sources:
        hemi = "rh" if hemi_idx else "lh"

        # NOTE: this call ensures that only vertices in the src can be plotted
        vertno_to_index(src, hemi, vertno)

        brain.add_foci(
            vertno, coords_as_verts=True, hemi=hemi, color="red", scale_factor=0.75
        )

    return brain


def show_waveforms(data, times, n_seconds=5):
    sfreq = 1.0 / (times[1] - times[0])
    n_samples = int(n_seconds * sfreq)

    data = np.atleast_2d(data)

    n_fft = sfreq
    n_overlap = n_fft // 2
    f, spec = welch(data, fs=sfreq, nperseg=n_fft, nfft=n_fft, noverlap=n_overlap)

    fig, (ax1, ax2) = plt.subplots(
        ncols=2,
        figsize=(9, 3),
        layout="constrained",
        gridspec_kw=dict(width_ratios=[3, 1]),
    )
    ax1.plot(times[:n_samples], data[:, :n_samples].T)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Amplitude (a. u.)")

    ax2.plot(f, 10 * np.log10(spec.T))
    ax2.set_xscale("log")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("10*log10(PSD)")

    return fig


def show_leadfield(fwd, info, hemi_idx, vertno):
    fig, (ax_main, ax_cbar) = plt.subplots(
        ncols=2,
        figsize=(3, 2),
        layout="constrained",
        gridspec_kw=dict(width_ratios=[1, 0.1]),
    )

    L = fwd["sol"]["data"]
    hemi = "rh" if hemi_idx else "lh"
    idx = vertno_to_index(fwd["src"], hemi, vertno)
    im, _ = mne.viz.plot_topomap(
        L[:, idx], info, sphere="eeglab", axes=ax_main, show=False
    )

    fig.colorbar(im, cax=ax_cbar)
    return fig
