import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import time
import tkinter as tk
from tkinter import ttk

class PIDController:
    def __init__(self, Kp=0.05, Ki=0.001, Kd=0.5, initial_av=0.433255):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = 31.0
        self.initial_av = initial_av
        
        # Control limits
        self.output_min = 0.0
        self.output_max = 1.0
        # Add anti-windup limits
        self.integral_min = 0
        self.integral_max = 1000.0
        self.reset()

    def reset(self):
        self.last_error = 0
        # Initialize for bumpless transfer
        self.integral = self.initial_av / self.Ki
        self.last_output = self.initial_av
        self.last_time = 0

    def compute(self, current_value, current_time):
        dt = current_time - self.last_time
        if dt <= 0: dt = 0.1
        
        error = self.setpoint - current_value
        print(f"\nTime: {current_time:.2f}s")
        print(f"Current Temperature: {current_value:.2f}°C")
        print(f"Setpoint: {self.setpoint}°C")
        print(f"Error: {error:.2f}°C")
        
        # Calculate terms
        P = self.Kp * error
        
        # Anti-windup: Only integrate if not saturated or if error will reduce saturation
        self.integral = np.clip(self.integral + error * dt, self.integral_min, self.integral_max)
        I = self.Ki * self.integral
        
        derivative = (error - self.last_error) / dt
        D = self.Kd * derivative
        
        # Print individual components
        print(f"P term: {P:.6f}")
        print(f"I term: {I:.6f}")
        print(f"D term: {D:.6f}")
        print(f"Integral value: {self.integral:.6f}")
        
        # Calculate output with limits
        output = P + I + D
        print(f"Output (before limiting): {output:.6f}")
        output = np.clip(output, self.output_min, self.output_max)
        
        print(f"Final valve position (av): {output:.6f}")
        print("-" * 50)
        
        self.last_error = error
        self.last_time = current_time
        self.last_output = output
        
        return output

class Reactor:
    def __init__(self):
        # Constants
        self.cp = 4181.3
        self.p = 1000
        self.U = 15000
        self.Ac = 9.596
        self.Vt = 3
        self.Vc = 0.5047
        self.Fmaxc = 120
        self.Fmaxh = 180
        
        # Parameters
        self.T0 = 31
        self.Tj0 = 47.7322203151538
        self.av = 0.433255
        self.Tc = 2
        self.Th = 95
        self.F = 40
        self.Ti = 16.6
        
        # State
        self.y = [self.T0, self.Tj0]
        self.controller = PIDController()
    
    def model(self, t, y):
        T, Tj = y
        Fc = self.Fmaxc * (1 - self.av)
        Fh = self.Fmaxh * self.av
        Foj = Fc + Fh
        f1 = (self.F * self.cp * self.Ti - self.F * self.cp * T + 
              self.U * self.Ac * (Tj - T)) / (self.p * self.cp * self.Vt)
        f2 = (Fc * self.cp * self.Tc + Fh * self.cp * self.Th - 
              Foj * self.cp * Tj + self.U * self.Ac * (T - Tj)) / (self.p * self.cp * self.Vc)
        return [f1, f2]
    
    def solve_step(self, t, dt):
        # Update control signal
        self.av = self.controller.compute(self.y[0], t)
        sol = solve_ivp(self.model, [t, t + dt], self.y, method='RK45')
        self.y = sol.y[:, -1]
        return self.y

class GUI:
    def __init__(self, reactor, plotter):
        self.reactor = reactor
        self.plotter = plotter
        self.running = True
        self.window = self._create_control_window()
        
    def _create_control_window(self):
        window = tk.Tk()
        window.title("Reactor Control")
        window.geometry("300x230+1100+20")

        # PID Parameters frame
        pid_frame = ttk.LabelFrame(window, text="PID Parameters")
        pid_frame.pack(pady=5, padx=5, fill="x")

        # Create entries for PID parameters
        params = [
            ("Kp:", self.reactor.controller.Kp),
            ("Ki:", self.reactor.controller.Ki),
            ("Kd:", self.reactor.controller.Kd),
            ("Setpoint:", self.reactor.controller.setpoint)
        ]

        self.pid_entries = {}
        for label, value in params:
            frame = ttk.Frame(pid_frame)
            frame.pack(fill="x", padx=5, pady=2)
            ttk.Label(frame, text=label).pack(side="left")
            entry = ttk.Entry(frame, width=10)
            entry.insert(0, str(value))
            entry.pack(side="right")
            self.pid_entries[label] = entry

        def update_pid():
            try:
                self.reactor.controller.Kp = float(self.pid_entries["Kp:"].get())
                self.reactor.controller.Ki = float(self.pid_entries["Ki:"].get())
                self.reactor.controller.Kd = float(self.pid_entries["Kd:"].get())
                new_setpoint = float(self.pid_entries["Setpoint:"].get())
                if new_setpoint != self.reactor.controller.setpoint:
                    self.reactor.controller.setpoint = new_setpoint
                    self.reactor.controller.reset()  # Reset controller state on setpoint change
                self.plotter.update_setpoint(self.reactor.controller.setpoint)
            except ValueError:
                pass

        ttk.Button(pid_frame, text="Update PID", command=update_pid).pack(pady=5)

        # Add separator
        ttk.Separator(window, orient='horizontal').pack(fill='x', pady=5)

        # Add kill button at the bottom
        def kill_program():
            self.running = False
            window.quit()
            window.destroy()
            plt.close('all')
            
        kill_button = ttk.Button(window, text="Exit Program", command=kill_program)
        kill_button.pack(pady=5)
        
        return window
    
    def update(self):
        self.window.update()

