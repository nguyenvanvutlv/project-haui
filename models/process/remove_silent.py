from typing import Union, List
import numpy as np
import torch
import torchaudio
import assets
import sklearn
import sklearn.svm
import sklearn.decomposition
import sklearn.ensemble
import soundfile as sf
from scipy.fftpack import fft
from scipy.fftpack import dct

eps = 0.00000001


def smoothMovingAvg(inputSignal, windowLen=11):
    windowLen = int(windowLen)
    if inputSignal.ndim != 1:
        raise ValueError("")
    if inputSignal.size < windowLen:
        raise ValueError("Input vector needs to be bigger than window size.")
    if windowLen < 3:
        return inputSignal
    s = np.r_[2 * inputSignal[0] - inputSignal[windowLen - 1::-1],
    inputSignal, 2 * inputSignal[-1] - inputSignal[-1:-windowLen:-1]]
    w = np.ones(windowLen, 'd')
    y = np.convolve(w / w.sum(), s, mode='same')
    return y[windowLen:-windowLen + 1]


def listOfFeatures2Matrix(features):
    '''
    listOfFeatures2Matrix(features)

    This function takes a list of feature matrices as argument and returns a single concatenated feature matrix and the respective class labels.

    ARGUMENTS:
        - features:        a list of feature matrices

    RETURNS:
        - X:            a concatenated matrix of features
        - Y:            a vector of class indeces
    '''

    X = np.array([])
    Y = np.array([])
    for i, f in enumerate(features):
        if i == 0:
            X = f
            Y = i * np.ones((len(f), 1))
        else:
            X = np.vstack((X, f))
            Y = np.append(Y, i * np.ones((len(f), 1)))
    return (X, Y)


def trainSVM(features, Cparam):
    '''
    Train a multi-class probabilitistic SVM classifier.
    Note:     This function is simply a wrapper to the sklearn functionality for SVM training
              See function trainSVM_feature() to use a wrapper on both the feature extraction and the SVM training (and parameter tuning) processes.
    ARGUMENTS:
        - features:         a list ([numOfClasses x 1]) whose elements containt numpy matrices of features
                            each matrix features[i] of class i is [n_samples x numOfDimensions]
        - Cparam:           SVM parameter C (cost of constraints violation)
    RETURNS:
        - svm:              the trained SVM variable

    NOTE:
        This function trains a linear-kernel SVM for a given C value. For a different kernel, other types of parameters should be provided.
    '''

    [X, Y] = listOfFeatures2Matrix(features)
    svm = sklearn.svm.SVC(C=Cparam, kernel='linear', probability=True)
    svm.fit(X, Y)

    return svm


def normalizeFeatures(features):
    '''
    This function normalizes a feature set to 0-mean and 1-std.
    Used in most classifier trainning cases.

    ARGUMENTS:
        - features:    list of feature matrices (each one of them is a numpy matrix)
    RETURNS:
        - features_norm:    list of NORMALIZED feature matrices
        - MEAN:        mean vector
        - STD:        std vector
    '''
    X = np.array([])

    for count, f in enumerate(features):
        if f.shape[0] > 0:
            if count == 0:
                X = f
            else:
                X = np.vstack((X, f))
            count += 1

    MEAN = np.mean(X, axis=0) + 0.00000000000001;
    STD = np.std(X, axis=0) + 0.00000000000001;

    features_norm = []
    for f in features:
        ft = f.copy()
        for n_samples in range(f.shape[0]):
            ft[n_samples, :] = (ft[n_samples, :] - MEAN) / STD
        features_norm.append(ft)
    return (features_norm, MEAN, STD)


