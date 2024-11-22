# Control de Temperatura del Reactor

Una simulación en Python de un sistema de control de temperatura para un reactor químico, con implementaciones tanto de control en lazo abierto como control PID.

## Características

- Simulación en tiempo real de temperaturas del reactor y de la camisa
- Controles GUI interactivos para:
  - Control en lazo abierto con ajuste manual de posición de válvula
  - Control PID con parámetros ajustables (Kp, Ki, Kd)
  - Modificación del punto de ajuste
- Gráficas en tiempo real de:
  - Temperatura del reactor
  - Temperatura de la camisa
  - Posición de la válvula (en modo control PID)

## Archivos

- `Simulacion_Reactor_Lazo_Abierto.py` - Simulación de control en lazo abierto
- `Simulacion_Reactor_Controlador.py` - Simulación de control PID

## Dependencias

- NumPy
- SciPy
- Matplotlib
- Tkinter

## Uso

Ejecute cualquiera de las simulaciones:
La ventana de simulación aparecerá con gráficas de temperatura e interfaz de control.

Lazo abierto: Ajuste manualmente la posición de la válvula usando el deslizador
![image](https://github.com/user-attachments/assets/d991f84b-cb0a-41ee-b12c-73d8375cafb5)

Control PID: Modifique los parámetros PID y el punto de ajuste según sea necesario
![image](https://github.com/user-attachments/assets/8f44c01a-276b-4931-a0db-ceb8d9f10bc3)
