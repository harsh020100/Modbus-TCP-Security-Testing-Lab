import sys
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

def connect_to_modbus_server(ip):
    client = ModbusTcpClient(ip, port=502)
    if not client.connect():
        print(f"Failed to connect to Modbus server at {ip}:502")
        sys.exit(1)
    print(f"Successfully connected to Modbus server at {ip}:502")
    return client

def read_coils(client):
    try:
        address = int(input("Enter the starting address: "))
        count = int(input("Enter the number of coils to read: "))
        response = client.read_coils(address, count)
        if response.isError():
            print(f"Error reading coils: {response}")
        else:
            # Convert the bits to 0 and 1
            coil_values = [1 if bit else 0 for bit in response.bits]
            print(f"Coils at address {address}: {coil_values}")
    except ValueError:
        print("Invalid input. Please enter numeric values.")

def write_coils(client):
    try:
        address = int(input("Enter the starting address: "))
        values = input("Enter the coil values as comma-separated (e.g., 1,0,1): ")
        values = [int(v) for v in values.split(",")]
        response = client.write_coils(address, values)
        if response.isError():
            print(f"Error writing coils: {response}")
        else:
            print(f"Successfully wrote {len(values)} coils starting at address {address}.")
    except ValueError:
        print("Invalid input. Please enter numeric values.")

def read_registers(client):
    try:
        address = int(input("Enter the starting address: "))
        count = int(input("Enter the number of registers to read: "))
        response = client.read_holding_registers(address, count)
        if response.isError():
            print(f"Error reading registers: {response}")
        else:
            print(f"Registers at address {address}: {response.registers}")
    except ValueError:
        print("Invalid input. Please enter numeric values.")

def write_registers(client):
    try:
        address = int(input("Enter the starting address: "))
        values = input("Enter the register values as comma-separated (e.g., 123,456): ")
        values = [int(v) for v in values.split(",")]
        response = client.write_registers(address, values)
        if response.isError():
            print(f"Error writing registers: {response}")
        else:
            print(f"Successfully wrote {len(values)} registers starting at address {address}.")
    except ValueError:
        print("Invalid input. Please enter numeric values.")

def menu(client):
    while True:
        print("\nMenu:")
        print("1. Read Coils")
        print("2. Write Coils")
        print("3. Read Registers")
        print("4. Write Registers")
        print("5. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            read_coils(client)
        elif choice == "2":
            write_coils(client)
        elif choice == "3":
            read_registers(client)
        elif choice == "4":
            write_registers(client)
        elif choice == "5":
            print("Exiting...")
            client.close()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python modbus_client.py <IP_ADDRESS>")
        sys.exit(1)

    ip_address = sys.argv[1]
    client = connect_to_modbus_server(ip_address)
    menu(client)
