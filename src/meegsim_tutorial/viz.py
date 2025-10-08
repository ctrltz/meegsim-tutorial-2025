import mne


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


def show_sources(sources, subjects_dir, **kwargs):
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
        brain.add_foci(vertno, coords_as_verts=True, hemi=hemi, 
                       color="red", scale_factor=0.75)
    
    return brain
