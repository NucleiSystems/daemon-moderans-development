import logging

import uvicorn
import subprocess
from nuclei_backend import app


def ip_addy():
    ip = (
        subprocess.check_output("ipconfig")
        .decode("utf-8")
        .split("IPv4 Address. . . . . . . . . . . : ")[1]
        .split("Subnet Mask")[0]
    )
    return f"\nserver runniyng on : http://{ip.strip()}:8000\n"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.log(1, ip_addy())
    print(ip_addy())
    uvicorn.run(
        "nuclei_backend:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        reload=True,
        use_colors=True,
        ssl_keyfile="./nucleibackend.systems+2-key.pem",
        ssl_certfile="./nucleibackend.systems+2.pem",
    )
