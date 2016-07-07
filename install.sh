#!/bin/bash

# va al HOME
cd ~

# descarga minion y lo descomprime (ya viene compilado)
wget -O minion-1.8.tar.gz "http://constraintmodelling.org/?smd_process_download=1&download_id=226"
tar -zxvf minion-1.8.tar.gz
rm minion-1.8.tar.gz

# descarga mace4 y prover9, los descomprime y los compila
wget -O LADR.tar.gz "https://www.cs.unm.edu/~mccune/mace4/download/LADR-2009-11A.tar.gz"
tar -zxvf LADR.tar.gz 
rm LADR.tar.gz
cd LADR-2009-11A
make all
cd ..

# descarga latdraw y lo compila
wget -O LatDraw.tar "http://www.latdraw.org/latdrawsrc.tar"
tar -xvf LatDraw.tar
rm LatDraw.tar
cd LatDraw2.0/src 
ant dist
cd ../..
