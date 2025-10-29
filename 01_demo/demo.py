"""
Tutorial and demo of core MEEGsim features
------------------------------------------

In this tutorial/demo, we will start with the pre-requisites for the simulation
(source space / forward model), then look into building blocks currently provided
by MEEGsim and how one can combine them in a simulation.

**NOTE:** this script is designed to run in steps, which are represented by the
functions below. After each step, the program stops. If you're done with exploring
the output of a certain step, you can go back to the script and skip it by
setting `complete` to True in the function arguments:

Before: def step1_2_inspect_source_space(src, complete=False): ...
After:  def step1_2_inspect_source_space(src, complete=True): ...

Some important steps are not skippable. Otherwise, you don't need to change anything
in code apart from the path to the data (see 0. Configuration below).
However, you're always welcome to explore and play around with the data.
The **EXERCISES** part of the sections below suggests some things you could try.
"""

import matplotlib.pyplot as plt
import mne
import numpy as np

from mne.datasets import fetch_fsaverage
from pathlib import Path

from meegsim.coupling import ppc_constant_phase_shift, ppc_shifted_copy_with_noise
from meegsim.location import select_random
from meegsim.waveform import narrowband_oscillation, one_over_f_noise, white_noise
from meegsim.simulate import SourceSimulator

from meegsim_tutorial.utils import divider, info_from_montage, FILL_ME
from meegsim_tutorial.viz import show_sources, show_waveforms, show_leadfield

"""
To focus more on the functionality of MEEGsim, we provide some helper functions
which are imported below. Here's a short overview of their purpose:

* `info_from_montage` - creates an `mne.Info` object that contains all EEG channels
  from the provided `montage`
* `show_sources` - shows the locations of the provided sources on the `fsaverage`
  brain surface
* `show_waveforms` - plots the provided waveforms in time and frequency domain
* `show_leadfield` - plots the leadfield of the provided sources
* `FILL_ME` - placeholder for the places where **your** input is expected. It always
  raises an error with instructions as an error message. Replace the whole `FILL_ME`
  call with your code.
"""


"""
0. Configuration
----------------

Below, please provide the same path to the sample dataset that you used
during the installation check.
"""
download_path = FILL_ME(
    "Provide the same value for path as the one you used during the installation check."
)

subject = "fsaverage"
subjects_dir = Path(download_path).expanduser().absolute() / "MNE-fsaverage-data"
fs_dir = fetch_fsaverage(subjects_dir=subjects_dir)


"""
1. Navigating the source space
"""


def step1_1_create_source_space():
    """
    1.1. Creating the source space
    ------------------------------

    Source space is one of the key ingredients in every simulation, since it defines
    location and orientations of all sources that we model. In this section, we have
    a closer look at how one can navigate the source space.

    **Take home:** in MEEGsim, we use two numbers to define position of sources that
    are added to the simulation:
      * index of the source space (0 - left hemisphere, 1 - right hemisphere)
      * index of the vertex within the respective hemisphere (`vertno`).

    Let's create a source space using the template MPI (`fsaverage`) from the
    sample MNE dataset and inspect it first. The `spacing` parameter below defines
    how coarse the source space will be. In this tutorial, we recommend using `oct5`
    to reduce the computational load during the workshop. For real data analysis, more
    dense grids are generally preferred.  Find more about other possible and recommended
    spacing values [here](https://mne.tools/stable/documentation/cookbook.html#setting-up-the-source-space).
    """
    src = mne.setup_source_space(
        subject=subject, spacing="oct5", subjects_dir=subjects_dir, add_dist=False
    )

    return src


