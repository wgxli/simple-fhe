#! /bin/bash
python3 1_keygen.py > 1_keygen.out
python3 2_encrypt.py > 2_encrypt.out
python3 3_process.py > 3_process.out
python3 4_decrypt.py > 4_decrypt.out
