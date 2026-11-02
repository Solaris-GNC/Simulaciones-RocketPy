"""Monte Carlo Viradinha MkII con el paracaidas real (Klima 125 cm) y despliegue por retardo.

Reconstruido a partir de montecalo.py del equipo y de la tabla de dispersiones del TR (5.2):
viento personalizado X/Y +-10 %, inclinacion 87/70 +-1.1 %, rumbo 90 +-2.2 %, rail 2.5 +-5 %,
masa 1.242 +-5 %, CdM 0.503 +-1 %, geometria <1 %, 200 simulaciones.
Cambios: Cd*S = 0.8 * pi * 0.625^2 (Klima 125 cm, Cd 0.8 como en OpenRocket) y despliegue a
t = apagado + 8 s (retardo del motor) en lugar de a 200 m.
Uso: python Montecarlo_Viradinha.py nom|adv [n]   (nom = nominal, adv = adverso; n por defecto 200)
Requiere RocketPy 1.10: pip install rocketpy==1.10.0
"""
import sys, os, json, warnings, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import importlib.metadata as _md
_v = _md.version("rocketpy")
if not (_v.startswith("1.10") or _v.startswith("1.11")):
    raise SystemExit(f"Tienes RocketPy {_v}. Este codigo esta probado con 1.10 y 1.11 (la 1.13 calcula mal la masa del "
                     "motor desde el .eng y falla con 'list index out of range'). Instala: pip install rocketpy==1.10.0")
from rocketpy import Environment, GenericMotor, Rocket, Flight, MonteCarlo
from rocketpy.stochastic import (StochasticEnvironment, StochasticFlight, StochasticNoseCone,
                                 StochasticParachute, StochasticRocket, StochasticGenericMotor,
                                 StochasticTail, StochasticTrapezoidalFins)

# Sin argumentos (p. ej. el boton "Run" de VS Code): corre nominal y adverso seguidos.
if len(sys.argv) < 2:
    import subprocess
    for _esc in ("nom", "adv"):
        print(f"===== Monte Carlo {_esc} =====", flush=True)
        subprocess.run([sys.executable, os.path.abspath(__file__), _esc], check=True)
    sys.exit(0)
ESC = sys.argv[1]
if ESC not in ("nom", "adv"):
    sys.exit("Escenario desconocido: usa nom o adv")
N = int(sys.argv[2]) if len(sys.argv) > 2 else 200
D = os.path.dirname(os.path.abspath(__file__))
SRC = D
OUT = os.path.join(D, "montecarlo_" + ESC)
os.makedirs(OUT, exist_ok=True)
np.random.seed(20261005)
# Semilla fija tambien para RocketPy: sus modelos estocasticos crean generadores con
# np.random.default_rng(None) (aleatorio en cada ejecucion). Se les da una semilla fija
# por orden de creacion, para que el Monte Carlo sea reproducible.
import random as _random
_random.seed(20261005)
_rng_orig = np.random.default_rng
_rng_n = [0]
def _rng_fijo(seed=None, *a, **k):
    if seed is None:
        _rng_n[0] += 1
        seed = 20261005 + _rng_n[0]
    return _rng_orig(seed, *a, **k)
np.random.default_rng = _rng_fijo

WX, WY, INC = {"nom": (-3.36, 0.2, 87.0), "adv": (-8.9, 0.5, 70.0)}[ESC]
CDS = 0.8 * math.pi * 0.625 ** 2
DELAY = 8.0

# --- el tiempo para el disparador por retardo (RocketPy no lo pasa al trigger) ---
_T = {"t": 0.0}
# RocketPy 1.10 calcula la presion del nodo justo antes de llamar al trigger: ahi se guarda t
_orig = Flight._Flight__calculate_and_save_pressure_signals
def _pres(self, parachute, t, z):
    _T["t"] = t
    return _orig(self, parachute, t, z)
Flight._Flight__calculate_and_save_pressure_signals = _pres

