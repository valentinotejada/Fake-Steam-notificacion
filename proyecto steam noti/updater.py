import urllib.request
import json


VERSION_ACTUAL = "1.0.0"

GITHUB_OWNER = "TU_USUARIO"
GITHUB_REPO = "TU_REPOSITORIO"


def comprobar_actualizacion():

    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    )

    try:

        respuesta = urllib.request.urlopen(url, timeout=5)

        datos = json.loads(respuesta.read().decode("utf-8"))

        ultima_version = datos["tag_name"]

        ultima_version = ultima_version.replace("v", "")

        if ultima_version != VERSION_ACTUAL:
            return ultima_version

        return None

    except Exception:

        return None