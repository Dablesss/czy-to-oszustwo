# Renderuje plik HTML do PNG przez headless Chrome: python render.py <plik.html> <wyjscie.png> <szer> <wys>
import base64, json, pathlib, subprocess, sys, tempfile, time, urllib.request
import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def render(jobs):
    p = subprocess.Popen([CHROME, "--headless=new", "--remote-debugging-port=9338", f"--user-data-dir={tempfile.mkdtemp()}",
                          "--hide-scrollbars", "--allow-file-access-from-files", "about:blank"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try:
            pg = [t for t in json.load(urllib.request.urlopen("http://127.0.0.1:9338/json/list")) if t["type"] == "page"][0]
            break
        except Exception:
            time.sleep(0.2)
    ws = websocket.create_connection(pg["webSocketDebuggerUrl"], suppress_origin=True)
    n = 0

    def cdp(m, **kw):
        nonlocal n
        n += 1
        ws.send(json.dumps({"id": n, "method": m, "params": kw}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == n:
                return r.get("result", {})

    for src, out, w, h in jobs:
        cdp("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)
        cdp("Page.navigate", url=pathlib.Path(src).resolve().as_uri())
        time.sleep(1.0)
        data = cdp("Page.captureScreenshot", format="png", clip={"x": 0, "y": 0, "width": w, "height": h, "scale": 1})["data"]
        pathlib.Path(out).write_bytes(base64.b64decode(data))
        print("ok", out)
    ws.close()
    p.terminate()


if __name__ == "__main__":
    render([(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))])