def step1_2_inspect_source_space(src, complete=False):
    """
    1.2. Inspecting the source space
    """
    if complete:
        return

    # If we print the resulting `src`, we get an overview of the generated source
    # space: two hemispheres with 1026 vertices (see `n_used` in the output below)
    # in each hemisphere.
    divider(pre=True)
    print("Short description of the source space structure:")
    print(src)
    divider(post=True)

    # Hemisphere-specific data can be accessed with `src[0]` and  `src[1]` for left
    # and right hemisphere, respectively.
    divider(pre=True)
    print("Description of the source space for left hemisphere:")
    print(src[0])
    divider(post=True)

    # It is also possible to visualize the positions of all sources on the brain
    # surface. Each source is a dipole that corresponds to a group of aligned
    # pyramidal neurons:
    mne.viz.plot_alignment(
        subject=subject,
        subjects_dir=subjects_dir,
        surfaces="white",
        coord_frame="mri",
        src=src,
    )

    # Each vertex has a unique number between 0 and 163841. The `vertno` array stores
    # indices of all vertices that belong to the source space (in this case, the left
    # hemisphere):
    divider(pre=True)
    print("Indices of vertices in the left hemisphere:")
    print(src[0]["vertno"])
    print(
        "NOTE: the indices are not guaranteed to be continuous (e.g., for the oct6 spacing)"
    )
    divider(post=True)

    # In MEEGsim, we use the combination of the hemisphere index (0/1) and `vertno`
    # to define the position of added sources. You can try it out below in a small
    # example (not yet simulation). The helper function `show_sources` will show the
    # source that is defined by `hemi_idx` and `vertno` below.

    hemi_idx = 0
    vertno = 0

    # TIP: add surf="pial" or surf="pial_semi_inflated" to show sulci/gyri
    show_sources(src, [(hemi_idx, vertno)], subjects_dir)

    # %% [markdown]
    # **EXERCISES**:
    # 1. Try moving the source to the right hemisphere.
    # 2. Try changing the `vertno` value to select a source in frontal/occipital/your
    # favorite area.

    input("Press any key to continue")
    print(
        "Step 1.2 is complete, please set complete to True after finishing the exercises"
    )
    exit(0)


def step1_3_select_random(src, complete=False):
    """
    1.3. Selecting random vertices in MEEGsim.
    """
    if complete:
        return

    # %% [markdown]
    # Sometimes, it can be useful to choose vertices randomly,
    # and the [`select_random`](https://meegsim.readthedocs.io/en/latest/generated/meegsim.location.select_random.html)
    # function can be used for this purpose. Notice the format of its output
    # (pairs of numbers):

    divider(pre=True)
    print("Randomly selected vertices:")
    print(select_random(src, n=10))
    divider(post=True)

    input("Press any key to continue")

    show_sources(src, select_random(src, n=10), subjects_dir)

    input("Press any key to continue")
    print("Step 1.3 is complete, please set complete to True")
    exit(0)


"""
2. Forward model
----------------

Forward model is the second key ingredient of all simulations. It provides a mapping
between source- and sensor-space activity, which is described by the lead field matrix.
In this section, we will explore and visualize the lead field.
"""


def step2_1_create_chanlocs():
    """
    2.1. Channel locations

    First, let's define channel locations for the simulated EEG setup. In MNE-Python,
    there are multiple [built-in channel configurations](https://mne.tools/stable/auto_tutorials/intro/40_sensor_locations.html#working-with-built-in-montages)
    (a.k.a. montages). In this tutorial, we will use the Biosemi64 montage with 64
    channels, which is a common setup nowadays. Below, we first create an `mne.Info`
    object that describes channel locations and then plot them:
    """
    info = info_from_montage("biosemi64")

    return info


def step2_2_inspect_chanlocs(info, complete=False):
    """
    2.2. Inspect channel locations

    We plot the channel locations as a sanity check:
    """
    if complete:
        return

    _, ax = plt.subplots(figsize=(4, 4))
    info.plot_sensors(sphere="eeglab", axes=ax)

    input("Press any key to continue")
    print("Step 2.2 is complete, please set complete to True")
    exit(0)


def step2_3_create_forward(info):
    """
    2.3. Create lead field

    With channel locations fixed, we are now ready to obtain the lead field. For this
    purpose, we use a pre-computed BEM (boundary element method) model of the template
    `fsaverage` head:
    """

    bem = subjects_dir / subject / "bem" / "fsaverage-5120-5120-5120-bem-sol.fif"
    trans = subjects_dir / subject / "bem" / "fsaverage-trans.fif"

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

    # By default, the forward model allows arbitrary orientations of sources. However,
    # MEEGsim at the moment only supports fixed orientations along the normal to the
    # cortical surface, so we need to convert the forward solution accordingly:
    fwd = mne.convert_forward_solution(fwd, force_fixed=True)

    return fwd


