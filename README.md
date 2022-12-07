#### Parking Management Simulation (for DingNet IoT exemplar)

* This is a Python-based simulation for modelling the arrival and departure of vehicles
in various parking locations spread across the city, and accordingly configure the power of motes 
stationed in those parking locations
* The implementation is inspired from https://realpython.com/simpy-simulating-with-python/
* In our use-case, we have considered following assumptions to keep the approach simpler 
(but all of these can be extended further):
  - overall 4 different parking locations throughout the city: North, East, West, and South 
  (each having one mote stationed, and dedicated for assisting in smart parking and efficient energy utilisation)
  - total 5 vehicles exist by default across different parking locations throughout the city
  - average rate of vehicle-arrival = 4-7 vehicles / 5 minute
  - assuming 2-4 vehicle departure starting 30 minutes of their stay (minimum parking-duration = 30 minutes)
  - total duration of simulation = 1 hour

* To run this program, on terminal/cmd you can simply navigate to the directory where the main.py file is present, 
and then run "python main.py", and you can see the output with simulation results.