def stChromaFeatures(X, fs, nChroma, nFreqsPerChroma):
    # TODO: 1 complexity
    # TODO: 2 bug with large windows

    chromaNames = ['A', 'A#', 'B', 'C', 'C#', 'D',
                   'D#', 'E', 'F', 'F#', 'G', 'G#']
    spec = X ** 2
    if nChroma.max() < nChroma.shape[0]:
        C = np.zeros((nChroma.shape[0],))
        C[nChroma] = spec
        C /= nFreqsPerChroma[nChroma]
    else:
        I = np.nonzero(nChroma > nChroma.shape[0])[0][0]
        C = np.zeros((nChroma.shape[0],))
        C[nChroma[0:I - 1]] = spec
        C /= nFreqsPerChroma
    finalC = np.zeros((12, 1))
    newD = int(np.ceil(C.shape[0] / 12.0) * 12)
    C2 = np.zeros((newD,))
    C2[0:C.shape[0]] = C
    C2 = C2.reshape(int(C2.shape[0] / 12), 12)
    # for i in range(12):
    #    finalC[i] = np.sum(C[i:C.shape[0]:12])
    finalC = np.matrix(np.sum(C2, axis=0)).T
    finalC /= spec.sum()

    #    ax = plt.gca()
    #    plt.hold(False)
    #    plt.plot(finalC)
    #    ax.set_xticks(range(len(chromaNames)))
    #    ax.set_xticklabels(chromaNames)
    #    xaxis = numpy.arange(0, 0.02, 0.01);
    #    ax.set_yticks(range(len(xaxis)))
    #    ax.set_yticklabels(xaxis)
    #    plt.show(block=False)
    #    plt.draw()

    return chromaNames, finalC


def stMFCC(X, fbank, n_mfcc_feats):
    """
    Computes the MFCCs of a frame, given the fft mag

    ARGUMENTS:
        X:        fft magnitude abs(FFT)
        fbank:    filter bank (see mfccInitFilterBanks)
    RETURN
        ceps:     MFCCs (13 element vector)

    Note:    MFCC calculation is, in general, taken from the 
             scikits.talkbox library (MIT Licence),
    #    with a small number of modifications to make it more 
         compact and suitable for the pyAudioAnalysis Lib
    """

    mspec = np.log10(np.dot(X, fbank.T) + eps)
    ceps = dct(mspec, type=2, norm='ortho', axis=-1)[:n_mfcc_feats]
    return ceps


def stSpectralRollOff(X, c, fs):
    """Computes spectral roll-off"""
    totalEnergy = np.sum(X ** 2)
    fftLength = len(X)
    Thres = c * totalEnergy
    # Ffind the spectral rolloff as the frequency position 
    # where the respective spectral energy is equal to c*totalEnergy
    CumSum = np.cumsum(X ** 2) + eps
    [a, ] = np.nonzero(CumSum > Thres)
    if len(a) > 0:
        mC = np.float64(a[0]) / (float(fftLength))
    else:
        mC = 0.0
    return (mC)


def stSpectralFlux(X, X_prev):
    """
    Computes the spectral flux feature of the current frame
    ARGUMENTS:
        X:            the abs(fft) of the current frame
        X_prev:        the abs(fft) of the previous frame
    """
    # compute the spectral flux as the sum of square distances:
    sumX = np.sum(X + eps)
    sumPrevX = np.sum(X_prev + eps)
    F = np.sum((X / sumX - X_prev / sumPrevX) ** 2)

    return F


def stSpectralEntropy(X, n_short_blocks=10):
    """Computes the spectral entropy"""
    L = len(X)  # number of frame samples
    Eol = np.sum(X ** 2)  # total spectral energy

    sub_win_len = int(np.floor(L / n_short_blocks))  # length of sub-frame
    if L != sub_win_len * n_short_blocks:
        X = X[0:sub_win_len * n_short_blocks]

    sub_wins = X.reshape(sub_win_len, n_short_blocks, order='F').copy()  # define sub-frames (using matrix reshape)
    s = np.sum(sub_wins ** 2, axis=0) / (Eol + eps)  # compute spectral sub-energies
    En = -np.sum(s * np.log2(s + eps))  # compute spectral entropy

    return En


def stSpectralCentroidAndSpread(X, fs):
    """Computes spectral centroid of frame (given abs(FFT))"""
    ind = (np.arange(1, len(X) + 1)) * (fs / (2.0 * len(X)))

    Xt = X.copy()
    Xt = Xt / Xt.max()
    NUM = np.sum(ind * Xt)
    DEN = np.sum(Xt) + eps

    # Centroid:
    C = (NUM / DEN)

    # Spread:
    S = np.sqrt(np.sum(((ind - C) ** 2) * Xt) / DEN)

    # Normalize:
    C = C / (fs / 2.0)
    S = S / (fs / 2.0)

    return (C, S)


