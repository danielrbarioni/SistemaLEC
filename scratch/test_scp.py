import subprocess
import os

vm_host = "10.34.0.202"
vm_user = "root"
vm_pass = "hc*l0ck2026"

remote_paths = [
    "/root/sistema-lec/data/app.db",
    "/home/root/sistema-lec/data/app.db",
    "/var/www/sistema-lec/data/app.db",
    "/opt/sistema-lec/data/app.db",
    "/app/data/app.db",
    "/root/data/app.db"
]

print("Script de cópia criado.")
