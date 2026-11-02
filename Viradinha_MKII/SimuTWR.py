from rocketpy import Environment, GenericMotor, Rocket, Flight

env = Environment(latitude=41.726083, longitude=0.111083, elevation=192)

import datetime
env.set_date((2026, 7, 15, 12))  
env.set_atmospheric_model(type="windy", file="ECMWF")

Viradinha_motor = GenericMotor.load_from_eng_file("datos/motores/Cesaroni_176H123.eng")

Viradinha = Rocket(
    radius=0.0787/2,
    mass=1.596,   #1624-228 del motor
    inertia=(0.451, 0.451, 0.004),
    power_off_drag="datos/aero/CD_MachOFF.txt",
    power_on_drag="datos/aero/CD_MachOn.txt",
    center_of_mass_without_motor=0.446,
    coordinate_system_orientation="tail_to_nose",
)

Viradinha.add_motor(Viradinha_motor, position=0)

rail_buttons = Viradinha.set_rail_buttons(
    upper_button_position=0.555,
    lower_button_position=0.05,
    angular_position=45,
)

nose_cone = Viradinha.add_nose(
    length=0.286, 
    kind="von karman", 
    position=1.31, 
    base_radius=0.0787/2
)

fin_set = Viradinha.add_trapezoidal_fins(
    n=4,
    root_chord=0.11,
    tip_chord=0.04,
    span=0.072,
    sweep_length=0.094,
    position=0.11,
    airfoil=("datos/aero/NACA0018_Cl_Alpha.txt", "degrees"),
)

tail = Viradinha.add_tail(
    top_radius=0.087/2,
    bottom_radius=0.08699/2,
    length=0.05,
    position=0.05
)
    

main = Viradinha.add_parachute(
    name="Parachute",
    cd_s=0.8,
    trigger=200,      
    sampling_rate=60,
    lag=0,
)

Viradinha.draw()
Viradinha.static_margin.plot()

test_flight = Flight(rocket=Viradinha, environment=env, rail_length=2.3, inclination=90, heading=0)

test_flight.export_data("Viradinha_flight_data.csv")

#TWR




#TWR
import matplotlib.pyplot as plt

# 1. Suponiendo que ya tienes tus objetos 'my_rocket' y 'my_flight'
# 'my_flight' debe haber sido ejecutado: my_flight.post_process()

# 2. Obtenemos los datos temporales
times = Viradinha.out_of_burn_time_steps  # Tiempos durante la combustión
thrust = [Viradinha.motor.thrust(t) for t in times]
mass = [Viradinha.mass(t) for t in times]
g = 9.80665

# 3. Calculamos el TWR
twr = [T / (M * g) for T, M in zip(thrust, mass)]

# 4. Graficar el resultado
plt.plot(times, twr)
plt.xlabel('Tiempo (s)')
plt.ylabel('Thrust-to-Weight Ratio (TWR)')
plt.title('Evolución del TWR durante el vuelo')
plt.grid(True)
plt.show()