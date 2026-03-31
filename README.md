# nonebot-plugin-doubao-draw

基于豆包 Seedream API 的 NoneBot2 AI 绘图插件，支持文生图和以图生图。

## 功能特性

- 文生图：根据提示词生成图片
- 以图生图：基于参考图片生成新图
- 多图参考：支持最多 9 张参考图片
- 引用图片：回复图片消息即可使用该图片作为参考
- Token 统计：显示每次生成的 token 消耗和费用
- 群组控制：支持配置只在指定群启用

## 安装

### 使用 nb-cli 安装

```bash
nb plugin install nonebot-plugin-doubao-draw
```

### 使用 pip 安装

```bash
pip install nonebot-plugin-doubao-draw
```

## 配置

在 NoneBot2 项目的 `.env` 文件中添加以下配置：

```env
DOUBAO_DRAW_API_KEY=your_api_key_here
DOUBAO_DRAW_ENABLED=true
DOUBAO_DRAW_SIZE=2K
DOUBAO_DRAW_GROUPS=[]
```

### 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| DOUBAO_DRAW_API_KEY | str | "" | 豆包 API 密钥（必填） |
| DOUBAO_DRAW_ENABLED | bool | true | 是否启用插件 |
| DOUBAO_DRAW_SIZE | str | "2K" | 图片尺寸 |
| DOUBAO_DRAW_GROUPS | list[int] | [] | 启用的群号列表，为空表示所有群启用 |

## 使用方法

### 文生图

```
/绘图 一只可爱的猫咪
```

### 以图生图（附图）

发送命令时附带图片：

```
/绘图 将这张图片变成油画风格 [附图]
```

支持同时附带多张图片（最多 9 张）。

### 以图生图（引用）

回复一张图片消息：

```
/绘图 将这张图片变成水彩画风格
```

### 查看帮助

```
/绘图帮助
```

## 获取 API Key

1. 访问 [火山引擎方舟](https://console.volcengine.com/ark)
2. 注册并登录账号
3. 开通 Seedream 模型服务
4. 获取 API Key

## 支持的模型

| 模型 | 输入价格 | 输出价格 |
|------|----------|----------|
| doubao-seedream-5-0-260128 | ¥0.008/千tokens | ¥0.08/千tokens |
| doubao-seedream-4-5-251128 | ¥0.015/千tokens | ¥0.15/千tokens |
| doubao-seedream-4-0-250828 | ¥0.008/千tokens | ¥0.08/千tokens |

## 注意事项

- 确保已正确配置 API Key
- 图片生成需要一定时间，请耐心等待
- 生成的图片通过 Base64 编码直接发送，无需额外存储

## 许可证

MIT License
