import sys, subprocess, logging
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s[%(name)s] %(message)s")
log = logging.getLogger(__name__ == "__main__" and "MainScript" or __name__)
def install(pkg):
    log.info("Installing {}.format(pkg) from pypi")
    return subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])
