# Seoul Souvenir Guide

首尔伴手礼购买指南的独立静态子项目，放在主仓库 `data/` 下，方便之后整合到主网页。

## 本地打开

直接用浏览器打开：

```bash
open data/seoul-souvenir-guide/index.html
```

也可以用本地静态服务器预览：

```bash
python3 -m http.server 8765 --directory data/seoul-souvenir-guide
```

然后访问 `http://localhost:8765/`。

## 文件结构

```text
data/seoul-souvenir-guide/
  index.html
  style.css
  script.js
  data/
    souvenirs.js
    seoulSouvenirs.json
    routePlans.json
  reports/
    verification-report.md
  screenshots/
```

## 数据说明

- `data/souvenirs.js`: 网页直接读取的数据。
- `data/seoulSouvenirs.json`: 方便后续整合主站的数据副本。
- `data/routePlans.json`: 今日购物路线建议。

图片字段遵循：

- `real`: 真实照片，需要显示来源和授权/平台说明。
- `ai_generated`: AI 生成示意图，页面必须显示 `AI生成示意图 / Not a real photo`。
- `placeholder`: 当前本地示意占位，不是真实照片，也不是 AI 生成位图。

当前商品卡片没有下载未授权品牌/商场图片，也没有把占位图伪装成实拍。
