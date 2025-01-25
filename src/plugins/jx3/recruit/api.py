from jinja2 import Template

from src.utils.time import Time
from src.utils.generate import generate
from src.utils.oss import upload_to_qiniu
from src.templates import HTMLSourceCode

from ._template import template_interserver, table_recruit_head

async def check_ad(msg: str, data: dict) -> bool:
    data = data["data"]
    for x in data:
        status = []
        for num in range(len(x)):
            status.append(True)
        result = []
        for y in x:
            if msg.find(y) != -1:
                result.append(True)
            else:
                result.append(False)
        if status == result:
            return True
    return False

async def get_recruit_image(data):
    time_now = Time(data["time"]).format("%H:%M:%S")
    server = data["server"]
    data = data["data"]
    contents = []
    for i in range(len(data)):
        detail = data[i]
        content = detail["content"]
        flag = "" if not detail["roomID"] else "<div style=\"padding: 5px 10px; background: blue; border-radius: 30%; color: #fff \">跨</div>"
        num = str(i + 1)
        name = detail["activity"]
        level = str(detail["level"])
        leader = detail["leader"]
        count = str(detail["number"]) + "/" + str(detail["maxNumber"])
        create_time = Time(detail["createTime"]).format()
        template = template_interserver
        contents.append(
            Template(template).render(
                sort = num,
                name = name,
                level = level,
                leader = leader,
                count = count,
                content = content,
                time = create_time,
                flag = flag
            )
        )
        if len(contents) == 50:
            break
    html = str(
        HTMLSourceCode(
            application_name = f" · {server} · 团队招募 · {time_now}",
            table_head = table_recruit_head,
            table_body = "\n".join(contents)
        )
    )
    image = await generate(html, "table")
    return upload_to_qiniu(image)