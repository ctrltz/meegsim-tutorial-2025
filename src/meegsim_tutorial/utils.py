import emoji
import mne
import numpy as np

from pathlib import Path


def print_emoji(text):
    print(emoji.emojize(text))


def divider(pre=False, post=False):
    if pre:
        print()
    print("".join(["-"] * 40))
    if post:
        print()


def FILL_ME(msg):
    raise NotImplementedError(msg)


def info_from_montage(montage_name, sfreq=250):
    """
    This function prepares an mne.Info object using all channels from
    the provided montage.
    """
    montage = mne.channels.make_standard_montage(montage_name)
    info = mne.create_info(ch_names=montage.ch_names, sfreq=sfreq, ch_types="eeg")
    info.set_montage(montage)
    return info


def vertno_to_index(src, hemi, vertno):
    hemis = ["lh", "rh"]
    assert hemi in hemis
    hemi_idx = hemis.index(hemi)

    vert_idx = np.where(src[hemi_idx]["vertno"] == int(vertno))[0]
    if not vert_idx.size:
        raise ValueError(
            "The provided vertno does not belong to the provided src. Please "
            "pick another vertex."
        )
    vert_idx = vert_idx.item(0)

    if hemi == "lh":
        return vert_idx

    return src[0]["nuse"] + vert_idx


def prepare_head_model(subjects_dir, spacing="oct5", montage="biosemi64"):
    src = mne.setup_source_space(
        subject="fsaverage", spacing=spacing, subjects_dir=subjects_dir, add_dist=False
    )

    fs_dir = Path(subjects_dir) / "fsaverage"
    bem = fs_dir / "bem" / "fsaverage-5120-5120-5120-bem-sol.fif"
    trans = fs_dir / "bem" / "fsaverage-trans.fif"

    info = info_from_montage(montage)
    fwd = mne.make_forward_solution(
        info,
        trans=trans,
        src=src,
        bem=bem,
        eeg=True,
        mindist=5.0,
        n_jobs=None,
        verbose=True,
    )
    fwd = mne.convert_forward_solution(fwd, force_fixed=True)

    return fwd, info
