# 🔐 Modbus TCP Security Testing Lab

A lightweight Modbus TCP lab environment built for learning, research, and controlled security testing.

This repository simulates a small Industrial Control System (ICS) environment and provides tools to interact with it using Modbus TCP.

---

## 📂 Repository Contents

### 1️⃣ Smart Street Light Controller.py  
Simulated Modbus TCP Server (PLC) with SCADA-style HMI interface.

### 2️⃣ Mbap_client.py  
Command-line Modbus TCP client for reading and writing coils and registers.

### 3️⃣ Mbap_Polling_Tool.py  
GUI-based Modbus polling tool for continuous monitoring.

---

## 🏗 Project Overview

This lab simulates:

- Modbus TCP Server (Port 502)
- Holding Registers (HR)
- Coils
- Ambient light (lux) sensor simulation
- Threshold-based automation logic
- Manual override functionality
- SCADA monitoring interface

Designed for:

- Modbus protocol learning  
- ICS/OT lab simulation  
- Security research  
- Controlled penetration testing practice  

---

## ⚙️ Requirements

- Python 3.9+
- pymodbus
- tkinter (usually preinstalled with Python)

Install dependency:

```bash
pip install pymodbus
pip install pyserial-asyncio
```

## 🚀 How to Run

### Step 1: Start the Modbus Server + SCADA

```bash
python "Smart Street Light Controller.py"
```

This will:

- Start the Modbus TCP server on port 502  
- Launch the SCADA HMI  
- Simulate the ambient light sensor  


### Step 2: Run CLI Modbus Client

```bash
python Mbap_client.py <SERVER_IP>
```

Example:

```bash
python Mbap_client.py 127.0.0.1
```

### Step 3: Run GUI Polling Tool

```bash
python Mbap_Polling_Tool.py
```

Then enter:

- Target IP  
- Port (default: 502)  
- Polling frequency  
- Select coils/registers to monitor  

---

### 🧠 Memory Map
| Type | Address | Description            |
|------|---------|------------------------|
| Holding Register   | 4       | Lux Threshold          |
| Holding Register   | 6       | Ambient Light Sensor   |
| Coil | 3       | Street Light Status    |
| Coil | 4       | Manual Override        |

### 🎯 Learning Objectives

- Understand Modbus TCP communication  
- Interact with coils and holding registers  
- Observe automation logic  
- Practice protocol interaction  
- Analyze potential security weaknesses in Modbus  

### ⚠️ Disclaimer

This project is intended strictly for:

- Educational purposes  
- Security research  
- Testing in controlled lab environments  

Do **NOT** use this code against systems without proper authorization.

---

### 👨‍💻 Author

**Harsh Srivastava**  
IoT & OT Security Research
