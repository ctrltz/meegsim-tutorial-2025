import matplotlib.pyplot as plt
import mne
import os

from mne.datasets import sample

from meegsim.location import select_random
from meegsim.simulate import SourceSimulator
from meegsim.waveform import narrowband_oscillation


# Head model
print("⬇️ Downloading and testing the template head model")

data_path = sample.data_path()
subjects_dir = data_path / "subjects"
src = mne.read_source_spaces(subjects_dir / "fsaverage" / "bem" / "fsaverage-ico-5-src.fif")

print("✅ Download complete!")


# Basic functionality
print("🔄 Testing basic functionality of MEEGsim")

sim = SourceSimulator(src)
sim.add_noise_sources(location=select_random, 
                      location_params=dict(n=10))
sim.add_point_sources(location=select_random,
                      location_params=dict(n=3),
                      waveform=narrowband_oscillation,
                      waveform_params=dict(fmin=8, fmax=12))

sc = sim.simulate(sfreq=250, duration=120)

print("✅ Basic functionality is fine!")


# Advanced functionality
print("🔄 Testing advanced functionality of MEEGsim")

sim = SourceSimulator(src)
sim.add_noise_sources(location=select_random, 
                      location_params=dict(n=10))
sim.add_patch_sources(location=select_random,
                      location_params=dict(n=3),
                      waveform=narrowband_oscillation,
                      waveform_params=dict(fmin=8, fmax=12),
                      extents=[10, 20, 50],
                      subject="fsaverage",
                      subjects_dir=subjects_dir)

sc = sim.simulate(sfreq=250, duration=120, random_state=1234)

print("✅ Advanced functionality is fine!")


# Plotting
print("🔄 Testing that plotting works")

if os.environ.get("BUILD_ENV", None) != "ci":
    brain = sc.plot(subject="fsaverage", 
                    subjects_dir=subjects_dir,
                    hemi="split", views=["lat", "med"])
    screenshot = brain.screenshot()
    brain.close()

    fig, ax = plt.subplots()
    ax.imshow(screenshot)
    ax.axis('off')

print("✅ Plotting is fine!")


# Happy end!
print("✅ Everything seems to work!")
