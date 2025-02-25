# MoCEGS Project Code: High-resolution Large-scale Power Network Model as a Digital Twin for the European Region

Repository accompanies the manuscript:

Uncovering the Energy Infrastructure in Europe: Dynamic Data Insights for Policy Impact Analysis

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



# Other Model Information

| Property            | Details |
|---------------------|---------|
| **Model Name**      | Macro-level Power Model for European Countries and Neighbouring Countries |
| **Overview**        | The model automatically collects the most updated data from ENTSO-E via API. This model treats every single substation as model nodes, and every 30 minutes as a single timeslice. A Pareto front is then generated for the optimal network (usually for a year) to analyse the trade-off of costs and sustainability factor for the region. Multiple policy scenario is also provided. |
| **Purpose**        | To analyse policy, trade-offs and optimality of power within the European Region (including neighbouring countries), with substation resolution and 30-minute frequency. |
| **Intended Domain** | Power management, optimization, and infrastructure of the European Union, European region, or neighbouring countries. |
| **Training Data**   | Directly queried in real-time from ENTSOE API in 30-min frequency for the intended period (default= 1 Jan 2023 to 31 Dec 2023). Temporarily missing data are being interpolated linearly. |
| **Model Information** | [Details about the model architecture, parameters, and key components] |
| **Inputs and Outputs** | Input: Real-time power price, loads, generation (by source). Back-up power prices when real-time prices are unavailable, environmental factors for power generation, network topology, policy scenario, and trade-off factors. Output: Optimal network generation and power transfer for every time slice based on policy scenario. Environmental factors and costs factor for the European region |
| **Performance Metrics** | Environmental factor and cost factor for the overall region |
| **Bias**           | ENTSOE API is the most complete database available for the European region, however,r there might be some missing data that is still possible. |
| **Robustness**     | The model performs well under the assumption that the data is accurate. Optimality is achieved for all cases, providing robustness for the solution. Our model also can allow N-best solution, where other near-optimal solutions can be also generated (if there is interest). |
| **Domain Shift**   | The model can be used for other domains provided that there is a high frequency of price, loads and generation that acts in a complex network. Possible domains include hydrogen network, heat network, etc. |
| **Test Data**      | Test data is not relevant for this model |
| **Optimal Conditions** | The model performs well when there are no missing data that is queried and all substations of study are included. |
| **Poor Conditions** | The model performs poorly when there are large amounts of missing data and there are changes in substations in the duration of study |
| **Explanation**    | The model is functioning based on a data-driven multiple-time slice P-graph model that is automatically constructed based on the historical connectivity of power within the region. |
| **Contact Information** | For any inquiries, contact Sin Yong Teng. Details below. |



Contact:
Sin Yong Teng 
Radboud University Nijmegen
sinyong.teng@ru.nl
