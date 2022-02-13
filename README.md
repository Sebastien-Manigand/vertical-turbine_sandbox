# vertical-turbine_sandbox

Vertical wind turbine sandbox simulating the averaged torque on a three-blade vertical turbine with standard NACA blade profiles.

## Project content

This simulation sandbox allows the user to set most of the simulation parameters: The number of setting simulated, the wind speed range, the turbine speed range, the blade tilt angle range and the dimension of the turbine. The project includes 4 python script and 1 data file necessary for a proper execution:
- naca_profile3.xml: This file contains all the drift and lift coefficients curves of the naca profiles, provided in a free version by Heliciel (the data are not really accurate). 

The database is detailed at: https://www.heliciel.com/aerodynamique-hydrodynamique/base%20de%20donnee%20profils%20aerodynamique%20hydrodynamique.htm.

The database itself is available at: https://www.heliciel.com/bases%20performances%20profils/naca_heliciel3.zip,

- xmlHandling.py: This script provide the functions to read the xml database of naca foiler profiles. These function are used by the other scripts.
- Foiler.py: This script defines the physic engine class for the vertical turbine,
- analyseOutput.py: This script analyse the output file of the simulation. It better works for a grid a results.
- main.py: This is the main script of the sandbox to launch in command line. It run an user interface to change the setting of the simulation and display the results as it runs. 

![view](https://user-images.githubusercontent.com/57091666/153756461-8a288f40-5271-40f0-9cd5-072c283c018c.png)

The simulation can show all the steps as an animation or skeep the animation to speed up the execution. At the end of the simulation, the script write the result of the simulation in an output file, if the option has been checked. The result can be plotted by running the script "analyseOutput.py". The following figures show an example of simulation with the same settings as in the top figure:

![avgTorque_tspeed-wspeed](https://user-images.githubusercontent.com/57091666/153756525-d059118e-bcbd-40a1-8ecd-8a4444ae145f.png)
![avgTorque_tspeed-tilt](https://user-images.githubusercontent.com/57091666/153756526-f107e1f4-26ef-4dcd-80a6-16a54b6b8a98.png)
