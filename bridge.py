import firebase_admin
from firebase_admin import credentials, db
import serial
import time
import sys
import socket
import requests

# ----------------------------
# 🔐 SETUP FIREBASE & SERIAL
# ----------------------------

# Konfigurasi
FIREBASE_URL = 'https://iot-packet-box-default-rtdb.firebaseio.com/'  # ganti sesuai punyamu
SERVICE_ACCOUNT = 'serviceAccountKey.json'  # pastikan file ini ada
SERIAL_PORT = 'COM11'  # ganti sesuai port Arduino kamu
BAUD_RATE = 9600

# 🔍 Fungsi: Cek koneksi internet
def check_internet():
    try:
        socket.gethostbyname('google.com')
        return True
    except socket.error:
        return False

# 🔍 Fungsi: Cek koneksi Firebase
def check_firebase_connection():
    try:
        r = requests.get(FIREBASE_URL + ".json", timeout=5)
        return r.status_code == 200
    except Exception as e:
        print("[❌] Gagal terhubung ke Firebase:", e)
        return False

# 🔍 Fungsi: Cek koneksi Serial ke Arduino
def connect_serial():
    try:
        arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print(f"[✅] Terhubung ke Arduino di {SERIAL_PORT}")
        time.sleep(2)
        return arduino
    except serial.SerialException as e:
        print(f"[❌] Gagal koneksi ke Arduino ({SERIAL_PORT}):", e)
        sys.exit()

# 🔧 Setup Firebase
def setup_firebase():
    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT)
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_URL
        })
        print("[✅] Firebase berhasil diinisialisasi")
    except Exception as e:
        print("[❌] Firebase gagal diinisialisasi:", e)
        sys.exit()

# ----------------------------
# 🚀 MAIN PROGRAM
# ----------------------------

if not check_internet():
    print("[❌] Tidak ada koneksi internet.")
    sys.exit()

if not check_firebase_connection():
    print("[❌] Firebase tidak dapat diakses. Cek URL atau koneksi.")
    sys.exit()

setup_firebase()
arduino = connect_serial()

command_ref = db.reference('box/command')
status_ref = db.reference('box/status')
package_ref = db.reference('box/package')

print("[⚙️] Program aktif...")

while True:
    try:
        # --- BACA SENSOR JARAK DARI ARDUINO ---
        if arduino.in_waiting:
            line = arduino.readline().decode().strip()
            if line.isdigit():
                distance = int(line)
                print(f"[📏] Jarak: {distance} cm")
                ada_paket = distance < 15
                package_ref.set(ada_paket)
            else:
                print(f"[⚠️] Data tidak valid dari Arduino: {line}")

        # --- BACA COMMAND DARI FIREBASE ---
        command = command_ref.get()
        if command in ['open', 'close']:
            print(f"[➡️] Menjalankan perintah: {command}")
            arduino.write((command + "\n").encode())
            status_ref.set(command)
            command_ref.set("none")

    except KeyboardInterrupt:
        print("\n[⛔] Dihentikan oleh user")
        break
    except Exception as e:
        print("[⚠️] Error dalam loop:", e)

    time.sleep(1)
