#!/bin/bash
g++ -std=c++0x csi-analysis.cpp -lzip -L ~/usr/bin/libzip/lib/ -I ~/usr/bin/libzip/include/ -I ~/usr/bin/libzip/lib/libzip/include/ -o condorCsIAnalysis
