# MoCEGS Project Code

Repository accompanies the manuscript:

Uncovering the Energy Infrastructure in Europe: Digital Twin Optimization and Interpretation via Multi-Way Analysis

Sin Yong Teng<sup>a*</sup>, Ákos Orosz<sup>b</sup>, Jean Pimentel<sup>c</sup>, Jeroen J. Jansen<sup>a</sup>, Ferenc Friedler<sup>c</sup>,

<sup>a</sup>Radboud University, Institute for Molecules and Materials, P.O. Box 9010, 6500 GL Nijmegen, the Netherlands 

<sup>b</sup>University of Pannonia, Egyetem u. 10, 8200, Veszprém, Hungary

<sup>c</sup>Széchenyi István University (University of Győr), Egyetem tér 1, 9026, Győr, Hungary



# Instructions to Run Software

1. Install all Python dependencies
2. Obtain token for ENTSOE API via https://www.entsoe.eu/ and transparency@entsoe.eu
3. Put the token in the base directory as "token.txt".
4. Run "energy_env_factor_runwrapper.py". Warning this takes very long.
5. Results are generated as zipped files.




# Notes for understanding

- Upon starting python code, the data (large) will be download for the relevant timeframe for the first time. This takes a long time.
- All the necessary settings can be changed in the "energy_env_factor_runwrapper.py" file.
- Results will be generated in currently empty folder. Especially Pareto1, Pareto2, Pareto3, Pareto4. These results are zipped files due to their large sizes.
- Most of figures are not automatically plotted by default. This is to save computation time.



Contact:
Sin Yong Teng 
Radboud University Nijmegen
sinyong.teng@ru.nl
