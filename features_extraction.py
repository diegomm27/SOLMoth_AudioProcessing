import numpy as np
from pyAudioAnalysis import audioBasicIO
import pandas as pd


def zero_crossing_rate(signal):
    """
    Calculates the zero crossing rate of an audio signal

    :param signal: audio signal
    :type signal: numpy.ndarray
    :return: zero crossing rate of the audio signal
    :rtype: numpy.float64
    """
    L = len(signal)
    times_crossed = np.sum(np.abs(np.diff(np.sign(signal)))) / 2
    return np.float64(times_crossed) / np.float64(L - 1.0)


def spectral_centroid(signal, sample_rate):
    """
    Calculates the spectral centroid of an audio signal

    :param signal: audio signal
    :type signal: numpy.ndarray
    :param sample_rate: sampling rate of the audio signal
    :type sample_rate: int
    :return: spectral centroid of the audio signal
    :rtype: numpy.float64
    """
    L = (np.arange(1, len(signal) + 1)) * (sample_rate / (2.0 * len(signal)))
    y = signal.copy()
    y = y / y.max()
    numerator = np.sum(L * y)
    denominator = np.sum(y)
    centroid = np.abs(numerator / denominator)
    centroid = centroid / (sample_rate / 2.0)
    return centroid


def spectral_entropy(signal, num_blocks):
    """
    Calculates the spectral entropy of an audio signal

    :param signal: audio signal
    :type signal: numpy.ndarray
    :param num_blocks: number of blocks to split the signal into
    :type num_blocks: int
    :return: spectral entropy of the audio signal
    :rtype: numpy.float64
    """
    L = len(signal)
    energy = np.abs(np.sum(signal ** 2))
    window_size = int(np.floor(L / num_blocks))
    if L != window_size * num_blocks:
        signal = signal[0:window_size * num_blocks]
    sub_frames = signal.reshape(window_size, num_blocks, order='F').copy()
    sub_energies = np.sum(sub_frames ** 2, axis=0) / energy
    entropy = -np.sum(sub_energies * np.log2(sub_energies))
    return entropy


def rolloff_factor(signal, c, sample_rate):
    """
    Calculates the spectral rolloff factor of an audio signal

    :param signal: audio signal
    :type signal: numpy.ndarray
    :param c: coefficient value to use for the calculation
    :type c: float
    :param sample_rate: sampling rate of the audio signal
    :type sample_rate: int
    :return: spectral rolloff factor of the audio signal
    :rtype: float
    """
    energy = np.abs(np.sum(signal ** 2))
    l = len(signal)
    cutoff = c * energy
    cumulative_sum = np.cumsum(signal ** 2)
    [index, ] = np.nonzero(cumulative_sum > cutoff)
    if len(index) > 0:
        rolloff = np.float64(index[0]) / (float(l))
    else:
        rolloff = 0.0
    return rolloff


def extract_audio_features(filename):
    """
    Extract audio features from an audio file.

    :param filename: path to the audio file.
    :return: a tuple containing the zero-crossing rate, the spectral centroid, the spectral entropy, and the spectral
    rolloff of the audio signal.
    """
    [Fs, x] = audioBasicIO.read_audio_file(filename)
    x = audioBasicIO.stereo_to_mono(x)
    zcr = zero_crossing_rate(x)
    centroid = spectral_centroid(x, Fs)
    entropy = spectral_entropy(x, 10)
    rolloff = rolloff_factor(x, 0.8, Fs)

    return zcr, centroid, entropy, rolloff


