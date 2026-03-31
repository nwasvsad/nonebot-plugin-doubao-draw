from nonebot import on_command, get_driver, logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
import io

from .config import Config
from .service import DoubaoDrawService, MODEL

__plugin_meta__ = PluginMetadata(
    name="豆包AI绘图",
    description="基于豆包Seedream API的AI绘图插件，支持文生图和以图生图",
    usage="发送 /绘图 <提示词> 即可生成图片\n"
          "/绘图 <提示词> 并附上图片可进行以图生图（支持多张图片）\n"
          "/绘图 <提示词> 并引用图片消息可基于引用图片生成\n"
          "/绘图帮助 查看帮助信息",
    type="application",
    homepage="https://github.com/nwasvsad/nonebot-plugin-doubao-draw",
    config=Config,
    supported_adapters={"~onebot.v11"},
    tags=["ai", "draw", "image", "doubao"],
)

HELP_TEXT = """【豆包AI绘图插件帮助】

可用指令：
1. /绘图 <提示词>
   - 根据提示词生成图片
   - 示例：/绘图 一只可爱的猫咪

2. /绘图 <提示词> + 附图
   - 以图生图，支持多张参考图
   - 发送命令时附带1-9张图片

3. /绘图 <提示词> + 引用图片
   - 基于引用的图片生成新图
   - 回复一张图片消息，发送命令

4. /绘图帮助
   - 显示本帮助信息

配置项：
- DOUBAO_DRAW_API_KEY: 豆包API密钥
- DOUBAO_DRAW_ENABLED: 是否启用插件
- DOUBAO_DRAW_SIZE: 图片尺寸(默认2K)
- DOUBAO_DRAW_GROUPS: 启用的群号列表"""

driver = get_driver()
_plugin_config = None

def get_plugin_config() -> Config:
    global _plugin_config
    if _plugin_config is None:
        _plugin_config = Config.parse_obj(dict(driver.config))
    return _plugin_config

def get_draw_service() -> DoubaoDrawService:
    cfg = get_plugin_config()
    return DoubaoDrawService(
        api_key=cfg.doubao_draw_api_key,
        size=cfg.doubao_draw_size
    )

def is_draw_enabled_for_group(group_id: int) -> bool:
    cfg = get_plugin_config()
    if not cfg.doubao_draw_enabled:
        return False
    if not cfg.doubao_draw_groups:
        return True
    return group_id in cfg.doubao_draw_groups

def get_all_attached_images(event: GroupMessageEvent) -> list:
    images = []
    for seg in event.message:
        if seg.type == "image":
            url = seg.data.get("url", "")
            if url:
                images.append(url)
    return images

def get_all_reply_images(event: GroupMessageEvent) -> list:
    images = []
    if hasattr(event, 'reply') and event.reply:
        reply_msg = event.reply
        if hasattr(reply_msg, 'message'):
            for seg in reply_msg.message:
                if seg.type == "image":
                    url = seg.data.get("url", "")
                    if url:
                        images.append(url)
    return images

def format_cost(cost: float) -> str:
    if cost < 0.01:
        return f"¥{cost*100:.2f}分"
    return f"¥{cost:.4f}"

draw_cmd = on_command("绘图", priority=5, block=True)
help_cmd = on_command("绘图帮助", priority=5, block=True)

@help_cmd.handle()
async def handle_help(event: GroupMessageEvent):
    group_id = event.group_id
    if not is_draw_enabled_for_group(group_id):
        await help_cmd.finish()
    await help_cmd.finish(HELP_TEXT)

@draw_cmd.handle()
async def handle_draw(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    group_id = event.group_id
    user_id = event.user_id

    if not is_draw_enabled_for_group(group_id):
        await draw_cmd.finish()

    prompt = args.extract_plain_text().strip()
    if not prompt:
        await draw_cmd.finish()

    cfg = get_plugin_config()
    if not cfg.doubao_draw_api_key:
        await draw_cmd.finish("绘图服务未配置API Key")

    attached_images = get_all_attached_images(event)
    reply_images = get_all_reply_images(event)
    all_images = attached_images + reply_images

    at_user = MessageSegment.at(user_id)

    if all_images:
        await draw_cmd.send("正在以图生图，参考 {} 张图片，请稍候...".format(len(all_images)))
        try:
            service = get_draw_service()
            result = await service.generate_image_with_ref(prompt, all_images)
            img_bytes = io.BytesIO(result.img_data)
            cost = result.get_cost(MODEL)
            msg = Message(at_user) + MessageSegment.image(img_bytes) + "\n消耗: {} tokens, 约 {}".format(result.output_tokens, format_cost(cost))
            await bot.send(event=event, message=msg)
            logger.info(f"[DoubaoDraw] 以图生图成功，群:{group_id}, 用户:{user_id}, 提示词:{prompt}, 参考图:{len(all_images)}张, tokens:{result.output_tokens}, 费用:{cost}")
        except Exception as e:
            logger.error(f"[DoubaoDraw] 以图生图失败: {e}")
            await bot.send(event=event, message=Message(at_user) + f"以图生图失败: {e}")
    else:
        await draw_cmd.send("正在生成图片，请稍候...")
        try:
            service = get_draw_service()
            result = await service.generate_image(prompt)
            img_bytes = io.BytesIO(result.img_data)
            cost = result.get_cost(MODEL)
            msg = Message(at_user) + MessageSegment.image(img_bytes) + "\n消耗: {} tokens, 约 {}".format(result.output_tokens, format_cost(cost))
            await bot.send(event=event, message=msg)
            logger.info(f"[DoubaoDraw] 图片发送成功，群:{group_id}, 用户:{user_id}, 提示词:{prompt}, tokens:{result.output_tokens}, 费用:{cost}")
        except Exception as e:
            logger.error(f"[DoubaoDraw] 生成失败: {e}")
            await bot.send(event=event, message=Message(at_user) + f"图片生成失败: {e}")
