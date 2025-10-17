"""
This module contains functions that will be added to MEEGsim in the near future.
"""

from meegsim_tutorial.utils import vertno_to_index


def get_leadfield(fwd, source):
    """
    Obtain a leadfield of the simulated point/patch source.

    Parameters
    ----------
    fwd : mne.Forward
        The forward model.
    source : PointSource | PatchSource
        The simulated source.

    Returns
    -------
    leadfield : array (n_channels,)
        The leadfield of the simulated source.
    """
    hemis = ["lh", "rh"]
    src = fwd["src"]
    L = fwd["sol"]["data"]

    indices = [
        vertno_to_index(src, hemis[hemi_idx], vertno)
        for hemi_idx, vertno in source.vertices
    ]
    leadfield = L[:, indices]
    if leadfield.ndim > 1:
        leadfield = leadfield.mean(axis=1)

    return leadfield
