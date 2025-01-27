from pathlib import Path
from jinja2 import Template

from src.const.path import ASSETS, build_path
from src.utils.network import Request
from src.utils.time import Time
from src.utils.generate import generate
from src.utils.oss import upload_to_qiniu
from src.templates import SimpleHTML, get_saohua

from ._template import template_monsters

import re

level_desc = ["", "+800", "秒杀首领;+150", "稀有提高;+200", "随机前进;+150",
              "后六翻倍;+100", "前六减半;+100", "+300", "后跃三步;+200", "+300", "逆向前进"]
level_icon = [18505, 4533, 13548, 13547, 3313, 4577, 4543, 4558, 4576, 4573]

# $Flag 特殊层标识 ; $Icon 图标 ; $Count 层数 ; $bossName 首领名称 ; $Desc 描述 ; $Coin 修罗之印

async def get_monsters_map():
    map_data = (await Request("https://cms.jx3box.com/api/cms/app/monster/map").get()).json()
    boss = (await Request("https://node.jx3box.com/monster/boss").get()).json()
    content = ["<div class=\"u-row\">"]
    for i in range(len(map_data["data"]["data"])):
        bid = map_data["data"]["data"][i]["dwBossID"]
        for x in boss["data"]:
            if x["dwNpcID"] == bid:
                name = x["szName"]
        level = map_data["data"]["data"][i]["nEffectID"]
        info = level_desc[level]
        icon = f"https://icon.jx3box.com/icon/{level_icon[level]}.png"
        flag = " is-effect" if level != 0 else ""  # 勿除空格
        details = info.split(";")
        if len(details) == 2:
            desc = details[0]
            coin = details[1]
        elif len(details) == 1:
            if details[0] == "":
                desc = ""
                coin = ""
            else:
                if details[0][0] == "+":
                    desc = ""
                    coin = details[0]
                else:
                    desc = details[0]
                    coin = ""
        else:
            desc = ""
            coin = ""
        count = i + 1
        if count % 10 == 0:
            flag = flag + " is-elite"  # 勿除空格
        new = Template(template_monsters).render(
            flag = flag,
            icon = icon,
            count = str(count),
            name = name,
            desc = desc,
            coin = coin
        )
        if count % 10 == 0:
            content.append(new)
            if count / 10 in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                content.append("</div>\n<div class=\"u-row\">")
            elif count / 10 == 10:
                content.append("</div>")
        else:
            content.append(new)
    start = re.sub(r"\..+\Z", "", map_data["data"]["start"].replace("T", " ")).split(" ")[0]
    current_time = Time().format("%H:%M:%S")
    msg = get_saohua()
    html = str(
        SimpleHTML(
            "jx3",
            "monsters.html",
            font = build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
            table_content = "\n".join(content),
            application_name = f"自{start}起7天 · 当前时间：{current_time}<br>{msg}"
        )
    )
    image = await generate(html, ".m-bmap.is-map-phone")
    return upload_to_qiniu(image)