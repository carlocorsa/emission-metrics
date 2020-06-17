# List of available pollutants
POLLUTANTS = ['SO2', 'BC', 'CO2', 'CH4']

# Radiative efficiency
A_CO2 = 1.76e-15  # W m-2 kg-1 (Myhre et al. 2013, used by Shine et al. 2015)
A_CH4 = 2.11e-13  # W m-2 kg-1 (Myhre et al. 2013, used by Shine et al. 2015)

# Climate sensitivity (K/m^2)
C1 = 0.631
C2 = 0.429

# Timescale of climate sensitivity (yr)
D = [8.4, 409.5]
D1 = 8.4
D2 = 409.5

# Conversion factor from latent heat to precipitation units
CF = 0.034

# Factor that relates the change in RF due to surface T changes
K = 2.2  # W m-2 K-1

# Standard time horizons
H1 = 100
H2 = 20

# List of available emission regions
EMISS_REGIONS = ['NHML', 'US', 'China', 'EastAsia', 'India', 'Europe']

# List of available emission regions for BC
BC_EMISS_REGIONS = ['Global', 'Asia']

# Pollutant specific constants
SPECS = {

    'SO2': {
        'tau': 4.35 / 365,  # Wang et al. (2013) (1 SO2 + 4 SO4),
        'fp': -0.4,  # Kvalevag et al. (2013) used by Shine et al. (2015),
        'k': 2.678,  # std = 0.317 - All k values were given by Bjorn from his paper Samset et al. (2018)
    },

    'BC': {
        'tau': 6.8 / 365,  # Wang et al. (2014) also cited by Hodnebrog et al. (2014)
        'fp': 1,  # because we are using RFa instead of RF -
                  # otherwise use 6.2 from Kvalevag et al. (2013) used by Shine et al. (2015)
        'k': 2.675,  # std = 0.819
    },

    'CO2': {
        'tau': [172.9, 18.51, 1.186],  # Collins et al. (2013)
        'a0': 0.217,
        'ai': [0.259, 0.338, 0.186],
        'fp': 1,  # because we are using RFa instead of RF -
                  # Otherwise use 0.6 from Kvalevag et al. (2013) used by Shine et al. (2015)
        'k': 2.470  # std = 0.160
    },

    'CH4': {
        'f': 1.24,  # from Voulgarakis et al. (2012) # Collins et al. (2013) -> 1.34
        'tau': 9.7 * 1.24,  # std = 1.5 from Naik et al. (2013) (1.24 is the factor f)
                            # check also 9.1 * f -std = 0.9 from Prather et al. (2012)
                            # check also Collins et al. (2013) -> 8.7 * f and Myhre et al. (2013) -> 12.4 yr
        'fp': 1,  # because we are using RFa instead of RF
                  # Otherwise use 0.3 from Kvalevag et al. (2013) used by Shine et al. (2015)
        'k': 2.766  # std = 0.383
    }

}
