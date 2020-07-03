# Regional Emission Metrics (REM)

## About

This repository allows to compute climate regional responses to the regional emissions of different pollutants based on global climate model simulations.  

The following responses can be calculated:

* Pulse Absolute Regional Temperature Potential (ARTP)
* Integrated Absolute Regional Temperature Potential (iARTP)
* Pulse Absolute Regional Precipitation Potential (ARPP)
* Integrated Absolute Regional Precipitation Potential (iARPP)
* Regional temperature variation
* Regional precipitation variation

The following pollutants are supported:

* SO<sub>2</sub>
* BC
* CH<sub>4</sub>
* CO<sub>2</sub>

The following emission regions can be used for SO<sub>2</sub>:

* Northern Hemisphere Mid Latitudes
* United States
* Europe
* East Asia
* India

For BC, the emission regions are:

* Global
* Asia

The following response regions are currently defined:

* Global
* Tropics
* NHML
* NHHL
* SHML
* SHHL
* Europe
* US
* China
* East Asia
* India
* Sahel

New response regions can be easily defined in the module [regions.py](simulations/regions.py).

## Setting-up the python environment

Please note the automated installation has only been tested using `conda` on a Mac.

1. Using `conda`

Create the environment `rem` and install all the required packages by running the command:

```
bash install_conda_env.sh
```

2. Using `pip`

Install all packages needed using the `requirements.txt` file:

```
pip install -r requirements.txt
```

or (try to) reproduce the development environment by using the `requirements_with_version.txt` file:

```
pip install -r requirements_with_version.txt
```

## Modules description

The repository consists of many modules grouped within different directories:

* [simulations](simulations): this directory contains modules to select input values for the response calculations, load and calculate variables from stored simulation files, define regions, apply scaling based on PDRMIP multi-model means.

* [metrics](metrics): this directory contains modules to compute regional metrics for the different pollutants.

* [scenarios](scenarios): this directory contains modules to compute temperature responses to different emission scenarios.

* [plotting](plotting): this directory contains modules for plotting responses.

* [uncertainties](uncertainties): this directory contains modules to compute and propagate uncertainties.

* [utils](utils): this directory contains utility modules (e.g., with statistical functions).

## Examples

Usage examples can be found in the following scripts:

* [so2_bc_bar_plots.py](so2_bc_bar_plots.py): computes and plots all regional temperature and precipitation potentials for emissions of SO<sub>2</sub> and BC from all emission regions.

![so2_bc_bar_plots](figures/SO2_BC_iARTP_bar_plot.png)

* [ch4_co2_bar_plots.py](ch4_co2_bar_plots.py): computes and plots all regional temperature and precipitation potentials for emissions of CH4<sub>4</sub> and CO<sub>2</sub>.

![ch4_co2_bar_plots](figures/CH4_CO2_ARPP_bar_plot.png)

* [so2_co2_mixed_temp_scenario.py](so2_co2_mixed_temp_scenario.py): computes and plots the temperature variation due to mixed emission scenarios of SO<sub>2</sub> and CO<sub>2</sub>.

![temp_mixed_scenarios](figures/SO2_CO2_temp_mixed_scenario_NHML_Europe.png)
