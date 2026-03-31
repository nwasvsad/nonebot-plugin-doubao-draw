import base64
from openai import OpenAI
from nonebot.log import logger

BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL = "doubao-seedream-4-5-251128"

MODEL_PRICE = {
    "doubao-seedream-5-0-260128": {"input": 0.008, "output": 0.08},
    "doubao-seedream-4-5-251128": {"input": 0.015, "output": 0.15},
    "doubao-seedream-4-0-250828": {"input": 0.008, "output": 0.08},
}

class DrawResult:
    def __init__(self, img_data: bytes, usage: dict):
        self.img_data = img_data
        self.usage = usage
        self.generated_images = usage.get("generated_images", 0)
        self.output_tokens = usage.get("output_tokens", 0)

    def get_cost(self, model: str) -> float:
        price = MODEL_PRICE.get(model, {}).get("output", 0.15)
        return (self.output_tokens / 1000) * price

class DoubaoDrawService:
    def __init__(self, api_key: str, size: str = "2K"):
        self.client = OpenAI(base_url=BASE_URL, api_key=api_key)
        self.size = size

    async def generate_image(self, prompt: str, watermark: bool = False) -> DrawResult:
        logger.info(f"[DoubaoDraw] 正在生成图片，提示词: {prompt}")

        response = self.client.images.generate(
            model=MODEL,
            prompt=prompt,
            size=self.size,
            response_format="b64_json",
            extra_body={"watermark": watermark}
        )

        if response.data and len(response.data) > 0:
            b64 = response.data[0].b64_json
            img_data = base64.b64decode(b64)
            usage = {
                "generated_images": getattr(response, "usage", {}).get("generated_images", 1),
                "output_tokens": getattr(response, "usage", {}).get("output_tokens", 0),
            }
            logger.info(f"[DoubaoDraw] 图片生成成功，大小: {len(img_data)} bytes, tokens: {usage}")
            return DrawResult(img_data, usage)
        else:
            logger.error("[DoubaoDraw] 图片生成失败: 未返回数据")
            raise Exception("图片生成失败")

    async def generate_image_with_ref(
        self,
        prompt: str,
        ref_images: list[str],
        watermark: bool = False
    ) -> DrawResult:
        logger.info(f"[DoubaoDraw] 正在以图生图，提示词: {prompt}, 参考图数量: {len(ref_images)}")

        response = self.client.images.generate(
            model=MODEL,
            prompt=prompt,
            size=self.size,
            response_format="b64_json",
            extra_body={
                "watermark": watermark,
                "image": ref_images if len(ref_images) > 1 else ref_images[0]
            }
        )

        if response.data and len(response.data) > 0:
            b64 = response.data[0].b64_json
            img_data = base64.b64decode(b64)
            usage = {
                "generated_images": getattr(response, "usage", {}).get("generated_images", 1),
                "output_tokens": getattr(response, "usage", {}).get("output_tokens", 0),
            }
            logger.info(f"[DoubaoDraw] 以图生图成功，大小: {len(img_data)} bytes, tokens: {usage}")
            return DrawResult(img_data, usage)
        else:
            logger.error("[DoubaoDraw] 以图生图失败: 未返回数据")
            raise Exception("以图生图失败")
