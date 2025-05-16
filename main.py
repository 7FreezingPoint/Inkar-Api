from quart import Quart, request

from src.utils.generate import (
    ScreenshotGenerator
)
# from src.plugins.jx3.announce import api as announce_api
from src.plugins.jx3.attributes import api as attributes_api
from src.plugins.jx3.detail import detail as detail_api
from src.plugins.jx3.trade import api as trade_api
from src.plugins.jx3.recruit import api as recruit_api
from src.plugins.jx3.pvp import api as pvp_api
from src.plugins.jx3.horse import api as horse_api
from src.plugins.jx3.serendipity import v1 as serendipity_v1_api
from src.plugins.jx3.serendipity import v3 as serendipity_v3_api
from src.plugins.jx3.dungeon import monster as dungeon_monster_api
from src.plugins.jx3.dungeon import role_monster as dungeon_role_monster_api
from src.plugins.jx3.gold import api as gold_api
from src.plugins.jx3.sandbox import api as sandbox_api
from src.plugins.jx3.joy.random_loot import RandomLoot
from src.plugins.jx3.joy import random_shilian as random_shilian_api

app = Quart(__name__)

# 在应用启动时启动浏览器
@app.before_serving
async def initialize_browser():
    await ScreenshotGenerator.launch()


# # 公告
# @app.route('/announce', methods=['POST'])
# async def announce():
#     img = await announce_api.get_image()
#     return img

# 属性
@app.route('/attributes', methods=['POST'])
async def attributes():
    img = await attributes_api.get_attr_v2_remake(await request.get_json())
    return img

# 物价
@app.route('/trade', methods=['POST'])
async def trade():
    img = await trade_api.get_single_item_price(await request.get_json())
    return img

# 招募
@app.route('/recruit', methods=['POST'])
async def recruit():
    img = await recruit_api.get_recruit_image(await request.get_json())
    return img

# 战绩
@app.route('/arean/record', methods=['POST'])
async def arean_record():
    img = await pvp_api.get_arena_record(await request.get_json())
    return img

# 马场
@app.route('/horse', methods=['POST'])
async def horse():
    img = await horse_api.get_horse_next_spawn(await request.get_json())
    return img

# 奇遇攻略
@app.route('/preposition', methods=['POST'])
async def preposition():
    data = await request.get_json()
    img = await serendipity_v1_api.get_preposition(data["name"])
    return img

# 奇遇查询
@app.route('/serendipity', methods=['POST'])
async def serendipity():
    img = await serendipity_v3_api.get_serendipity_image_v3(await request.get_json())
    return img

# 百战
@app.route('/monster', methods=['POST'])
async def monster():
    img = await dungeon_monster_api.get_monsters_map()
    return img

# 精耐
@app.route('/role/monster', methods=['POST'])
async def role_monster():
    img = await dungeon_role_monster_api.get_role_monsters_map(await request.get_json())
    return img

# 资历分布
@app.route('/detail', methods=['POST'])
async def detail():
    img = await detail_api.get_exp_info(await request.get_json())
    return img

# 金价
@app.route('/gold', methods=['POST'])
async def gold():
    img = await gold_api.get_coin_price_image(await request.get_json())
    return img

# 沙盘
@app.route('/sandbox', methods=['POST'])
async def sandbox():
    img = await sandbox_api.get_sandbox_image(await request.get_json())
    return img

# 模拟掉落
@app.route('/random/loot', methods=['POST'])
async def random_loot():
    data = await request.get_json()
    instance = await RandomLoot.with_map_name(data["mapName"], data["mode"])
    if instance is None:
        return "副本名称或难度输入错误"
    return await instance.generate()

# 模拟试炼
@app.route('/random/shilian', methods=['POST'])
async def random_shilian():
    data = await request.get_json()
    return await random_shilian_api.generate_shilian_box(data["level"], data["chose"])

# 在应用关闭时关闭浏览器
@app.after_serving
async def cleanup_browser(exception=None):
    await ScreenshotGenerator.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)