def step2_4_inspect_leadfield(fwd, info, complete=False):
    """
    2.4. Inspect the lead field

    Among other fields, the forward model (`fwd`) contains the lead field matrix,
    which we inspect below:
    """
    if complete:
        return

    L = fwd["sol"]["data"]
    print(L.shape)

    # Matrix `L` defined above is the resulting lead field. It has 64 rows (1 row per
    # channel) and 2052 columns (1 column per modeled source). Lead field describes
    # how all sources get mixed when their activity is projected to sensor space.
    # We can explore the lead field of separate sources to get a better feeling of
    # the mixing process:

    hemi_idx = 0
    vertno = 0

    show_sources(src, [(hemi_idx, vertno)], subjects_dir)
    _ = show_leadfield(fwd, info, hemi_idx, vertno)
    plt.show(block=True)

    # **EXERCISE**: try changing `hemi_idx` and `vertno` and see how the lead field
    # changes.

    input("Press any key to continue")
    print("Step 2.4 is complete, please set complete to True")
    exit(0)


"""
3. Generating source activity

With source space and lead field in place, we are now ready to start simulating
data. In this section, we will introduce basic waveforms of source activity -
noise (white or 1/f) and oscillations. All waveforms are generated from white
noise by processing (e.g., filtering) the signal to obtain the desired properties.
"""


def get_times(sfreq=250, duration=60, complete=False):
    """
    Simulation of activity requires a vector of time points for each generated
    sample (similar to `raw.times` in MNE-Python). Below, we create such vector
    for 60 s of data with the sampling frequency of 250 Hz. The individual time
    points are therefore 4 ms (0.004 s) apart from each other:
    """
    times = np.arange(sfreq * duration) / sfreq

    if not complete:
        divider(pre=True)
        print("First 10 time points:")
        print(times[:10])
        divider(post=True)

    return times


def step3_1_background_noise(complete=False):
    """
    3.1. Noise: background (1/f) and sensor (white)

    In this section, we show different ways to simulating time series
    of noise with MEEGsim (1 time series of each kind in the example below).
    For 1/f noise, it is possible to set `slope` to a desired value:
    """
    if complete:
        return

    times = get_times()
    n1 = one_over_f_noise(1, times, slope=1)
    n2 = one_over_f_noise(1, times, slope=1.5)
    n3 = white_noise(1, times)

    # **NOTE:** if you re-run the script, the resulting time series change randomly.
    # This can be helpful when generating multiple datasets (i.e., "subjects") for
    #  the same simulation idea.
    _ = show_waveforms(np.vstack([n1, n2, n3]), times, n_seconds=2)
    plt.show(block=True)

    input("Press any key to continue")
    print("Step 3.1 is complete, please set complete to True")
    exit(0)


def step3_2_oscillatory_activity(complete=False):
    """
    3.2. Oscillatory activity

    Oscillatory activity is simulated by filtering white noise in a frequency
    band of interest (defined with cutoff frequencies `fmin` and `fmax`):
    """
    if complete:
        return

    times = get_times()
    s1 = narrowband_oscillation(1, times, fmin=8, fmax=12)
    s2 = narrowband_oscillation(1, times, fmin=16, fmax=24)

    _ = show_waveforms(np.vstack([s1, s2]), times, n_seconds=2)
    plt.show(block=True)

    input("Press any key to continue")
    print("Step 3.2 is complete, please set complete to True")
    exit(0)


"""
4. Combining the ingredients
----------------------------

By now, we learned how to place sources and generate their activity, but that doesn't
feel like a proper simulation yet. It's time to combine the introduced ingredients.
For this purpose, we will use the `SourceSimulator` class provided by MEEGsim, which
allows one to add sources of activity to the simulation and set their coupling.
"""