def stEnergyEntropy(frame, n_short_blocks=10):
    """Computes entropy of energy"""
    Eol = np.sum(frame ** 2)  # total frame energy
    L = len(frame)
    sub_win_len = int(np.floor(L / n_short_blocks))
    if L != sub_win_len * n_short_blocks:
        frame = frame[0:sub_win_len * n_short_blocks]
    # sub_wins is of size [n_short_blocks x L]
    sub_wins = frame.reshape(sub_win_len, n_short_blocks, order='F').copy()

    # Compute normalized sub-frame energies:
    s = np.sum(sub_wins ** 2, axis=0) / (Eol + eps)

    # Compute entropy of the normalized sub-frame energies:
    Entropy = -np.sum(s * np.log2(s + eps))
    return Entropy


def stEnergy(frame):
    """Computes signal energy of frame"""
    return np.sum(frame ** 2) / np.float64(len(frame))


def stZCR(frame):
    """Computes zero crossing rate of frame"""
    count = len(frame)
    countZ = np.sum(np.abs(np.diff(np.sign(frame)))) / 2
    return (np.float64(countZ) / np.float64(count - 1.0))


def mfccInitFilterBanks(fs, nfft):
    """
    Computes the triangular filterbank for MFCC computation 
    (used in the stFeatureExtraction function before the stMFCC function call)
    This function is taken from the scikits.talkbox library (MIT Licence):
    https://pypi.python.org/pypi/scikits.talkbox
    """

    # filter bank params:
    lowfreq = 133.33
    linsc = 200 / 3.
    logsc = 1.0711703
    numLinFiltTotal = 13
    numLogFilt = 27

    if fs < 8000:
        nlogfil = 5

    # Total number of filters
    nFiltTotal = numLinFiltTotal + numLogFilt

    # Compute frequency points of the triangle:
    freqs = np.zeros(nFiltTotal + 2)
    freqs[:numLinFiltTotal] = lowfreq + np.arange(numLinFiltTotal) * linsc
    freqs[numLinFiltTotal:] = freqs[numLinFiltTotal - 1] * \
                              logsc ** np.arange(1, numLogFilt + 3)
    heights = 2. / (freqs[2:] - freqs[0:-2])

    # Compute filterbank coeff (in fft domain, in bins)
    fbank = np.zeros((nFiltTotal, nfft))
    nfreqs = np.arange(nfft) / (1. * nfft) * fs

    for i in range(nFiltTotal):
        lowTrFreq = freqs[i]
        cenTrFreq = freqs[i + 1]
        highTrFreq = freqs[i + 2]

        lid = np.arange(np.floor(lowTrFreq * nfft / fs) + 1,
                        np.floor(cenTrFreq * nfft / fs) + 1,
                        dtype=int)
        lslope = heights[i] / (cenTrFreq - lowTrFreq)
        rid = np.arange(np.floor(cenTrFreq * nfft / fs) + 1,
                        np.floor(highTrFreq * nfft / fs) + 1,
                        dtype=int)
        rslope = heights[i] / (highTrFreq - cenTrFreq)
        fbank[i][lid] = lslope * (nfreqs[lid] - lowTrFreq)
        fbank[i][rid] = rslope * (highTrFreq - nfreqs[rid])

    return fbank, freqs


def stChromaFeaturesInit(nfft, fs):
    """
    This function initializes the chroma matrices used in the calculation of the chroma features
    """
    freqs = np.array([((f + 1) * fs) / (2 * nfft) for f in range(nfft)])
    Cp = 27.50
    nChroma = np.round(12.0 * np.log2(freqs / Cp)).astype(int)

    nFreqsPerChroma = np.zeros((nChroma.shape[0],))

    uChroma = np.unique(nChroma)
    for u in uChroma:
        idx = np.nonzero(nChroma == u)
        nFreqsPerChroma[idx] = idx[0].shape

    return nChroma, nFreqsPerChroma


