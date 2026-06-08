import paramiko
from .config import get_settings

def get_ssh_client() -> paramiko.SSHClient:
    settings = get_settings()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=settings.wendian_host,
        username=settings.wendian_user,
        password=settings.wendian_password
    )

    return client

def run_remote(command: str) -> tuple[int, str, str]:
    client = get_ssh_client()
    try:
        _, stdout, stderr = client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, stdout.read().decode(), stderr.read().decode()
    finally:
        client.close()