def step4_1_general_workflow(fwd):
    """
    4.1. First simulation
    ---------------------
    The general workflow of simulations with MEEGsim is presented below. There are
    two main classes:

        * `SourceSimulator` - this class allows you to define the parameters of your
          simulation (source locations, waveforms, and coupling)
        * `SourceConfiguration` - this class corresponds to one possible instance of
          simulation with the parameters you defined. If some of the parameters are
          chosen randomly, configurations will differ. One `SourceSimulator` can thus
          be used to produce multiple `SourceConfiguration` objects (i.e., datasets).
          Source configurations can be converted to common used MNE objects (currently,
          `raw` or `stc`).

    See also ../assets/general_workflow.png
    """
    # re-using the approach from section 3.2 here
    sfreq = 250
    duration = 60
    times = get_times()
    s1 = narrowband_oscillation(1, times, fmin=8, fmax=12)
    s2 = narrowband_oscillation(1, times, fmin=16, fmax=24)

    # To initialize the `SourceSimulator`, we need to provide the source space that
    # defines all candidate source locations:
    src = fwd["src"]
    sim = SourceSimulator(src)

    # When adding sources, we need to set their `location` and `waveform` either
    # explicitly (`(hemi_idx, vertno)` and time course) or through a generating function
    # (`select_random`, `one_over_f_noise`). Below, we first add two point sources in
    # motor areas of both hemispheres using the time courses of alpha and beta oscillations
    # from Section 3.2. For convenience, we can also assign meaningful names to the sources.
    # This feature comes in handy when defining the connectivity:
    sim.add_point_sources(
        location=[(0, 0), (1, 0)],
        waveform=np.vstack([s1, s2]),
        names=["m1-lh", "m1-rh"],
    )

    # Afterwards, we add 100 noise sources in random locations by providing the names
    # of the generator functions:
    _ = sim.add_noise_sources(
        location=select_random,
        location_params=dict(n=100),
        waveform=one_over_f_noise,  # default, can be omitted
        waveform_params=dict(slope=1),  # default, can be omitted
    )

    # The `sim` object does not contain the simulated data, it only describes how
    # the sources should be simulated. By running its `simulate` method, we obtain
    # a `SourceConfiguration` object which actually contains all sources and their
    # data:
    sc = sim.simulate(sfreq=sfreq, duration=duration, fwd=fwd, random_state=123)

    return sim, sc


def step4_2_inspect_source_configuration(sc, complete=False):
    """
    4.2. Inspect and debug the source configuration
    -----------------------------------------------

    To get a better feeling of what we have just achieved, we can inspect the
    resulting source configuration in more detail.
    """
    if complete:
        return

    # Each source has a name for quick access, and names can be set when creating the
    # sources (see the `add_point_sources` call above; it is also helpful when defining
    # ground-truth connectivity):
    divider(pre=True)
    print("Simulated sources")
    print(sc._sources)
    divider(post=True)

    # If the names are not provided explicitly, they are (for now, this behavior might
    # be changed) generated automatically:
    divider(pre=True)
    print("Simulated NOISE sources")
    print(sc._noise_sources)
    divider(post=True)

    # Now, let's plot all sources
    sc.plot(
        subject="fsaverage",
        subjects_dir=subjects_dir,
        colors=dict(point="red"),
        hemi="split",
        views=["lat", "med"],
        size=600,
        time_viewer=False,
    )

    # In addition, we can access each non-noise source by its name and, for example,
    # plot its activity:

    divider(pre=True)
    print("Accessing individual sources")
    print(sc["m1-lh"])
    divider(post=True)

    show_waveforms(sc["m1-lh"].waveform, sc.times)
    plt.show(block=True)

    # **EXERCISE**: plot the activity of the source `m1-rh`.

    input("Press any key to continue")
    print(
        "Step 4.2 is complete, please set complete to True once done with the exercise"
    )
    exit(0)


def step4_3_obtain_data(sc, fwd, info, complete=False):
    """
    4.3. Obtain data

    Finally, we can also obtain the simulated data in source and sensor space
    with `to_stc` and `to_raw` methods, respectively:
    """
    if complete:
        return

    stc = sc.to_stc()

    divider(pre=True)
    print("Resulting stc:")
    print(stc)
    divider(post=True)

    stc.plot(
        subject="fsaverage",
        subjects_dir=subjects_dir,
        hemi="split",
        views=["lat", "med"],
    )

    # To obtain sensor-space data, we need to provide the forward model (`fwd`)
    # and channel locations (`info`). In addition, we can add a certain level of
    # measurement noise (`sensor_noise_level`; between 0 and 1, 0 - no noise at all,
    # 1 - only noise, no brain activity):

    raw = sc.to_raw(fwd, info, sensor_noise_level=0.01)

    # Let's inspect the simulated data and its spectra:
    raw.plot(scalings=dict(eeg=2e-6))
    _ = raw.compute_psd(fmax=40, n_fft=2 * sc.sfreq, n_overlap=sc.sfreq).plot(
        sphere="eeglab"
    )
    plt.show(block=True)

    input("Press any key to continue")
    print("Step 4.3 is complete, please set complete to True")
    exit(0)