def stFeatureExtraction(signal: np.ndarray, sample_rate: int,
                        window_size: int, window_steps: int) -> Union[np.ndarray, List[Union[str, List[str]]]]:
    window_size = int(window_size)
    window_steps = int(window_steps)
    # normalization
    signal = np.double(signal)

    signal = signal / (2.0 ** 15)
    DC = signal.mean()
    MAX = (np.abs(signal)).max()
    signal = (signal - DC) / (MAX + 0.0000000001)
    N = len(signal)  # total number of samples
    cur_p = 0
    count_fr = 0
    nFFT = int(window_size / 2)

    [fbank, freqs] = mfccInitFilterBanks(sample_rate, nFFT)
    nChroma, nFreqsPerChroma = stChromaFeaturesInit(nFFT, sample_rate)

    n_time_spectral_feats = 8
    n_harmonic_feats = 0
    n_mfcc_feats = 13
    n_chroma_feats = 13
    n_total_feats = n_time_spectral_feats + n_mfcc_feats + n_harmonic_feats + n_chroma_feats
    #    n_total_feats = n_time_spectral_feats + n_mfcc_feats + n_harmonic_feats
    feature_names = []
    feature_names.append("zcr")
    feature_names.append("energy")
    feature_names.append("energy_entropy")
    feature_names += ["spectral_centroid", "spectral_spread"]
    feature_names.append("spectral_entropy")
    feature_names.append("spectral_flux")
    feature_names.append("spectral_rolloff")
    feature_names += ["mfcc_{0:d}".format(mfcc_i)
                      for mfcc_i in range(1, n_mfcc_feats + 1)]
    feature_names += ["chroma_{0:d}".format(chroma_i)
                      for chroma_i in range(1, n_chroma_feats)]
    feature_names.append("chroma_std")
    st_features = []
    while (cur_p + window_size - 1 < N):  # for each short-term window_sizedow until the end of signal
        count_fr += 1
        x = signal[cur_p:cur_p + window_size]  # get current window
        cur_p = cur_p + window_steps  # update window position
        X = abs(fft(x))  # get fft magnitude
        X = X[0:nFFT]  # normalize fft
        X = X / len(X)
        if count_fr == 1:
            X_prev = X.copy()  # keep previous fft mag (used in spectral flux)
        curFV = np.zeros((n_total_feats, 1))
        curFV[0] = stZCR(x)  # zero crossing rate
        curFV[1] = stEnergy(x)  # short-term energy
        curFV[2] = stEnergyEntropy(x)  # short-term entropy of energy
        [curFV[3], curFV[4]] = stSpectralCentroidAndSpread(X, sample_rate)  # spectral centroid and spread
        curFV[5] = stSpectralEntropy(X)  # spectral entropy
        curFV[6] = stSpectralFlux(X, X_prev)  # spectral flux
        curFV[7] = stSpectralRollOff(X, 0.90, sample_rate)  # spectral rolloff
        curFV[n_time_spectral_feats:n_time_spectral_feats + n_mfcc_feats, 0] = \
            stMFCC(X, fbank, n_mfcc_feats).copy()  # MFCCs
        chromaNames, chromaF = stChromaFeatures(X, sample_rate, nChroma, nFreqsPerChroma)
        curFV[n_time_spectral_feats + n_mfcc_feats:
              n_time_spectral_feats + n_mfcc_feats + n_chroma_feats - 1] = \
            chromaF
        curFV[n_time_spectral_feats + n_mfcc_feats + n_chroma_feats - 1] = \
            chromaF.std()
        st_features.append(curFV)
        # delta features
        '''
        if count_fr>1:
            delta = curFV - prevFV
            curFVFinal = numpy.concatenate((curFV, delta))            
        else:
            curFVFinal = numpy.concatenate((curFV, curFV))
        prevFV = curFV
        st_features.append(curFVFinal)        
        '''
        # end of delta
        X_prev = X.copy()

    st_features = np.concatenate(st_features, 1)
    return st_features, feature_names


def stereo2mono(x: np.ndarray) -> Union[int, np.ndarray]:
    """_summary_

        chuyển đổi từ stereo sang mono

    Args:
        x (np.ndarray): _description_

    Returns:
        Union[int, np.ndarray]: _description_
    """
    if isinstance(x, int):
        return -1
    if x.ndim == 1:
        return x
    elif x.ndim == 2:
        if x.shape[1] == 1:
            return x.flatten()
        else:
            if x.shape[1] == 2:
                return ((x[:, 1] / 2) + (x[:, 0] / 2))
            else:
                return -1


