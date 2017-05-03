#!/usr/bin/env python


""" Class that reads in received data from a specified file, and plots
and decodes the data. """


import numpy as np
import matplotlib.pyplot as plt


j = (0 + 1j)


class Decoder(object):

    def __init__(self, data_path, filename):

        self.data_path = data_path
        self.filename = filename
        self.data_raw = None
        self.frequency_offset = None
        self.phase_offset = None
        self.data_fixed = None

        self.samples = None


    def read_file(self):

        file_path = self.data_path + self.filename
        self.data_raw = np.fromfile(file_path, dtype=np.complex64)


    def find_offsets_bpsk(self):

        # Take the normalized data
        normalized_data = self.data_raw / np.linalg.norm(self.data_raw)
        squared_data = np.square( normalized_data )

        # Take FFT of the square of the normalized data
        fft_data = np.fft.fft( squared_data )
        fft_shape = np.fft.fftfreq( squared_data.shape[-1] )

        # Find the index of the maximum amplitude peak
        max_index = np.absolute(fft_data).argmax()

        # Extract frequency and phase offsets from the peak
        self.frequency_offset = ( fft_shape[max_index]/2 ) * (2 * np.pi)
        self.phase_offset = np.sqrt(fft_data[max_index])

        print(self.frequency_offset, self.phase_offset)


    def fix_offsets(self):

        data_fixed = np.zeros(len(self.data_raw), dtype=np.complex64)
        for i, val in enumerate(self.data_raw):
            data_fixed[i] = val * np.exp(-j * self.frequency_offset * i) / \
                    self.phase_offset

        self.data_fixed = np.array(data_fixed, dtype=np.complex64)


    def plot_data(self):

        plt.figure()
        plt.plot(self.data_fixed.real, '.', label='real')
        plt.plot(self.data_fixed.imag, '.', label='imag')
        plt.show()

    
    def sample_data(self, T):
        oldval = None
        start_index = None
        for i, val in enumerate(self.data_fixed):
            if i == 0:
                oldval = val
                continue

            if (val - oldval) > 0.0025:
                start_index = i
                break

        samples = []
        for i in range(i, len(self.data_fixed), T):
            data = self.data_fixed[i].real

            if data > 0:
                samples.append(1)
            else:
                samples.append(0)

        self.samples = np.array(samples[:36])

    
    def is_data_correct(self):
        true_data = np.loadtxt('data_in_binary.txt')

        errors = true_data - self.samples
        print( np.count_nonzero(errors) )


if __name__ == "__main__":

    data_path = '../data/'
    input_filename = 'send_1.bin'

    decoder = Decoder(data_path, input_filename)
    decoder.read_file()
    decoder.find_offsets_bpsk()
    decoder.fix_offsets()
    #decoder.plot_data()

    samples = decoder.sample_data(200)
    decoder.is_data_correct()