def step4_4_adjust_snr(sim, fwd, info, sfreq=250, duration=60, complete=False):
    """
    4.4. Adjusting the signal-to-noise ratio (SNR)

    In the plot above, oscillatory activity is present but not very pronounced.
    To control its level, we can adjust the SNR of oscillatory activity relative
    to 1/f noise. This has to be done when simulating the data so we redo this step
    below. The desired SNR is specified in the `snr_global` argument, while
    `snr_params` define the frequency band for the adjustment of SNR:
    """
    if complete:
        return

    sc = sim.simulate(
        sfreq=sfreq,
        duration=duration,
        snr_global=3,
        snr_params=dict(fmin=8, fmax=30),
        fwd=fwd,
        random_state=123,
    )
    raw = sc.to_raw(fwd, info, sensor_noise_level=0.01)

    # Inspect the resulting spectra
    _ = raw.compute_psd(fmax=40, n_fft=2 * sfreq, n_overlap=sfreq).plot(sphere="eeglab")

    # **EXERCISE**: try other values of `snr_global` to get the spectra which look
    # reasonable (e.g., realistic or just cool) to you.

    input("Press any key to continue")
    print("Step 4.4 is complete, please set complete to True")
    exit(0)


"""
5. Setting up ground-truth connectivity
---------------------------------------

The current focus of MEEGsim is on connectivity (i.e., synchronization of activity)
between sources of interest. In this section, we explore the ways to set ground-truth
coupling in MEEGsim. In both cases, the user is expected to provide a waveform and
some function-specific parameters as input, and MEEGsim functions will return another
waveform that is coupled to the input one in a desired way (i.e., with desired phase
lag and coupling strength).
"""


def step5_1_constant_phase_lag(complete=False):
    """
    5.1. Constant phase lag

    The simplest way to obtain synchronization is to copy the input waveform and
    apply a constant phase lag to it. This approach is implemented in the
    `ppc_constant_phase_shift`. The amplitude envelope of the output waveform can
    either be generated randomly (default) or copied from the input.
    """
    if complete:
        return

    sfreq = 250
    times = get_times(sfreq=sfreq)
    original = narrowband_oscillation(1, times, fmin=8, fmax=12)
    coupled = ppc_constant_phase_shift(
        original, sfreq, phase_lag=np.pi, fmin=8, fmax=12
    )

    # Plot the result
    _ = show_waveforms(np.vstack([original, coupled]), times, n_seconds=2)
    plt.show(block=True)

    # **EXERCISE**: try other values of `phase_lag` between 0 and `2 * np.pi`.

    input("Press any key to continue")
    print(
        "Step 5.1 is complete, please set complete to True once done with the exercise"
    )
    exit(0)


def step5_2_weak_synchronization(complete=False):
    """
    5.2. Weak synchronization

    Constant phase shift leads to perfect synchronization, which is likely not
    realistic for brain data. Therefore, it is useful to control the strength of
    synchronization, for example, with the `ppc_shifted_copy_with_noise` method.
    This method allows you to set a desired value of coherence. If we set the
    coherence (`coh` below) to 1, we again get perfect synchronization:
    """
    if complete:
        return

    sfreq = 250
    times = get_times(sfreq=sfreq)
    original = narrowband_oscillation(1, times, fmin=8, fmax=12)
    coupled = ppc_shifted_copy_with_noise(
        original, sfreq, coh=0.1, phase_lag=np.pi, fmin=8, fmax=12, band_limited=False
    )

    # Plot the result
    _ = show_waveforms(np.vstack([original, coupled]), times, n_seconds=2)
    plt.show(block=True)

    # **EXERCISE**: try other values of `coh` below 1 and observe how the coupling
    # becomes less stable.

    input("Press any key to continue")
    print(
        "Step 5.2 is complete, please set complete to True once done with the exercise"
    )
    exit(0)


