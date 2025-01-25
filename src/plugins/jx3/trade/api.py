from jinja2 import Template

from src.const.path import ASSETS, TEMPLATES, build_path
from src.utils.network import Request
from src.utils.time import Time
from src.utils.file import read
from src.utils.generate import generate
from src.utils.oss import upload_to_qiniu

from ._template import headers, template_wujia

import datetime
import json

async def query_aijx3_data(url: str, params: dict = {}):
    data = (await Request(url, headers=headers, params=params).post()).json()
    return data

async def get_item_history(standard_name: str) -> tuple[list[int], list[str]]:
    current_timestamp = Time().raw_time
    start_timestamp = current_timestamp - 3*30*24*60*60 # 3个月前
    params = {
        "goodsName":standard_name,
        "belongQf3":"", 
        "endTime": Time(current_timestamp).format("%Y-%m-%d"), 
        "startTime": Time(start_timestamp).format("%Y-%m-%d")
    }
    data = await query_aijx3_data("https://www.aijx3.cn/api/wj/goods/getAvgGoodsPriceRecord", params=params)
    data = data["data"]
    dates = []
    prices = []
    for each_data in data:
        dates.append(
            Time(
                int(
                    datetime.datetime.strptime(
                        each_data["tradeTime"], "%Y-%m-%dT%H:%M:%S.000+0000"
                    ).timestamp()
                )
            ).format(
                "%Y-%m-%d"
                )
            )
        prices.append(each_data["price"])
    return prices[::-1], dates[::-1]

def select_min_max(data: list, margin: float = 0.1, round_to: int = 10) -> tuple[int, int]:
    if not data:
        return 0, 100000
    data = [float(item) for item in data]
    data_min = min(data)
    data_max = max(data)
    data_range = data_max - data_min
    extend = data_range * margin
    optimal_min = data_min - extend
    optimal_max = data_max + extend
    def round_down(value: float, round_to: int) -> float:
        return (value // round_to) * round_to
    def round_up(value: float, round_to: int) -> float:
        return ((value + round_to - 1) // round_to) * round_to
    adjusted_min = round_down(optimal_min, round_to)
    adjusted_max = round_up(optimal_max, round_to)
    return int(adjusted_min), int(adjusted_max)

sales_mapping = {
    1: "出售",
    2: "收购",
    3: "想出",
    4: "想收",
    5: "成交",
    6: "正出",
    7: "公示"
}

async def get_data(data) -> dict:
    full_table = {}
    for index, zone in enumerate(["电信区", "双线区", "无界区", "公示期", "正售中", "服务器"]):
        table = []
        for item in data[index]:
            price = str(item["value"]) + "元"
            table.append(
                Template(template_wujia).render(
                    date=item["date"],
                    server=item["server"],
                    price=price,
                    sales=sales_mapping.get(item["sales"], "未知"),
                )
            )
        full_table[zone] = "\n".join(table)
    return full_table

async def get_single_item_price(data):
    aijx3_data = await get_data(data["data"])

    prices, dates = await get_item_history(data["name"])
    max, min = select_min_max(prices)

    html = Template(read(build_path(TEMPLATES, ["jx3", "item_price.html"]))).render(
        font = build_path(ASSETS, ["font", "PingFangSC-Medium.otf"]),
        item_image = data.get("view", "https://inkar-suki.codethink.cn/Inkar-Suki-Docs/img/Unknown.png"),
        item_name = data["name"],
        item_alias = data["alias"],
        custom_msg = data["desc"],
        server = data["server"],
        aijx3_data = aijx3_data,
        dates = json.dumps(dates, ensure_ascii=False),
        max = max,
        min = min,
        values = json.dumps(prices, ensure_ascii=False)
    )
    final_path = await generate(html, "body", False)
    if not isinstance(final_path, str):
        return
    return upload_to_qiniu(final_path)
    # return Path(final_path).as_uri()