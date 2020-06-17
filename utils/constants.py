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
