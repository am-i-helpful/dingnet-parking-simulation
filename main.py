import math
import simpy
import random
from typing import TypeVar


# Below are certain assumptions of the parking simulation, which can be further refined based on real-world scenario:
# ---------------------------------------------------------------------------------------------------------------------
# At any point of time, the number of vehicles parked in all the parking stations can't be more than 100
# The inbound rate of arrival of the vehicles is assumed as 0-2 vehicles (per 5 minutes) to each of the 4 parking zones
# The outbound rate of departure of the vehicles is assumed as 2-3 vehicles (per 30 minutes) from all 4 parking zones
# ---------------------------------------------------------------------------------------------------------------------
vehicle_arrival_rate = random.randint(4, 7)  # per 5 minutes, to be configured in algorithm
vehicle_departure_rate = random.randint(2, 4)  # per 30 minutes, to be configured in algorithm


class ParkingLocation(object):
    __Name = ''
    __AccessValue = 0
    __Available: int = 0
    __Occupied: int = 0
    __MotePowerValue: int = 0
    __MoteSamplingRateValue: int = 0

    def __str__(self) -> str:
        return self.__Name

    def __init__(self, name, access_value, availability, occupancy):
        self.__Name = name
        self.__AccessValue = access_value
        self.__Available = availability
        self.__Occupied = occupancy
        self.__MotePowerValue = 1
        self.__MoteSamplingRateValue = 1

    def get_available_spots(self):
        return self.__Available

    def get_occupied_spots(self):
        return self.__Occupied

    def set_occupied_spots(self, arg_occupied: int):
        self.__Occupied = arg_occupied

    def get_parking_mote_power(self):
        return self.__MotePowerValue

    def set_parking_mote_power(self, arg_power: int):
        self.__MotePowerValue = arg_power

    def get_parking_mote_sampling_rate(self):
        return self.__MoteSamplingRateValue

    def set_parking_mote_sampling_rate(self, arg_sampling_rate: int):
        self.__MoteSamplingRateValue = arg_sampling_rate

    def successor(self):
        element = self.__AccessValue
        if element + 1 > 4:
            element = 0
        return element + 1

    def predecessor(self):
        element = self.__AccessValue
        if element - 1 < 1:
            element = 5
        return element - 1

    def get_neighbours(self):
        list_of_parking_preference = []
        if self.__Name == 'North':
            list_of_parking_preference.extend(['East', 'West', 'South'])
        elif self.__Name == 'West':
            list_of_parking_preference.extend(['North', 'South', 'East'])
        elif self.__Name == 'South':
            list_of_parking_preference.extend(['West', 'East', 'North'])
        elif self.__Name == 'East':
            list_of_parking_preference.extend(['South', 'North', 'West'])
        return list_of_parking_preference


Type_ParkingLocation = TypeVar("Type_ParkingLocation", bound=ParkingLocation)
# referenced from https://stackoverflow.com/questions/55751368/python-how-to-pass-to-a-function-argument-type-of-a-class-object-typing


def main():
    print("Beginning with the parking-system simulation!")
    print("=========================================================")
    # ------ Below code is based on an example given at https://realpython.com/simpy-simulating-with-python/ ------#
    # -------------------------------------------------------------------------------------------------------------#
    # Set up the environment
    env = simpy.Environment()
    random.seed(42)
    # Initialise the 4 parking locations with default values for respective motes stationed inside the parking location
    NORTH = ParkingLocation('North', 1, 100, 0)
    WEST = ParkingLocation('West', 2, 100, 0)
    SOUTH = ParkingLocation('South', 3, 100, 0)
    EAST = ParkingLocation('East', 4, 100, 0)
    list_of_parking_objects = [NORTH, WEST, SOUTH, EAST]
    # Initialise dictionary for ease in lookup of nearest neighbours in order
    dict_neighbour_lookup = {NORTH: [EAST, WEST, SOUTH], WEST: [NORTH, SOUTH, EAST], SOUTH: [WEST, EAST, NORTH],
                             EAST: [SOUTH, NORTH, WEST]}
    env.process(brain_process(env, list_of_parking_objects, dict_neighbour_lookup))
    env.run(until=60)  # Simulation to run for 60 minutes, to monitor the hourly performance of smart-parking algorithm
    # for key, value in dict_neighbour_lookup.items():
    #     temp_list = []
    #     for neighbour_names in value:
    #         temp_list.append(str(neighbour_names))
    #     print(key, temp_list)


