ECE 438 Final project: Secret Sharing Protocol
==============================================

Introduction
------------
This serves as the final project for ECE 438. A real-world implementation based on Shamir's Secret Sharing algorithm. This is a P2P application layer network protocol. A secret is distributed among a group of people so that more than a specified number of people can reconstruct the secret back together.

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
|-- MPSS.pdf ................ Detailed project paper
|-- peer_ip.txt ............. Act like a server file storing all the peers in the network
|-- peer.py ................. The main executing file *
|-- README .................. Intro, links, Usage
|-- requirement.txt ......... Requirements for building
```

Implementation Details
----------------------

``lib/`` contains all the library code including network socket, message, cryptography implementation.

The main logic file is ``peer.py`` to execute. You are able to assign role, ip:port to the peer when executing.
For dealer, it will make a random 16 byte secret and encrypt the file ``safe/secret_file.txt`` to ``safe/enc_file.enc``. The secret will be split into shares and send to the peers in the network seperately and we assume the participants already got the encrypted file ``safe/enc_file.enc``.
For peers, when dealer finished sharing the secret, they can initiate the reconstruct process to recover the secret and then use the secret to decrypt the file in ``safe/``.

``peer_ip.txt`` is the file containing all the peer ip and port. We assume all the peers in the network are able to know the peers in the network from this file in the P2P network.

Please refer to MPSS.pdf, our project paper, for more details.

Usage
-----

Please run command ``python3 peer.py`` to use the functionality.

Here is an example of how to run the program. 

Terminal 1 (participant): 
``python3 peer.py`` role: p, ip and port: 127.0.0.1:5005

Terminal 2 (participant):
``python3 peer.py`` role: p, ip and port: 127.0.0.1:5006

Terminal 3 (participant):
``python3 peer.py`` role: p, ip and port: 127.0.0.1:5007

Terminal 4 (dealer):
``python3 peer.py`` role: d, ip and port: 127.0.0.1:5001

Then the secret will be shared among the participants.

Any of 1, 2, 3 can initiate secret recovery by type in command RECONSTRUCT.

The secret will be recovered by peers and the file will be decrypted by them seperately in ``safe/``.

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