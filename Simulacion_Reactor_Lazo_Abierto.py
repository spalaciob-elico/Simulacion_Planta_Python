import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import time
import tkinter as tk
from tkinter import ttk

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
        sol = solve_ivp(self.model, [t, t + dt], self.y, method='RK45')
        self.y = sol.y[:, -1]
        return self.y

class GUI:
    def __init__(self, reactor, plotter):
        self.reactor = reactor
        self.plotter = plotter
        self.running = True  # Add flag for program control
        self.window = self._create_control_window()
        
    def _create_control_window(self):
        window = tk.Tk()
        window.title("Reactor Control")
        window.geometry("300x180+1000+20")

        slider_frame = ttk.Frame(window)
        slider_frame.pack(pady=5)
        
        slider_value = ttk.Label(slider_frame, text=f"{self.reactor.av:.2f}")
        
        def on_slider_move(event):
            slider_value.config(text=f"{slider.get():.2f}")
        
        slider = ttk.Scale(slider_frame, from_=0, to=1, orient='horizontal',
                          length=200, command=on_slider_move)
        slider.set(self.reactor.av)
        
        slider.pack(side='left', padx=(0, 5))
        slider_value.pack(side='left')
        
        value_label = ttk.Label(window, text=f"Current av: {self.reactor.av:.2f}")
        value_label.pack(pady=5)
        
        def apply_value():
            self.reactor.av = slider.get()
            value_label.config(text=f"Current av: {self.reactor.av:.2f}")
            self.plotter.update_title(self.reactor.av)
            
        apply_button = ttk.Button(window, text="Apply", command=apply_value)
        apply_button.pack(pady=10)
        
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
    def __init__(self, window_size=1000):
        self.window_size = window_size
        self.time_values = []
        self.T_values = []
        self.Tj_values = []
        self._setup_plots()
        
    def _setup_plots(self):
        plt.ion()
        self.fig = plt.figure(figsize=(8, 8))
        self.fig.canvas.manager.window.geometry("+20+20")
        
        # Add tight_layout and adjust spacing
        plt.subplots_adjust(hspace=0.3)  # Increase vertical space between subplots
        plt.suptitle("Reactor Temperature Control", y=0.95)  # Move suptitle up
        
        plt.subplot(2,1,1)
        plt.xlabel("Time (s)")
        plt.ylabel("Temperature (°C)")
        plt.grid(True)
        self.line1, = plt.plot([], [], label="Reactor Temperature (T)")
        plt.legend()
        plt.xlim(0, self.window_size)
        plt.ylim(0, 100)
        
        plt.subplot(2,1,2)
        plt.title("Jacket Temperature Over Time", pad=10)  # Add padding to title
        plt.xlabel("Time (s)")
        plt.ylabel("Temperature (°C)")
        plt.grid(True)
        self.line2, = plt.plot([], [], label="Jacket Temperature (Tj)")
        plt.legend()
        plt.xlim(0, self.window_size)
        plt.ylim(0, 100)
    
    def update(self, t, T, Tj):
        self.time_values.append(t)
        self.T_values.append(T)
        self.Tj_values.append(Tj)
        
        self.line1.set_data(self.time_values, self.T_values)
        self.line2.set_data(self.time_values, self.Tj_values)
        
        if t > self.window_size:
            plt.subplot(2,1,1)
            plt.xlim(t - self.window_size, t)
            plt.subplot(2,1,2)
            plt.xlim(t - self.window_size, t)
        
        plt.draw()
        plt.pause(0.01)
    
    def update_title(self, av):
        plt.subplot(2,1,1)
        plt.title(f"Reactor Temperature Over Time (av={av:.2f})")
        plt.subplot(2,1,2)
        plt.title(f"Jacket Temperature Over Time (av={av:.2f})")

class Simulation:
    def __init__(self):
        self.reactor = Reactor()
        self.plotter = Plotter()
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
