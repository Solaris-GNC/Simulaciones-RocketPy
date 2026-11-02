# Viradinha MKII

Motor AeroTech H165R · paracaídas Klima 125 cm (Cd·S = 0.98 m²) con despliegue a los 8 s del apagado ·
lanzamiento en Alcolea de Cinca (192 m).

## Archivos

| Archivo | Qué hace |
|---|---|
| `Simulacion_Viradinha.ipynb` | Simulación principal (atmósfera `windy`: usa el pronóstico del día en que se ejecuta) |
| `Montecarlo_Viradinha.py` | Monte Carlo del TR, 200 simulaciones por escenario |
| `SimuTWR.py` | Cálculo del TWR (versión antigua: usa `Cesaroni_176H123.eng`, que no está en el repo) |
| `datos/motores/AeroTech_H165R.eng` | Curva de empuje |
| `datos/aero/CD_MachOFF.txt`, `CD_MachOn.txt` | Cd vs Mach motor apagado / encendido |
| `datos/aero/NACA0018_Cl_Alpha.txt` | Cl vs alfa de la aleta (raíz NACA 0018, punta NACA 0012) |
| `openrocket/` | Ficheros `.ork` (pendiente de subir `PUMEL_v3-7_Klima.ork`) |
| `CAMBIOS.txt` | Historial de cambios y correcciones |

## Ejecutar

Desde esta carpeta:

```
python Montecarlo_Viradinha.py nom    # nominal: viento 3.36 m/s, rail 87°
python Montecarlo_Viradinha.py adv    # adverso: viento 8.9 m/s, rail 70°
python Montecarlo_Viradinha.py        # los dos seguidos
```

Los resultados se guardan en `montecarlo_nom/` y `montecarlo_adv/` (no se suben al repo).

## Resultados (TR)

| Escenario | Apogeo medio | Deriva media |
|---|---|---|
| Nominal (3.36 m/s, 87°) | 401 m | 185 m |
| Adverso (8.9 m/s, 70°) | 324 m | 228 m |