env = Environment(latitude=41.726083, longitude=0.111083, elevation=192)
env.set_atmospheric_model(type="custom_atmosphere", wind_u=WX, wind_v=WY)
stochastic_env = StochasticEnvironment(environment=env, wind_velocity_x_factor=(1, 0.10),
                                       wind_velocity_y_factor=(1, 0.10))

motor = GenericMotor.load_from_eng_file(os.path.join(SRC, "datos", "motores", "AeroTech_H165R.eng"))
T_BURN = motor.burn_out_time
def retardo(p, h, y):
    return _T["t"] >= T_BURN + DELAY

stochastic_motor = StochasticGenericMotor(motor)
rocket = Rocket(radius=0.0787 / 2, mass=1.271, inertia=(0.451, 0.451, 0.004),
                power_off_drag=os.path.join(D, "datos", "aero", "CD_MachOFF.txt"), power_on_drag=os.path.join(D, "datos", "aero", "CD_MachOn.txt"),
                center_of_mass_without_motor=0.505, coordinate_system_orientation="tail_to_nose")
rocket.add_motor(motor, position=0.03)
rocket.set_rail_buttons(upper_button_position=0.755, lower_button_position=0.085, angular_position=45)
nose = rocket.add_nose(length=0.230, kind="von karman", position=1.23, base_radius=0.0787 / 2)
fins = rocket.add_trapezoidal_fins(n=4, root_chord=0.11, tip_chord=0.04, span=0.072, sweep_length=0.07,
                                   position=0.11, airfoil=(os.path.join(D, "datos", "aero", "NACA0018_Cl_Alpha.txt"), "degrees"))
tail = rocket.add_tail(top_radius=0.0787 / 2, bottom_radius=0.078699 / 2, length=0.05, position=0.05)
main = rocket.add_parachute(name="Klima 125 cm", cd_s=CDS, trigger=retardo, sampling_rate=60, lag=0.001)

srocket = StochasticRocket(rocket=rocket, radius=(0.0787 / 2, 0.0004, "normal"), mass=(1.271, 0.0636, "normal"),
                           power_off_drag=[os.path.join(D, "datos", "aero", "CD_MachOFF.txt")], power_on_drag=[os.path.join(D, "datos", "aero", "CD_MachOn.txt")],
                           center_of_mass_without_motor=(0.505, 0.00505, "normal"))
srocket.add_motor(stochastic_motor, position=(0.03, 0.005, "normal"))
srocket.add_nose(StochasticNoseCone(nosecone=nose, length=(0.230, 0.0023, "normal"), base_radius=(0.0787 / 2, 0.0004, "normal")))
srocket.add_trapezoidal_fins(StochasticTrapezoidalFins(trapezoidal_fins=fins, root_chord=(0.11, 0.0011, "normal"),
                                                       tip_chord=(0.04, 0.0004, "normal"), span=(0.072, 0.0007, "normal")))
srocket.add_tail(StochasticTail(tail=tail, top_radius=(0.0787 / 2, 0.0004, "normal"), bottom_radius=(0.078699 / 2, 0.0004, "normal"),
                                length=(0.05, 0.0005, "normal")))
srocket.add_parachute(StochasticParachute(parachute=main, cd_s=(CDS, 0.06 * CDS, "normal"), lag=(0.001, 0.2, "uniform")))

flight = Flight(rocket=rocket, environment=env, rail_length=2.5, inclination=INC, heading=90)
sflight = StochasticFlight(flight=flight, inclination=(INC, 0.011 * INC, "normal"), heading=(90, 1.98, "normal"),
                           rail_length=(2.5, 0.125, "normal"))

