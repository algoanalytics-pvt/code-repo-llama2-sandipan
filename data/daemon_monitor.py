import logging
import subprocess
import sys

d_dir = sys.argv[1]
logging.basicConfig(filename=f"{d_dir}/daemon_stat.log", format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S', filemode='a+', level=logging.DEBUG)
logger= logging.getLogger()

try:
    daemon_bool= False
    command = "systemctl status docker"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    daemon_status, error = process.communicate()
    if process.returncode == 0:
        if daemon_status.split("\n")[2][((daemon_status.split("\n")[2].find("(")) + 1) : (daemon_status.split("\n")[2].find(")"))] == "running":
            daemon_bool = True
        elif daemon_status.split("\n")[2][((daemon_status.split("\n")[2].find("(")) + 1) : (daemon_status.split("\n")[2].find(")"))] == "dead":
            daemon_bool = False
        elif daemon_status.split("\n")[2][((daemon_status.split("\n")[2].find("(")) + 1) : (daemon_status.split("\n")[2].find(")"))] == "start":
            daemon_bool = True
        elif daemon_status.split("\n")[2][((daemon_status.split("\n")[2].find("(")) + 1) : (daemon_status.split("\n")[2].find(")"))] == "stop-sigterm":
            daemon_bool = False
    

        logger.info(msg=f'{daemon_bool}')
    else:
        logger.info(msg=f'{daemon_bool}')

except Exception as e:
    logger.info(f'following exception occured: {e}')
