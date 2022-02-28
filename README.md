# GNURadio implementation of LoRa transmitter and receiver

This module contains a modular implementation of LoRa. Transmitter (Tx) and receiver (Rx) chains are, at the best possible extent, broken down into atomic building blocks. Only the timing and carrier frequency offset tracking-enables chirp spread spectrum (CSS) demodulator is implemented in a monolithic way, as GNURadio does not allow efficient loops in the flowgraph.

This modularity is meant to:
 - easily experiment with LoRa physical layer variations (different error correcting code, preamble pattern, etc.),
 - use this implementation as pedagogic material: part of Tx/Rx chains could be re-implemented as an exercise, subtilities of real-world physical layer implementation are clearly visible (for example: different Tx/Rx chain depending on header or payload, padding bits).

# Installation

## Under linux

Within `gr-lora2` directory, and as a regular user:
```sh
$ mkdir build
$ cd build
$ cmake ..
$ make -j4
```
A root:
```sh
# make install
# ldconfig
```

# Examples

Several example GNURadio-companion flowgraph are present in `examples/GRC`:
 - `lora_test.grc`: LoRa Tx/Rx in a simple flowgraph with no channel, for sanity checks
 - `lora_tx.grc`: A LoRa transmitter
 - `lora_rx.grc`: A LoRa receiver
 - `lora_soft_test.grc`: Soft decoding LoRa Tx/Rx in a simple flowgraph with no channel, for sanity checks
 - `lora_soft_rx.grc`: A LoRa receiver using soft decoding

## How to send LoRa packets
`lora_test.grc` or `lora_tx.grc` expect data coming from UDP datagrams on port 52002: payload of received UDP datagram are transferred into the payload of LoRa packets, and sent.
That means that some care is needed to make sure that the payload length of the input UDP datagram can fit in one LoRa packet (this depends on the spreading factor and the coding rate).

Both flowgraph need the following parameters to be specified:
 - `SF`: LoRa spreading factor.
 - `CR`: LoRa coding rate.
 - `has_crc`: whether or not to append a LoRa CRC at the end of the packet.

`lora_tx.grc` expects an SDR supported by osmocom sink, and the following additional parameters:
 - `RF_samp_rate`: the sample rate of your SDR (in Hz).
 - `chan_freq`: the center frequency of the channel you wish to use (in Hz).
 - `chan_bw`: the bandwidth of the channel you wish to use (in Hz).

## How to receive LoRa packets
`lora_test.grc`, `lora_rx.grc`, `lora_soft_test.grc`, `lora_soft_rx.grc` will transfer the payload of the received LoRa packets to the payload of UDP datagrams sent on port 52001.

All flowgraphs need the following parameters to be specified:
 - `SF`: LoRa spreading factor.

`lora_rx.grc` and `lora_soft_rx.grc` expect an SDR supported by osmocom source, and the following additional parameters:
 - `RF_samp_rate`: the sample rate of your SDR (in Hz).
 - `chan_freq`: the center frequency of the channel you wish to use (in Hz).
 - `chan_bw`: the bandwidth of the channel you wish to use (in Hz).

# Related material

(Earlier) development of this module lead to the publication of the following research articles:
- A. Marquet, N. Montavont, G. Papadopoulos, **Investigating Theoretical Performance and Demodulation Techniques for LoRa**. _2019 IEEE 20th International Symposium on "A World of Wireless, Mobile and Multimedia Networks" (WoWMoM)_, Jun 2019, Washington, United States. pp.1-6, [⟨10.1109/WoWMoM.2019.8793014⟩](https://dx.doi.org/10.1109/WoWMoM.2019.8793014). [⟨hal-02284110⟩](https://hal.archives-ouvertes.fr/hal-02284110).
- A. Marquet, N. Montavont, G. Papadopoulos, **Towards an SDR implementation of LoRa: Reverse-engineering, demodulation strategies and assessment over Rayleigh channel**. _Computer Communications_, Elsevier, 2020, 153, pp.595-605. [⟨10.1016/j.comcom.2020.02.034⟩](https://dx.doi.org/10.1016/j.comcom.2020.02.034). [⟨hal-02485052⟩](https://hal.archives-ouvertes.fr/hal-02485052).
- A. Marquet, N. Montavont, **Carrier and Symbol Synchronisation for LoRa Receivers**. _International Conference on Embedded Wireless Systems and Networks_, Feb 2020, Lyon, France. pp.277-282. [⟨hal-02860476⟩](https://hal.archives-ouvertes.fr/hal-02860476).

All this work was either built upon or inspired by similar efforts. You will find below references and implementations that had significant impact on this work.

Articles:
 - M. Knight, B. Seeber, **Decoding LoRa: Realizing a Modern LPWAN with SDR**. _Proceedings of the GNU Radio Conference_, v. 1, n. 1, sep. 2016. Available at: <[https://pubs.gnuradio.org/index.php/grcon/article/view/8](https://pubs.gnuradio.org/index.php/grcon/article/view/8)>.
 - P. Robyns, P. Quax, W. Lamotte and W. Thenaers, **A Multi-Channel Software Decoder for the LoRa Modulation Scheme**. _Proceedings of the 3rd International Conference on Internet of Things, Big Data and Security - IoTBDS,_ ISBN 978-989-758-296-7; ISSN 2184-4976, pages 41-51. DOI: 10.5220/0006668400410051.
 - R. Ghanaatian, O. Afisiadis, M. Cotting and A. Burg, **Lora Digital Receiver Analysis and Implementation**. _ICASSP 2019 - 2019 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_, 2019, pp. 1498-1502, doi: 10.1109/ICASSP.2019.8683504.
 - J. Tapparel, O. Afisiadis, P. Mayoraz, A. Balatsoukas-Stimming and A. Burg, **An Open-Source LoRa Physical Layer Prototype on GNU Radio**. _2020 IEEE 21st International Workshop on Signal Processing Advances in Wireless Communications (SPAWC)_, 2020, pp. 1-5, doi: 10.1109/SPAWC48557.2020.9154273.
 - M. Xhonneux, O. Afisiadis, D. Bol and J. Louveaux, **A Low-Complexity LoRa Synchronization Algorithm Robust to Sampling Time Offsets**. _IEEE Internet of Things Journal_, vol. 9, no. 5, pp. 3756-3769, 1 March1, 2022, doi: 10.1109/JIOT.2021.3101002.
 - C. Bernier, F. Dehmas and N. Deparis, **Low Complexity LoRa Frame Synchronization for Ultra-Low Power Software-Defined Radios**. _IEEE Transactions on Communications_, vol. 68, no. 5, pp. 3140-3152, May 2020, doi: 10.1109/TCOMM.2020.2974464.

Other LoRa implementations:
 - https://github.com/BastilleResearch/gr-lora
 - https://github.com/rpp0/gr-lora
 - https://github.com/tapparelj/gr-lora_sdr
 - https://github.com/f4exb/sdrangel (see chirpchat)

