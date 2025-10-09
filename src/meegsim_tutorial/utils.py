import emoji
import mne


def print_emoji(text):
    print(emoji.emojize(text))


def divider(pre=False, post=False):
    if pre:
        print()
    print(''.join(['-'] * 40))
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
