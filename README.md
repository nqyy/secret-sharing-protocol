ECE 438 Final project: Secret Sharing Protocol
==============================================

Introduction
------------
This serves as the final project for ECE 438. A real-world implementation based on Shamir's Secret Sharing algorithm. This is a P2P application layer network protocol.

Directory Structure
-------------------
```
secret_sharing_protocol/ .... Top src dir
|-- lib/ .................... Secret sharing and network library
    |-- AES.py .............. AES file encryption and decryption lib
    |-- message.py .......... Network message lib
    |-- secret_sharing.py ... Secret sharing lib
    |-- tcp_socket.py ....... Special network socket lib
|-- safe/ ................... A safe storing encrypted file and decrypted file
|-- LICENSE ................. Full license text
|-- peer_ip.txt ............. Act like a server file storing all the peers in the network
|-- peer.py ................. The main executing file *
|-- README .................. Intro, links, build info
|-- requirement.txt ......... Requirements for building
```

Implementation Details
----------------------

Usage
-----

Requirements
------------
Packages installation guide: ``pip install -r requirement.txt``

Please use Python3

Requirements: pycrypto

Reference
---------
Shamir Adi, "How to share a secret", https://cs.jhu.edu/~sdoshi/crypto/papers/shamirturing.pdf.

PyCryptodome, "Secret Sharing", https://github.com/Legrandin/pycryptodome/blob/master/lib/Crypto/Protocol/SecretSharing.py.

Notice
------
All rights reserved.