def brain_process(env, list_of_parking_objects, dict_neighbour_lookup):
    counter = 0  # to keep track of time in the interval of 5 minutes, as every arrival or departure is in same multiple
    picked_location = None
    # let's assume total 5 vehicles already exist across different parking locations throughout the city - default state
    print("We assume that total 5 vehicles exist (by default) across different parking locations"
          f" at time: {env.now} minutes.")
    for total_vehicle in range(5):
        picked_location = random.choice(list_of_parking_objects)
        env.process(arrival_of_few_vehicles(env, picked_location, 1, dict_neighbour_lookup))
    counter += 1
    while True:
        yield env.timeout(5)  # Wait a bit (5 minutes) before generating new vehicles
        counter += 1
        current_time = env.now
        print("=========================================================")
        print(f"Overall time spent in the simulation is: {current_time} minutes currently.")

        # average rate of vehicle-arrival = 4-7 vehicles / 5 minute
        total_vehicle = random.randint(4, 7)
        print(f"Total vehicles arriving right now is: {total_vehicle}")
        picked_location = random.choice(list_of_parking_objects)
        print(f"Random parking location chosen right now is: {picked_location}")
        yield env.process(arrival_of_few_vehicles(env, picked_location, total_vehicle, dict_neighbour_lookup))

        # assuming 2-4 vehicle departure starting 30 minutes of their stay (minimum parking-duration = 30 minutes)
        if counter > 6:
            total_vehicle = random.randint(2, 4)
            print(f"Total vehicles expected to depart right now is: {total_vehicle}")
            # picked_location = random.choice(list_of_parking_objects)
            yield env.process(departure_of_few_vehicles(env, list_of_parking_objects, total_vehicle))


def arrival_of_few_vehicles(env, picked_location: Type_ParkingLocation, total_vehicle, dict_neighbour_lookup):
    get_number_of_vehicles = 0
    for vehicle in range(total_vehicle):
        returned_parking_location = parking_algorithm(picked_location, dict_neighbour_lookup)
        if returned_parking_location is None:  # if null (None) parking object is returned
            print("Can't do much, as all the parking spots across the city are occupied!")
            break
        else:
            get_number_of_vehicles = returned_parking_location.get_occupied_spots()
            print(f"Total vehicles at location '{returned_parking_location}' currently = {get_number_of_vehicles + 1}")
            # now assume that one-vehicle is parked, and increase the parking location mote's occupancy by 1
            returned_parking_location.set_occupied_spots((get_number_of_vehicles + 1))
            # TODO communicate with motes in DingNet to adjust its power
            returned_parking_location.set_parking_mote_power(set_power_wrt_number_of_vehicles((get_number_of_vehicles + 1)))
            # print("I'm executing successfully!")
    yield env.timeout(0)  # required for simulation to happen, as part of generator process


def departure_of_few_vehicles(env, list_of_parking_objects, total_vehicle):
    for vehicle in range(total_vehicle):
        picked_location = random.choice(list_of_parking_objects)
        get_number_of_vehicles = picked_location.get_occupied_spots()
        if get_number_of_vehicles > 1:
            picked_location.set_occupied_spots(get_number_of_vehicles - 1)
            print(f"Removing one vehicle from {picked_location}, as part of random departures!")
            # TODO communicate with motes in DingNet to adjust its power
            picked_location.set_parking_mote_power(set_power_wrt_number_of_vehicles((get_number_of_vehicles - 1)))
            print(f"Total vehicles at location '{picked_location}' currently = {picked_location.get_occupied_spots()}")
        else:
            print(f"Can't remove any vehicle from {picked_location}, as there are none parked here currently!")
    yield env.timeout(0)  # required for simulation to happen, as part of generator process


def set_power_wrt_number_of_vehicles(total_vehicles):
    mote_power = math.floor(total_vehicles / 7)
    if total_vehicles % 7 != 0 and total_vehicles != 0:
        mote_power = mote_power + 1
    return mote_power


# The logic of the parking algorithm revolves around the idea that incoming traffic would be dispersed
# across all parking stations. But, the critical thing to understand is that any parking location would allow
# the incoming vehicle to park till it reaches a threshold (say, 98%), and afterwards start dispersing the new arrivals
# to other/neighbouring parking stations. An important aspect of this algorithm is to find
# the ratio of dispersal of vehicles in the nearby stations, such that the parking spots are optimally occupied,
# and at the same time also achieving the optimal energy utilisation (energy)
# -------------------------------------------------------------------------------------------------------------------
# Allot vehicles to a parking station based on its occupancy or the nearest neighbour with occupancy below threshold
def parking_algorithm(parking_location: Type_ParkingLocation, dict_neighbour_lookup):
    threshold_level = 98
    # 98% occupancy means no further parking allowed in that location; 2 extra reserved for unexpected scenarios
    flag = False
    decided_parking_location = None
    power_level = parking_location.get_parking_mote_power()
    # print(f"Power level of the {parking_location} mote is currently set as: {power_level}")
    current_occupancy = parking_location.get_occupied_spots()
    # print(f"Current occupancy of the {parking_location} is: {current_occupancy}")
    # Algorithm logic follows, as stated above:
    if current_occupancy > threshold_level:
        for neighbour_name in dict_neighbour_lookup[parking_location]:
            current_occupancy = neighbour_name.get_occupied_spots()
            if current_occupancy < threshold_level:
                decided_parking_location = neighbour_name
                flag = True
                print(
                    f"Returning the parking location '{decided_parking_location}' as it is having occupancy percentage: {current_occupancy}%")
                break
    else:
        decided_parking_location = parking_location
        flag = True
        print(f"Returning the parking location '{decided_parking_location}' as it is having occupancy percentage: {current_occupancy}%")
    if not flag:
        decided_parking_location = None
        print(f"None of the parking locations have an available parking spot! So, the vehicles can't be parked currently, unfortunately!")
    return decided_parking_location


if __name__ == '__main__':
    main()
