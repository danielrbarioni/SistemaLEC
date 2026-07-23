import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

def test_aghu_vm():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(os.getenv('LEC_VM_HOST', '10.34.0.202'), username=os.getenv('LEC_VM_USER', 'root'), password=os.getenv('LEC_VM_PASSWORD'))
    
    code = """
import asyncio, asyncpg

async def main():
    try:
        conn = await asyncpg.connect('postgresql://ugen_integra:aghuintegracao@10.34.0.92:6544/dbaghu')
        rows = await conn.fetch('SELECT prontuario, nome, dt_nascimento, nome_mae FROM agh.aip_pacientes LIMIT 3;')
        print('SUCCESS:', rows)
        await conn.close()
    except Exception as e:
        print('ERROR:', e)

asyncio.run(main())
"""
    cmd = f"""/var/app/sistemalec/.venv/bin/python3 -c "{code}" """
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("STDOUT:", stdout.read().decode())
    print("STDERR:", stderr.read().decode())
    ssh.close()

if __name__ == '__main__':
    test_aghu_vm()
