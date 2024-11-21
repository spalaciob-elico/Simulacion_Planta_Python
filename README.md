![Simulacion_Lazo_Abierto](https://github.com/user-attachments/assets/b1bd077b-1115-4446-80ce-3a96c4a41f38)

### Componentes Principales

1. Clase Reactor:
- Maneja el modelo físico del reactor con temperaturas y flujos
- Implementa ecuaciones diferenciales para transferencia de calor
- Resuelve las ecuaciones paso a paso usando solve_ivp

- Contiene constantes físicas (cp, densidad, coeficientes de transferencia)

2. Clase GUI:
- Crea ventana de control con slider (0-1) para posición de válvula
- Muestra valor actual de la válvula
- Tiene botones de aplicar y salir
- Actualiza parámetros del reactor en tiempo real

3. Clase Plotter:
- Crea dos gráficos en tiempo real: temperaturas del reactor y chaqueta
- Actualiza los gráficos con nuevos valores 
- Mantiene una ventana deslizante de datos
- Auto-escala conforme avanza el tiempo

4. Clase Simulation:
- Coordina todos los componentes
- Ejecuta el bucle principal de simulación
- Maneja tiempos y actualizaciones
- Gestiona tiempo real vs tiempo de simulación

### Flujo del Programa
1. Crea instancia de simulación
2. Abre ventana de control y gráficos
3. Continuamente:
   - Actualiza GUI
   - Resuelve ecuaciones del reactor
   - Actualiza gráficos
   - Maneja pasos de tiempo
4. Corre hasta que el usuario presione salir

El sistema simula un reactor químico con control de temperatura mediante posición de válvula (av), mostrando en tiempo real las respuestas de temperatura tanto del reactor como de la chaqueta de enfriamiento.



