# Simulaciones-RocketPy

Colección de simulaciones de [RocketPy](https://github.com/RocketPy-Team/RocketPy) de los cohetes de Solaris GNC.
Cada cohete tiene su carpeta con sus simulaciones y sus datos (motor, curvas aerodinámicas, ficheros de OpenRocket).

## Cohetes

| Cohete | Carpeta | Motor | Estado |
|---|---|---|---|
| Viradinha MKII | [Viradinha_MKII/](Viradinha_MKII/) | AeroTech H165R | Simulación + Monte Carlo |
| ErgueCeos | [ErgueCeos/](ErgueCeos/) | — | Pendiente |

## Estructura de cada cohete

```
<Cohete>/
├── README.md        qué es el cohete, cómo ejecutar sus simulaciones, resultados
├── *.ipynb / *.py   simulaciones
├── openrocket/      ficheros .ork
└── datos/
    ├── motores/     curvas de empuje (.eng)
    └── aero/        Cd vs Mach, Cl vs alfa, ...
```

Las rutas de los datos son relativas a la carpeta del cohete: ejecuta los notebooks/scripts desde ella.

## Instalación

```
pip install -r requirements.txt
```

Las simulaciones están probadas con **RocketPy 1.10 / 1.11**. La 1.13 calcula mal la masa del motor
desde el `.eng` y falla con `list index out of range`.
