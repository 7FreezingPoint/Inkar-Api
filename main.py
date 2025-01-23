from quart import Quart, request

from src.utils.generate import (
    ScreenshotGenerator
)
# from src.plugins.jx3.announce import api as announce_api
from src.plugins.jx3.attributes import api as attributes_api
# from src.plugins.jx3.recruit import api as recruit_api
# from src.plugins.jx3.gold import api as gold_api
# from src.plugins.jx3.serendipity import v3 as serendipity_v3_api
# from src.plugins.jx3.trade import api as trade_api
# from src.plugins.jx3.sandbox import api as sandbox_api
# from src.plugins.jx3.pvp import api as pvp_api

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

# # 招募
# @app.route('/recruit', methods=['POST'])
# async def recruit():
#     img = await recruit_api.get_recruit_image(await request.get_json())
#     return img

# # 金价
# @app.route('/gold', methods=['POST'])
# async def gold():
#     img = await gold_api.get_coin_price_image(await request.get_json())
#     return img

# # 奇遇查询
# @app.route('/serendipity', methods=['POST'])
# async def serendipity():
#     img = await serendipity_v3_api.get_serendipity_image_v3(await request.get_json())
#     return img

# # 沙盘
# @app.route('/sandbox', methods=['POST'])
# async def sandbox():
#     img = await sandbox_api.get_sandbox_image(await request.get_json())
#     return img

# # 物价
# @app.route('/trade', methods=['POST'])
# async def trade():
#     img = await trade_api.get_single_item_price(await request.get_json())
#     return img

# # 战绩
# @app.route('/arean/record', methods=['POST'])
# async def arean_record():
#     img = await pvp_api.get_arena_record(await request.get_json())
#     return img

# 在应用关闭时关闭浏览器
@app.after_serving
async def cleanup_browser(exception=None):
    await ScreenshotGenerator.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)