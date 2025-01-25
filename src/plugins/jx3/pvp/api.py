from jinja2 import Template

from src.const.path import ASSETS, build_path
from src.utils.time import Time
from src.utils.oss import upload_to_qiniu
from src.utils.generate import generate
from src.templates import SimpleHTML, get_saohua

from ._template import msg_box, template_arena_record

async def get_arena_record(param):
    msgbox = []
    for mode, data in param["performance"].items():
        if isinstance(data, dict):  # 检查值是否为字典
            input_params = {
                "rank": f"{mode} · " + str(data["grade"]) + "段",
                "count": str(data["totalCount"]),
                "win": str(data["winCount"]),
                "percent": str(round(data["winCount"] / data["totalCount"] * 100, 2)) + "%",
                "score": str(data["mmr"]),
                "best": str(data["mvpCount"]),
                "rank_": data["ranking"]
            }
            msgbox.append(Template(msg_box).render(**input_params))
        else:
            continue

    tables = []
    for i in param["history"]:
        input_params = {
            "kungfu": build_path(ASSETS, ["image", "jx3", "kungfu", i["kungfu"] + ".png"]),
            "rank": str(i["avgGrade"]),
            "mode": str(i["pvpType"]) + "v" + str(i["pvpType"]),
            "time": Time(i["startTime"]).format("%m月%d日 %H:%M:%S"),
            "relate": Time().relate(i["endTime"]),
            "length": "共" + str(i["endTime"] - i["startTime"]) + "秒",
            "score": str(i["totalMmr"]),
            "delta": str(i["mmr"]),
            "color": "green" if i["mmr"] > 0 else "red",
            "status": "WIN" if i["won"] else "LOST"
        }
        if i["mvp"]:
            input_params["status"] = input_params["status"] + "(MVP)"
        tables.append(Template(template_arena_record).render(**input_params))
    final_input = {
        "custom_font": build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
        "msgbox": "\n".join(msgbox),
        "table": "\n".join(tables),
        "server": param["serverName"],
        "name": param["roleName"],
        "saohua": get_saohua()
    }
    html = str(
        SimpleHTML(
            "jx3",
            "arena_record",
            **final_input
        )
    )
    image = await generate(html, ".total")
    return upload_to_qiniu(image)
    # return image