# ---- vuelo determinista: graficas de estabilidad, trayectoria y Vz ----
r = {"burnout": T_BURN, "apogee": flight.apogee - env.elevation, "t_apogee": flight.apogee_time,
     "deploy_t": [e[0] for e in flight.parachute_events], "x_impact": flight.x_impact, "y_impact": flight.y_impact,
     "impact_velocity": flight.impact_velocity, "out_of_rail_time": flight.out_of_rail_time,
     "stab_min": float(min(flight.stability_margin.y_array)), "stab_max": float(max(flight.stability_margin.y_array)),
     "static_margin": float(flight.static_margin(0)), "stab_end": float(flight.stability_margin.y_array[-1])}
vz = flight.vz.y_array; t = flight.vz.x_array
r["vz_descent"] = float(np.mean(vz[t > flight.apogee_time + 3]))
json.dump(r, open(os.path.join(OUT, "determinista.json"), "w"), indent=1, default=float)
print("DETERMINISTA", json.dumps(r, default=float))

flight.stability_margin.plot(filename=os.path.join(OUT, "stability.png"))
flight.vz.plot(filename=os.path.join(OUT, "vz.png"))
flight.plots.trajectory_3d(filename=os.path.join(OUT, "traj3d.png"))

if N > 0:
    warnings.filterwarnings("ignore")
    mc = MonteCarlo(filename=os.path.join(OUT, "mc"), environment=stochastic_env, rocket=srocket, flight=sflight)
    mc.simulate(number_of_simulations=N, append=False, parallel=False)
    res = mc.results
    out = {}
    for k in ("apogee", "x_impact", "y_impact", "impact_velocity", "apogee_x", "apogee_y", "out_of_rail_velocity",
              "frontal_surface_wind", "lateral_surface_wind", "max_mach_number"):
        if k in res:
            a = np.array(res[k], dtype=float)
            if k == "apogee":
                a = a - env.elevation  # sobre el suelo (AGL), como en el TR
            out[k] = {"mean": a.mean(), "std": a.std(), "p2.5": np.percentile(a, 2.5), "p97.5": np.percentile(a, 97.5),
                      "min": a.min(), "max": a.max()}
    if "x_impact" in res:
        dr = np.hypot(np.array(res["x_impact"]), np.array(res["y_impact"]))
        out["drift"] = {"mean": dr.mean(), "min": dr.min(), "max": dr.max(), "p2.5": np.percentile(dr, 2.5), "p97.5": np.percentile(dr, 97.5)}
    out["n"] = len(res.get("apogee", []))
    out["keys"] = sorted(res.keys())
    json.dump(out, open(os.path.join(OUT, "mc_resumen.json"), "w"), indent=1, default=float)
    print("MC", json.dumps(out, default=float))

# ---------------- figuras con el formato del TR (Fig. 10-18) ----------------
from matplotlib.patches import Ellipse
SIZE = {10: (902, 468), 11: (904, 467), 12: (783, 596), 13: (677, 530), 14: (803, 590),
        15: (747, 580), 16: (748, 572), 17: (943, 421), 18: (1153, 563)}
def fig(n):
    w, h = SIZE[n]
    return plt.figure(figsize=(w / 100, h / 100), dpi=100)


def save(n):
    plt.savefig(os.path.join(OUT, f"Figura_{n:02d}.png"), dpi=100)
    plt.close("all")




def tray3d(f, n, elev, azim):
    alt = f.altitude[:, 1]; x = f.x[:, 1]; y = f.y[:, 1]
    min_z, max_z = alt.min(), alt.max()
    min_xy, max_xy = min(x.min(), y.min()), max(x.max(), y.max())
    fig(n)
    ax = plt.subplot(111, projection="3d")
    ax.plot(x, y, zs=min_z, zdir="z", linestyle="--")
    ax.plot(x, alt, zs=min_xy, zdir="y", linestyle="--")
    ax.plot(y, alt, zs=min_xy, zdir="x", linestyle="--")
    ax.plot(x, y, alt, linewidth=2)
    ax.scatter(0, 0, 0, color="black")
    ax.scatter(f.x(f.t_final), f.y(f.t_final), f.z(f.t_final) - f.env.elevation, color="red", marker="X")
    ax.set_xlabel("X - East (m)"); ax.set_ylabel("Y - North (m)"); ax.set_zlabel("Z - Altitude Above Ground Level (m)")
    ax.set_xlim(min_xy, max_xy); ax.set_ylim(min_xy, max_xy); ax.set_zlim(0, max_z)
    ax.view_init(elev, azim)
    plt.subplots_adjust(left=0, right=1, bottom=0.02, top=1)
    save(n)


