# MoCEGS Project Code: High-resolution Large-scale Power Network Model as a Digital Twin for the European Region

[![DOI](https://zenodo.org/badge/827989164.svg)](https://doi.org/10.5281/zenodo.14922201)


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


# Important pre-requisites/libraries

This model relies on our previous Pgraph library (official PyPi library): https://github.com/tsyet12/Pgraph
You may install it in this manner: pip install ProcessGraph


# Notes for understanding

- Upon starting python code, the data (large) will be download for the relevant timeframe for the first time. This takes a long time.
- All the necessary settings can be changed in the "energy_env_factor_runwrapper.py" file.
- Results will be generated in currently empty folder. Especially Pareto1, Pareto2, Pareto3, Pareto4. These results are zipped files due to their large sizes.
- Most of figures are not automatically plotted by default. This is to save computation time.


# Explanation of Folders

By default, this repository does not contain the large amount of data used for the model. Instead, the code will automatically query the necessary data upon the first instance of model building. This will take some time, and please ensure a stable internet connection for the first instance. Also, make sure that you have a token from the ENTSOE API and have saved it as "token.txt" in the repository.

Static Data
- NUTS_RG_20M_2021_3035, geoJSON_EU, ref-nuts-2021-01m: These folder contains geospatial metadata for general European Countries
- currencyRates: This folder contains the currency exchange rate for certain countries that are not using Euro as the main currency.

Automatic Input Data:
- capacity: This is 30-minute generation capacity (by energy source) data that is directly queried from ENTSOE API.
- flow: This is the 30-minute power flow data that is directly queried from ENTSOE API. (This is an optional query)
- load: This is the 30-minute power load (consumption) that is directly queried from ENTSOE API. 
- price: This is the 30-minute power price that is directly queried from ENTSOE API. 

Output Data
- P-graphs: This folder contains the generated P-graph file for every single timeslice.
- Solutions: This folder contains the generated solution summary for running the model.
- importOptimized: This folder contains all the data for substation importing energy, for every time-slice after being optimized.
- exportOptimized: This folder contains all the data for substation exporting energy, for every time-slice after being optimized.
- capacityOptimized: This folder contains all the used capacity (generation) data for substation in every time-slice after being optimized.
- Pareto1-4: These folder provides overall data for the Pareto front of Policy Scenario 1-4 after being optimized.
- Figure1-7: These folder provides the possibility to save default figures from the model. Under default settings, these figures are not generated to save computation time.

Important Code Files:
- energy_pgraph_10_optimize.py: This is the code for the main model. It is not recommended to change the code here.
- energy_env_factor_runwrapper.py: This is the runner for the code. The main variables to change are environmental environmental_impacts (This is the trade-off factor for environmental impact) and caselist (This is the policy scenario to be run).
- energy_pgraph_10_optimize_temp.py: This is a temporary copy of "energy_pgraph_10_optimize.py" on every instance for the runner file. This is done to prevent any corrupted files from happening. You do not need to change this.

Other files:
- README.md: This is the "read me" file to provide instructions for the model.
- area.csv: Default station numbering code and station letter code relation.
- areas_updated_fix.csv: Default station numbering code, station letter code and country/station code relation. Additionally, back-up prices for electricity is saved here, together with the classification of whether a station is within EU.
- dict_territories.csv: Relation of country/station code to country two-letter code.
- env.csv: Environmental emission based on different sources of power generation mainly based on IPCC.
- territory_population.csv: Population of each country within the study.
- territory_population_low.csv: Population of each country within the study. In this case, these numbers are linearly renormalized (gives lower numbers) to numerically reduce computation space.
- test_studio.pgsx: The most recent instance of P-graph is saved here for troubleshooting.



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
