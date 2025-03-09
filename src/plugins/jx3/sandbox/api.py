from src.const.path import ASSETS, TEMPLATES, build_path
from src.utils.file import read
from src.utils.time import Time
from src.utils.generate import generate
from src.utils.oss import upload_to_qiniu

async def get_sandbox_image(data):
    html = read(build_path(TEMPLATES, ["jx3", "sandbox.html"]))
    update_time = str(Time(data["update"]).format())
    html = html.replace("$time", update_time)
    html = html.replace("$server", data["server"])
    html = html.replace("$customfont", build_path(ASSETS, ["font", "PingFangSC-Semibold.otf"]))
    html = html.replace("$css", build_path(TEMPLATES, ["jx3", "sandbox.css"]))
    for i in data["data"]:
        camp = "haoqi" if i["campName"] == "浩气盟" else "eren"
        html = html.replace("$" + i["castleName"], camp)
    image = await generate(html, ".m-sandbox-map")
    return upload_to_qiniu(image)