def funcion(f, attr, n, titulo, ylab, wide=False):
    fn = getattr(f, attr)
    fig(n)
    plt.plot(fn.x_array, fn.y_array)
    plt.title(titulo); plt.xlabel("Time (S)"); plt.ylabel(ylab); plt.grid(True)
    plt.subplots_adjust(left=0.07 if wide else 0.13, right=0.97, bottom=0.12, top=0.9)
    save(n)


def elipses(r, n, xlim, ylim):
    from rocketpy.plots.monte_carlo_plots import generate_monte_carlo_ellipses
    imp, apo = generate_monte_carlo_ellipses(r["apogee_x"], r["apogee_y"], r["x_impact"], r["y_impact"])
    fig(n)
    ax = plt.subplot(111)
    for e in imp:
        e.set_facecolor((0, 0, 1, 0.2)); e.set_edgecolor((0, 0, 0.5, 0.3)); ax.add_artist(e)
    for e in apo:
        e.set_facecolor((0, 1, 0, 0.2)); e.set_edgecolor((0, 0.5, 0, 0.3)); ax.add_artist(e)
    plt.axhline(0, color="black", linewidth=0.8); plt.axvline(0, color="black", linewidth=0.8)
    ax.scatter(0, 0, s=30, marker="*", color="black", label="Launch Point")
    ax.scatter(r["apogee_x"], r["apogee_y"], s=5, marker="^", color="green", label="Simulated Apogee")
    ax.scatter(r["x_impact"], r["y_impact"], s=5, marker="v", color="blue", label="Simulated Landing Point")
    ax.legend()
    ax.set_title(r"1$\sigma$, 2$\sigma$ and 3$\sigma$ Monte Carlo Ellipses")
    ax.set_ylabel("Y (m)"); ax.set_xlabel("X (m)")
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    plt.subplots_adjust(left=0.09, right=0.95, bottom=0.13, top=0.92)
    fw = plt.gcf()
    bb = ax.get_position()
    fw.text(bb.x0 - 0.075, bb.y1, "North", ha="left", va="top"); fw.text(bb.x0 - 0.075, bb.y0 + 0.02, "South", ha="left", va="bottom")
    fw.text(bb.x0 - 0.04, bb.y0 - 0.1, "West", ha="left", va="top"); fw.text(bb.x1 + 0.04, bb.y0 - 0.1, "East", ha="right", va="top")
    save(n)
    # semiejes 3 sigma: extremos de la elipse de impacto exterior
    e = imp[-1]
    return e



nst, n3d, nvz, nel = {"nom": (10, 12, 15, 17), "adv": (11, 14, 16, 18)}[ESC]
funcion(flight, "stability_margin", nst, "Stability Margin (C) x Time (S)", "Stability Margin (C)", wide=True)
funcion(flight, "vz", nvz, "Vz (M/S) x Time (S)", "Vz (M/S)")
tray3d(flight, n3d, 15, -135)
if ESC == "nom":
    tray3d(flight, 13, 15, -95)
if N > 0:
    rr = {k: np.array(v, dtype=float) for k, v in res.items() if k in ("apogee_x", "apogee_y", "x_impact", "y_impact")}
    lim = {"nom": ((-370, 130), (-95, 105)), "adv": ((-600, 400), (-185, 235))}[ESC]
    elipses(rr, nel, *lim)
print("Figuras guardadas en", OUT)
