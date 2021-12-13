
import numpy as np
from scipy import signal
import math
import csv
import matplotlib.pyplot as plt
def read_csv(filename):
    print("----- Reading csv file -----")
    t, x, y, z = [], [], [], []

    csv_reader = csv.reader(open(f'./phase_diff/{filename}.csv'))
    for line in csv_reader:
        t.append(line[0])
        x.append(line[1])
        y.append(line[2])
        z.append(line[3])

    return t, x, y, z

def phase_detect(signal1, signal2):
    pass


def diff(signal1, signal2, signal3):
    x1 = signal1
    x2 = signal2
    x3 = signal3
    x1h = signal.hilbert(x1)
    x2h = signal.hilbert(x2)
    x3h = signal.hilbert(x3)

    c1 = np.inner(x1h, np.conj(x2h)) / math.sqrt(np.inner(x1h, np.conj(x1h)) * np.inner(x2h, np.conj(x2h)))
    phase_diff12 = np.angle(c1)
    print(f"przesuniecie12: {phase_diff12} rad")

    c2 = np.inner(x2h, np.conj(x3h)) / math.sqrt(np.inner(x2h, np.conj(x3h)) * np.inner(x3h, np.conj(x3h)))
    phase_diff23 = np.angle(c2)
    print(f"przesuniecie23: {phase_diff23} rad")

    c3 = np.inner(x1h, np.conj(x3h)) / math.sqrt(np.inner(x1h, np.conj(x3h)) * np.inner(x3h, np.conj(x3h)))
    phase_diff13 = np.angle(c3)
    print(f"przesuniecie13: {phase_diff13} rad")

    #return {"phaseXY" : phase_diff12, "phaseYZ" : phase_diff23, "phase13": phase_diff13}

def FFT(x):
    """
        A recursive implementation of
        the 1D Cooley-Tukey FFT, the
        input should have a length of
        power of 2.
        """
    N = len(x)

    if N == 1:
        return x
    else:
        X_even = FFT(x[::2])
        X_odd = FFT(x[1::2])
        factor = \
            np.exp(-2j * np.pi * np.arange(N) / N)

        X = np.concatenate( [X_even + factor[:int(N / 2)] * X_odd, X_even + factor[int(N / 2):] * X_odd])
        return X
def signal_fft(signal):
    fft1 = np.fft.fft(signal)
    fft1_freq = np.fft.fftfreq(len(fft1))
    print(fft1_freq.min(), fft1_freq.max())

    # Wyszukuje piku
    idx = np.argmax(np.abs(fft1))
    print(idx)
    freq = fft1_freq[idx]
    frate = 3200
    
    # 
    freq_in_hertz = abs(freq * frate) #*2*np.pi
    print(freq_in_hertz)
    return(freq_in_hertz)

def hilbert(x1,x2):
    Hx1 = hilbert(x1); # transformata    Hilberta    sygnału    x1
    Hx2 = hilbert(x2); # transformata    Hilberta    sygnału    x2

    y1=x1+%i*Hx1;
    y2=x2+%i*Hx2;

    #obliczenie liczby sprzężonej do y1
    ReY1=real(y1);
    ImY1=imag(y1);
    y1s=[real(y1)–%i*imag(y1)];

    #iloczyn liczb zespolonych y1s oraz y2
    M=y1s.*y2;

    #wydzielenie części rzeczywistej i urojonej z M
    ReM=real(M);
    ImM=imag(M);

    #wyznaczenie przesunięcia fazowego
    WYNIK=atan(ImM,ReM);

    #uśrednienie wyników, konwersja na stopnie
    D=sTime/(1/f);
    phase_diff=[((sum(WYNIK))/((fs/f)*D))*(180/%pi)]


if __name__ == "__main__":
    t, x, y, z = read_csv("16.4Hz") #model_obciazenie_0g.csv 16.4Hz
    #print(t)
    fft_x = signal_fft(y[3:2051])
    #FFT(z[2:205])
