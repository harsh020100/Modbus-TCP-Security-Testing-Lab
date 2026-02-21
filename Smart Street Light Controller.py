import asyncio
import tkinter as tk
from threading import Thread
from datetime import datetime
from pymodbus.server.async_io import StartAsyncTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.client import ModbusTcpClient
import random
import time

# ============================================================
# --------------------- MODBUS SERVER ------------------------
# ============================================================

# Memory Map
# HR 4  -> Lux Threshold
# HR 6  -> Ambient Light Sensor
# COIL 3 -> Street Light Status
# COIL 4 -> Manual Override

slave_context = ModbusSlaveContext(
    co=ModbusSequentialDataBlock(1, [0] * 10),
    hr=ModbusSequentialDataBlock(1, [0] * 10),
)

context = ModbusServerContext(slaves=slave_context, single=True)


async def simulate_lux_sensor():
    while True:
        registers = context[0].getValues(3, 1, count=10)
        registers[5] = random.randint(300, 900)
        context[0].setValues(3, 1, registers)
        await asyncio.sleep(3)


async def street_light_logic():
    while True:
        registers = context[0].getValues(3, 1, count=10)
        coils = context[0].getValues(1, 1, count=10)

        threshold = registers[3]
        ambient = registers[5]
        override = coils[3]

        if override:
            coils[2] = 1
        else:
            coils[2] = 1 if ambient < threshold else 0

        context[0].setValues(1, 1, coils)
        await asyncio.sleep(1)


async def start_server():
    registers = context[0].getValues(3, 1, count=10)

    # HIGH INITIAL THRESHOLD → LIGHT STARTS ON
    registers[3] = 2000
    context[0].setValues(3, 1, registers)

    identity = ModbusDeviceIdentification()
    identity.VendorName = "harshsecurity "
    identity.ProductName = "Smart Street Light PLC"
    identity.ProductCode = "Programmable Logic Controller"
    identity.MajorMinorRevision = "1.0"

    print("Modbus Server Running on Port 502...")

    await asyncio.gather(
        simulate_lux_sensor(),
        street_light_logic(),
        StartAsyncTcpServer(
            context=context,
            identity=identity,
            address=("0.0.0.0", 502),
        )
    )

# ============================================================
# --------------------- SCADA HMI ----------------------------
# ============================================================

