"""Relacion empuje/peso (TWR) del Viradinha MKII con el AeroTech H165R.

Mismo cohete que Simulacion_Viradinha.ipynb (masa 1.271 kg sin motor, CdM 0.505 m).
El TWR solo depende del motor y de la masa, asi que no hace falta simular el vuelo.
Uso: python SimuTWR.py
Requiere RocketPy 1.10: pip install rocketpy==1.10.0
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import importlib.metadata as _md
_v = _md.version("rocketpy")
if not (_v.startswith("1.10") or _v.startswith("1.11")):
    raise SystemExit(f"Tienes RocketPy {_v}. Este codigo esta probado con 1.10 y 1.11 (la 1.13 calcula mal la masa del "
                     "motor desde el .eng y falla con 'list index out of range'). Instala: pip install rocketpy==1.10.0")
from rocketpy import GenericMotor, Rocket

D = os.path.dirname(os.path.abspath(__file__))

Viradinha_motor = GenericMotor.load_from_eng_file(os.path.join(D, "datos", "motores", "AeroTech_H165R.eng"))

Viradinha = Rocket(
    radius=0.0787/2,
    mass=1.271, #sin motor
    inertia=(0.451, 0.451, 0.004),
    power_off_drag=os.path.join(D, "datos", "aero", "CD_MachOFF.txt"),
    power_on_drag=os.path.join(D, "datos", "aero", "CD_MachOn.txt"),
    center_of_mass_without_motor=0.505,
    coordinate_system_orientation="tail_to_nose",
)
Viradinha.add_motor(Viradinha_motor, position=0.03)

#TWR
g = 9.80665
times = np.linspace(0, Viradinha_motor.burn_out_time, 500)  # tiempos durante la combustion
thrust = np.array([Viradinha_motor.thrust(t) for t in times])
mass = np.array([Viradinha.total_mass(t) for t in times])  # cohete + motor (el propelente se va gastando)
twr = thrust / (mass * g)

print(f"Masa al despegue: {mass[0]:.3f} kg")
print(f"TWR maximo: {twr.max():.1f} (t = {times[twr.argmax()]:.2f} s)")
print(f"TWR medio durante la combustion: {twr.mean():.1f}")

plt.plot(times, twr)
plt.axhline(5, color="gray", linestyle="--", label="TWR = 5 (minimo habitual)")
plt.xlabel('Tiempo (s)')
plt.ylabel('Thrust-to-Weight Ratio (TWR)')
plt.title('Evolución del TWR durante la combustión (H165R)')
plt.legend()
plt.grid(True)
plt.show()
