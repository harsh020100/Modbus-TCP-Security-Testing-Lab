import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from pymodbus.client import ModbusTcpClient
from threading import Thread
import time


class ModbusGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mbap Polling Tool - harshsecurity.com")
        self.root.geometry("800x600")
        self.root.configure(bg="#121212")

        self.client = None
        self.polling = False

        style = ttk.Style()
        style.theme_use("clam")

        # ===== GLOBAL LABEL STYLING =====
        style.configure("TLabel",
                        background="#121212",
                        foreground="white",
                        font=("Segoe UI", 10))

        style.configure("TLabelframe",
                        background="#121212",
                        foreground="white")

        style.configure("TLabelframe.Label",
                        background="#121212",
                        foreground="#00d4ff",
                        font=("Segoe UI", 10, "bold"))

        # ===== CHECKBOX STYLE (FIXED HOVER ISSUE) =====
        style.configure("TCheckbutton",
                        background="#121212",
                        foreground="white",
                        font=("Segoe UI", 10))

        style.map("TCheckbutton",
                  background=[("active", "#121212"),
                              ("selected", "#121212")],
                  foreground=[("active", "#00d4ff"),
                              ("selected", "#00ffcc")])

        # ===== BUTTON STYLE =====
        style.configure("Primary.TButton",
                        font=("Segoe UI", 10, "bold"),
                        padding=8,
                        background="#007acc",
                        foreground="white")

        style.map("Primary.TButton",
                  background=[("active", "#0099ff")],
                  foreground=[("active", "white")])

        style.configure("Danger.TButton",
                        font=("Segoe UI", 10, "bold"),
                        padding=8,
                        background="#c0392b",
                        foreground="white")

        style.map("Danger.TButton",
                  background=[("active", "#e74c3c")],
                  foreground=[("active", "white")])

        # ================= CONNECTION FRAME =================
        conn_frame = ttk.LabelFrame(root, text=" Connection Settings ")
        conn_frame.pack(fill="x", padx=20, pady=15)

        ttk.Label(conn_frame, text="Modbus Host IP:").grid(row=0, column=0, padx=10, pady=10)
        self.ip_entry = ttk.Entry(conn_frame, width=20)
        self.ip_entry.grid(row=0, column=1)

        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, padx=10)
        self.port_entry = ttk.Entry(conn_frame, width=10)
        self.port_entry.insert(0, "502")
        self.port_entry.grid(row=0, column=3)

        # ================= POLLING FRAME =================
        poll_frame = ttk.LabelFrame(root, text=" Polling Configuration ")
        poll_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(poll_frame, text="Polling Frequency (1-99 sec):").grid(row=0, column=0, padx=10, pady=10)
        self.freq_entry = ttk.Entry(poll_frame, width=10)
        self.freq_entry.insert(0, "1")
        self.freq_entry.grid(row=0, column=1)

        self.coils_var = tk.BooleanVar()
        self.registers_var = tk.BooleanVar()

        ttk.Checkbutton(
            poll_frame,
            text="Read Coils",
            variable=self.coils_var,
            cursor="hand2"
        ).grid(row=1, column=0, padx=10, sticky="w")

        ttk.Checkbutton(
            poll_frame,
            text="Read Registers",
            variable=self.registers_var,
            cursor="hand2"
        ).grid(row=1, column=1, padx=10, sticky="w")

        # ================= BUTTON FRAME =================
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=15)

        self.start_button = ttk.Button(
            btn_frame,
            text="Start Polling",
            style="Primary.TButton",
            command=self.start_polling
        )
        self.start_button.grid(row=0, column=0, padx=20)

        self.stop_button = ttk.Button(
            btn_frame,
            text="Stop Polling",
            style="Danger.TButton",
            command=self.stop_polling,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=20)

        # ================= OUTPUT FRAME =================
        output_frame = ttk.LabelFrame(root, text=" Live Output ")
        output_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.output_text = tk.Text(
            output_frame,
            bg="#000000",
            fg="#00ff66",
            insertbackground="white",
            font=("Consolas", 10)
        )
        self.output_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.output_text.configure(yscrollcommand=scrollbar.set)

        # ================= FOOTER =================
        footer = tk.Label(
            root,
            text="Powered by HarshSecurity  |  harshsecurity.com",
            bg="#121212",
            fg="#888888",
            font=("Segoe UI", 9)
        )
        footer.pack(side="bottom", pady=8)

    # ================= LOGIC (UNCHANGED) =================

    def start_polling(self):
        ip = self.ip_entry.get()
        port = self.port_entry.get()
        freq = self.freq_entry.get()

        if not ip:
            messagebox.showerror("Input Error", "Please enter a Modbus host IP address.")
            return

        try:
            port = int(port)
            if port < 1 or port > 65535:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid port number (1-65535).")
            return

        try:
            freq = int(freq)
            if freq < 1 or freq > 99:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a polling frequency between 1 and 99 seconds.")
            return

        if not self.coils_var.get() and not self.registers_var.get():
            messagebox.showerror("Input Error", "Please select at least one data type to poll.")
            return

        self.client = ModbusTcpClient(ip, port=port)
        if not self.client.connect():
            messagebox.showerror("Connection Error", "Failed to connect to Modbus host.")
            return

        self.polling_frequency = freq
        self.polling = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        Thread(target=self.poll_loop, daemon=True).start()

    def stop_polling(self):
        self.polling = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        if self.client:
            self.client.close()

    def poll_loop(self):
        while self.polling:
            output = []

            if self.coils_var.get():
                coils = self.client.read_coils(0, 10)
                if not coils.isError():
                    coil_values = [int(bit) for bit in coils.bits]
                    output.append("Coils: " + str(coil_values))
                else:
                    output.append("Coils: Read error")

            if self.registers_var.get():
                regs = self.client.read_holding_registers(0, 10)
                if not regs.isError():
                    output.append("Registers: " + str(regs.registers))
                else:
                    output.append("Registers: Read error")

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, "\n".join(output))

            time.sleep(self.polling_frequency)


root = tk.Tk()
app = ModbusGUI(root)
root.mainloop()