class StreetLightHMI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Street Light Controller SCADA System - harshsecurity.com")
        self.root.geometry("900x520")
        self.root.configure(bg="#0f172a")
        self.polling = True

        # HEADER
        header = tk.Frame(root, bg="#111827", height=70)
        header.pack(fill="x")

        tk.Label(
            header,
            text="SMART STREET LIGHT CONTROL SYSTEM",
            bg="#111827",
            fg="#22d3ee",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left", padx=20, pady=15)

        self.clock_label = tk.Label(
            header,
            bg="#111827",
            fg="white",
            font=("Segoe UI", 12)
        )
        self.clock_label.pack(side="right", padx=20)

        # BODY
        body = tk.Frame(root, bg="#0f172a")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        # LEFT PANEL
        left_panel = tk.Frame(body, bg="#1e293b", width=400, height=380)
        left_panel.pack(side="left", fill="both", expand=True, padx=15)
        left_panel.pack_propagate(False)

        tk.Label(
            left_panel,
            text="STREET LIGHT STATUS",
            bg="#1e293b",
            fg="#38bdf8",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=15)

        self.canvas = tk.Canvas(
            left_panel,
            width=250,
            height=250,
            bg="#1e293b",
            highlightthickness=0
        )
        self.canvas.pack()

        self.glow = self.canvas.create_oval(
            40, 40, 210, 210,
            fill="#374151",
            outline=""
        )

        self.status_label = tk.Label(
            left_panel,
            text="STATUS: UNKNOWN",
            bg="#1e293b",
            fg="white",
            font=("Segoe UI", 14, "bold")
        )
        self.status_label.pack(pady=10)

        self.mode_label = tk.Label(
            left_panel,
            text="MODE: AUTO",
            bg="#1e293b",
            fg="#facc15",
            font=("Segoe UI", 12, "bold")
        )
        self.mode_label.pack()

        # RIGHT PANEL
        right_panel = tk.Frame(body, bg="#1e293b", width=400, height=380)
        right_panel.pack(side="right", fill="both", expand=True, padx=15)
        right_panel.pack_propagate(False)

        tk.Label(
            right_panel,
            text="SYSTEM PARAMETERS",
            bg="#1e293b",
            fg="#38bdf8",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=15)

        self.threshold_label = tk.Label(
            right_panel,
            text="Threshold: -- lux",
            bg="#1e293b",
            fg="white",
            font=("Segoe UI", 12)
        )
        self.threshold_label.pack(pady=5)

        self.lux_label = tk.Label(
            right_panel,
            text="Ambient Light: -- lux",
            bg="#1e293b",
            fg="white",
            font=("Segoe UI", 12)
        )
        self.lux_label.pack(pady=5)

        input_frame = tk.Frame(right_panel, bg="#1e293b")
        input_frame.pack(pady=15)

        tk.Label(
            input_frame,
            text="Set Threshold:",
            bg="#1e293b",
            fg="white",
            font=("Segoe UI", 11)
        ).grid(row=0, column=0, padx=5)

        self.threshold_input = tk.Entry(
            input_frame,
            width=8,
            font=("Segoe UI", 12),
            justify="center"
        )
        self.threshold_input.insert(0, "2000")
        self.threshold_input.grid(row=0, column=1, padx=5)

        tk.Button(
            right_panel,
            text="APPLY",
            command=self.set_threshold,
            bg="#22c55e",
            fg="white",
            width=18,
            height=2
        ).pack(pady=5)

        tk.Button(
            right_panel,
            text="TOGGLE MANUAL OVERRIDE",
            command=self.toggle_override,
            bg="#f97316",
            fg="black",
            width=22,
            height=2
        ).pack(pady=10)

        self.connection_label = tk.Label(
            right_panel,
            text="● CONNECTING",
            bg="#1e293b",
            fg="orange",
            font=("Segoe UI", 11, "bold")
        )
        self.connection_label.pack(pady=10)

        # MODBUS CLIENT
        self.client = ModbusTcpClient('127.0.0.1', port=502)
        self.connected = self.client.connect()

        if self.connected:
            self.connection_label.config(text="● CONNECTED", fg="#22c55e")
        else:
            self.connection_label.config(text="● DISCONNECTED", fg="red")

        Thread(target=self.poll_data, daemon=True).start()
        self.update_clock()

    def update_clock(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self.update_clock)

    def poll_data(self):
        while self.polling:
            try:
                light_on = self.client.read_coils(3, 1).bits[0]
                override = self.client.read_coils(4, 1).bits[0]

                regs = self.client.read_holding_registers(4, 3)
                threshold = regs.registers[0]
                ambient = regs.registers[2]

                if light_on:
                    self.canvas.itemconfig(self.glow, fill="#fde047")
                    self.status_label.config(text="STATUS: ON", fg="#fde047")
                else:
                    self.canvas.itemconfig(self.glow, fill="#374151")
                    self.status_label.config(text="STATUS: OFF", fg="white")

                mode = "MANUAL" if override else "AUTO"
                self.mode_label.config(text=f"MODE: {mode}")

                self.threshold_label.config(text=f"Threshold: {threshold} lux")
                self.lux_label.config(text=f"Ambient Light: {ambient} lux")

            except:
                self.connection_label.config(text="● CONNECTION LOST", fg="red")

            time.sleep(1)

    def set_threshold(self):
        try:
            value = int(self.threshold_input.get())
            self.client.write_register(4, value)
        except:
            pass

    def toggle_override(self):
        try:
            current = self.client.read_coils(4, 1).bits[0]
            self.client.write_coil(4, not current)
        except:
            pass

    def stop(self):
        self.polling = False
        self.client.close()
        self.root.destroy()


# ============================================================
# ----------------------- LAUNCH -----------------------------
# ============================================================

def start_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server())


def launch():
    Thread(target=start_async_loop, daemon=True).start()
    time.sleep(1)
    root = tk.Tk()
    app = StreetLightHMI(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()


if __name__ == "__main__":
    launch()