class Plotter:
    def __init__(self, window_size=1000, reactor=None):
        self.window_size = window_size
        self.reactor = reactor  # Store reactor reference
        self.time_values = []
        self.T_values = []
        self.Tj_values = []
        self.av_values = []  # Add av values array
        self.setpoint_values = []  # Add array to store setpoint history
        self.setpoint_line = None
        self._setup_plots()
        
    def _setup_plots(self):
        plt.ion()
        self.fig = plt.figure(figsize=(9, 8))  # Made figure taller for 3 subplots
        self.fig.canvas.manager.window.geometry("+20+20")
        
        plt.subplots_adjust(hspace=0.4)  # Increased spacing between subplots
        plt.suptitle("Reactor Temperature Control", y=0.95)
        
        # First subplot (Temperature)
        plt.subplot(3,1,1)  # Changed to 3,1,1
        plt.title("Reactor Temperature Over Time")
        plt.xlabel("Time (s)")
        plt.ylabel("Temperature (°C)")
        plt.grid(True)
        self.line1, = plt.plot([], [], label="Reactor Temperature (T)")
        self.setpoint_line, = plt.plot([], [], 'r--', label="Setpoint")
        plt.legend()
        plt.xlim(0, self.window_size)
        plt.ylim(10, 90)
        
        # Second subplot (Jacket Temperature)
        plt.subplot(3,1,2)  # Changed to 3,1,2
        plt.title("Jacket Temperature Over Time")  # Add padding to title
        plt.xlabel("Time (s)")
        plt.ylabel("Temperature (°C)")
        plt.grid(True)
        self.line2, = plt.plot([], [], label="Jacket Temperature (Tj)")
        plt.legend()
        plt.xlim(0, self.window_size)
        plt.ylim(10, 90)
        
        # New third subplot (Valve Position)
        plt.subplot(3,1,3)
        plt.title("Valve Position Over Time")
        plt.xlabel("Time (s)")
        plt.ylabel("av")
        plt.grid(True)
        self.line3, = plt.plot([], [], label="Valve Position (av)")
        plt.legend()
        plt.xlim(0, self.window_size)
        plt.ylim(0, 1)
    
    def update(self, t, T, Tj):
        self.time_values.append(t)
        self.T_values.append(T)
        self.Tj_values.append(Tj)
        self.av_values.append(self.reactor.av)  # Add av value
        self.setpoint_values.append(self.reactor.controller.setpoint)  # Store current setpoint
        
        self.line1.set_data(self.time_values, self.T_values)
        self.line2.set_data(self.time_values, self.Tj_values)
        self.line3.set_data(self.time_values, self.av_values)  # Update av plot
        
        # Update setpoint line with historical values
        if self.setpoint_line:
            self.setpoint_line.set_data(self.time_values, self.setpoint_values)
        
        if t > self.window_size:
            for i in range(1, 4):  # Update all three subplots
                plt.subplot(3,1,i)
                plt.xlim(t - self.window_size, t)
        
        plt.draw()
        plt.pause(0.01)
    
    def update_title(self, av):
        plt.subplot(2,1,1)
        plt.title(f"Reactor Temperature Over Time")
        plt.subplot(2,1,2)
        plt.title(f"Jacket Temperature Over Time")

    def update_setpoint(self, setpoint):
        # No need to modify historical values
        self.setpoint_values[-1] = setpoint  # Update only the latest value
        if self.time_values:
            self.setpoint_line.set_data(self.time_values, self.setpoint_values)
            plt.draw()

class Simulation:
    def __init__(self):
        self.reactor = Reactor()
        self.plotter = Plotter(reactor=self.reactor)  
        self.gui = GUI(self.reactor, self.plotter)
        self.dt = 1
        self.t = 0
        self.real_time = False
    
    def run(self):
        start_time = time.time()
        while self.gui.running:  # Modified to check running flag
            self.gui.update()
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            if elapsed_time >= self.t + self.dt or not self.real_time:
                y = self.reactor.solve_step(self.t, self.dt)
                self.t += self.dt
                self.plotter.update(self.t, y[0], y[1])
                
                if self.real_time:
                    time.sleep(self.dt)

if __name__ == "__main__":    
    simulation = Simulation()
    simulation.run()