def step5_3_adding_to_simulation(fwd, complete=False):
    """
    5.3. Add connectivity to the simulation
    ---------------------------------------

    To add coupling to the simulation, we can use the `set_coupling` method of the
    `SourceSimulator`. Coupling edges have to defined using names of sources. First,
    let's bring back the simulation we already had:
    """
    if complete:
        return

    sim = SourceSimulator(src)
    sim.add_point_sources(
        location=[(0, 0), (1, 0)],
        waveform=narrowband_oscillation,
        waveform_params=dict(fmin=8, fmax=12),
        names=["m1-lh", "m1-rh"],
    )
    _ = sim.add_noise_sources(
        location=select_random,
        location_params=dict(n=100),
        waveform=one_over_f_noise,  # default, can be omitted
        waveform_params=dict(slope=1),  # default, can be omitted
    )

    # Now, let's add coupling to the simulation:
    sim.set_coupling(
        {
            ("m1-lh", "m1-rh"): dict(coh=0.5, phase_lag=np.pi),
        },
        method=ppc_shifted_copy_with_noise,
        fmin=8,
        fmax=12,
        band_limited=False,
    )

    # Now we can simulate the data and check the presence of coupling:
    sc = sim.simulate(
        sfreq=250,
        duration=60,
        snr_global=3,
        snr_params=dict(fmin=8, fmax=30),
        fwd=fwd,
        random_state=123,
    )

    _ = show_waveforms(
        np.vstack([sc["m1-lh"].waveform, sc["m1-rh"].waveform]), sc.times, n_seconds=2
    )
    plt.show(block=True)

    input("Press any key to continue")
    print("Step 5.3 is complete, please set complete to True")
    exit(0)


"""
6. Summary
----------

Congrats, you've made it to the end of the demo! Below you can find an overview of
what we've covered so far. This rather short script generates simulated EEG data for
100 sources of 1/f activity and 2 sources of alpha activity with pre-defined
coupling parameters and desired SNR. Comments above function calls highlight the
similarity between MEEGsim syntax and textual description that one could use in the paper.
"""


def step6_summary(fwd, info):
    sfreq = 250
    duration = 60

    src = fwd["src"]
    sim = SourceSimulator(src)

    # 100 noise sources placed randomly
    sim.add_noise_sources(location=select_random, location_params=dict(n=100))

    # 2 sources of narrowband (8-12 Hz) oscillation
    sim.add_point_sources(
        location=[(0, 0), (1, 0)],
        waveform=narrowband_oscillation,
        waveform_params=dict(fmin=8, fmax=12),
        names=["m1-lh", "m1-rh"],
    )

    # Coupling between alpha sources with a phase lag of pi/2 and coherence of 0.5
    sim.set_coupling(
        ("m1-lh", "m1-rh"),
        method=ppc_shifted_copy_with_noise,
        fmin=8,
        fmax=12,
        coh=0.5,
        phase_lag=np.pi / 2,
    )

    # SNR of 0.5 in 8-30 Hz
    sc = sim.simulate(
        sfreq=sfreq,
        duration=duration,
        snr_global=0.5,
        snr_params=dict(fmin=8, fmax=30),
        fwd=fwd,
        random_state=123,
    )

    # 1% of sensor space noise
    raw = sc.to_raw(fwd, info, sensor_noise_level=0.01)

    return raw


"""
Now it's your turn to simulate! Check out the `02_hands_on` folder
with some tasks that we prepared.
"""


if __name__ == "__main__":
    src = step1_1_create_source_space()
    step1_2_inspect_source_space(src)
    step1_3_select_random(src)

    info = step2_1_create_chanlocs()
    step2_2_inspect_chanlocs(info)
    fwd = step2_3_create_forward(info)
    step2_4_inspect_leadfield(fwd, info)

    step3_1_background_noise()
    step3_2_oscillatory_activity()

    sim, sc = step4_1_general_workflow(fwd)
    step4_2_inspect_source_configuration(sc)
    step4_3_obtain_data(sc, fwd, info)
    step4_4_adjust_snr(sim, fwd, info)

    step5_1_constant_phase_lag()
    step5_2_weak_synchronization()
    step5_3_adding_to_simulation(fwd)

    step6_summary(fwd, info)

    print("""
        Congrats, you've made it to the end of the demo!
        Thank you very much for participating!
    """)