def silenceRemoval(x: np.ndarray, sample_rate: int,
                   window_size: int, window_steps: int,
                   smoothing_window: float = 0.5, weight: float = 0.2) -> torch.Tensor:
    # feature extraction

    # convert stereo to mono
    x: Union[int, np.ndarray] = stereo2mono(x)
    st_features, feature_names = stFeatureExtraction(
        x, sample_rate, window_size * sample_rate, window_steps * sample_rate)

    # Step 2: train binary svm classifier of low vs high energy frames
    # keep only the energy short-term sequence (2nd feature)
    st_energy = st_features[1, :]
    en = np.sort(st_energy)
    # number of 10% of the total short-term windows
    l1 = int(len(en) / 10)
    # compute "lower" 10% energy threshold
    t1 = np.mean(en[0:l1]) + 0.000000000000001
    # compute "higher" 10% energy threshold
    t2 = np.mean(en[-l1:-1]) + 0.000000000000001
    # get all features that correspond to low energy
    class1 = st_features[:, np.where(st_energy <= t1)[0]]
    # get all features that correspond to high energy
    class2 = st_features[:, np.where(st_energy >= t2)[0]]
    # form the binary classification task and ...
    faets_s = [class1.T, class2.T]
    # normalize and train the respective svm probabilistic model
    # (ONSET vs SILENCE)

    [faets_s_norm, means_s, stds_s] = normalizeFeatures(faets_s)
    svm = trainSVM(faets_s_norm, 1.0)

    # Step 3: compute onset probability based on the trained svm
    prob_on_set = []
    for i in range(st_features.shape[1]):
        # for each frame
        cur_fv = (st_features[:, i] - means_s) / stds_s
        # get svm probability (that it belongs to the ONSET class)
        prob_on_set.append(svm.predict_proba(cur_fv.reshape(1, -1))[0][1])
    prob_on_set = np.array(prob_on_set)
    # smooth probability:
    prob_on_set = smoothMovingAvg(prob_on_set, smoothing_window / window_steps)

    # Step 4A: detect onset frame indices:
    prog_on_set_sort = np.sort(prob_on_set)
    # find probability Threshold as a weighted average
    # of top 10% and lower 10% of the values
    Nt = int(prog_on_set_sort.shape[0] / 10)
    T = (np.mean((1 - weight) * prog_on_set_sort[0:Nt]) +
         weight * np.mean(prog_on_set_sort[-Nt::]))

    max_idx = np.where(prob_on_set > T)[0]
    # get the indices of the frames that satisfy the thresholding
    i = 0
    time_clusters = []
    seg_limits = []

    # Step 4B: group frame indices to onset segments
    while i < len(max_idx):
        # for each of the detected onset indices
        cur_cluster = [max_idx[i]]
        if i == len(max_idx) - 1:
            break
        while max_idx[i + 1] - cur_cluster[-1] <= 2:
            cur_cluster.append(max_idx[i + 1])
            i += 1
            if i == len(max_idx) - 1:
                break
        i += 1
        time_clusters.append(cur_cluster)
        seg_limits.append([cur_cluster[0] * window_steps,
                           cur_cluster[-1] * window_steps])

    # Step 5: Post process: remove very small segments:
    min_dur = 0.3
    seg_limits_2 = []
    for s in seg_limits:
        if s[1] - s[0] > min_dur:
            seg_limits_2.append(s)
    seg_limits = seg_limits_2

    return seg_limits


def process_remove(waveform: Union[str, np.ndarray, torch.Tensor], sample_rate: int,
                   silent_waveform: np.ndarray,
                   smoothingWindow: float = 0.5, weight: float = 0.2, ) -> Union[np.ndarray, torch.Tensor]:
    if isinstance(waveform, str):
        waveform, sample_rate = torchaudio.load(waveform)
    elif isinstance(waveform, np.ndarray):
        waveform = torch.as_tensor(waveform).float()
    waveform = torchaudio.transforms.Resample(
        orig_freq=sample_rate, new_freq=assets.INPUT_SAMPLE_RATE)(waveform)
    waveform = waveform.squeeze()

    segments = silenceRemoval(waveform, assets.INPUT_SAMPLE_RATE, 0.03, 0.03, smoothingWindow, weight)
    mask = np.zeros(waveform.shape, dtype=bool)

    results = []
    for i, s in enumerate(segments):
        results.append(
            np.array(waveform[int(assets.INPUT_SAMPLE_RATE * s[0]):int(assets.INPUT_SAMPLE_RATE * s[1])])
        )
        results.append(silent_waveform.copy())

    return results, segments