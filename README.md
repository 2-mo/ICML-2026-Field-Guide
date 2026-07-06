# ICML 2026 Field Guide / 逛会指南

一个面向 ICML 2026 Seoul / COEX 的移动端逛会指南。目标不是替代 ICML 官方 app，而是把现场最容易卡住行动的信息整理成一个能快速打开的静态网页：当天路线、poster 主题密度、晚间活动、交通、COEX 周边补给和景点。

## 在线发布

本项目的 GitHub Pages 首页是：

- `docs/index.html`

推荐 GitHub Pages 设置：

- Source：Deploy from a branch
- Branch：`main`
- Folder：`/docs`

本地预览：

```bash
python3 -m http.server 8000 -d docs
```

然后打开：

```text
http://localhost:8000
```

`docs/` 是发布到 GitHub Pages 所需的静态站点目录；`data/` 和 `scripts/` 是数据处理与复跑来源；`output/xiaohongshu_v3/final/` 是小红书宣传图成品。

## License / 授权

本仓库内容采用 [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)（CC BY 4.0）授权，除非文件内另有说明。

This repository is licensed under CC BY 4.0 unless otherwise noted.

本项目不是 ICML 官方项目；会议日程、论文、地图、交通和活动信息可能变化，正式出行和参会前请以 ICML 官方网站、官方 app、RSVP 页面和现场公告为准。

## 项目定位

本目录目前先整理官方数据源和可复跑脚本，后续在此基础上生成主题路线和逛会指南。

## 官方主数据源

- 日程页：https://icml.cc/virtual/2026/calendar
- Papers 页：https://icml.cc/virtual/2026/papers.html
- 官方静态 JSON：https://icml.cc/static/virtual/data/icml-2026-orals-posters.json
- 官方摘要 JSON：https://icml.cc/static/virtual/data/icml-2026-abstracts.json

主表优先使用官方静态 JSON；HTML 解析脚本保留作校验和兜底。

## 关键输出

- `docs/index.html`
  - GitHub Pages 静态网页入口。
  - 移动端优先的逛会控制台，首页主入口为 Timeline、Events、Travel；Papers、Schedule、Search 作为按需深挖视图保留。

- `docs/data/*.json`
  - 网页使用的轻量 JSON 数据包，由 `scripts/build_web_data.py` 从 `data/processed/*.csv` 生成。
  - 首页和导航使用 `manifest.json`、`focus.json`、`schedule.json`、`events.json`、`travel.json` 等轻量包。
  - 每日路线从 `docs/data/guide_plans/*.json` 按日期加载；明星作者论文从 `docs/data/star_papers/*.json` 按需加载。
  - `papers.json` 和 `search.json` 用于深挖检索；外部活动只作为 RSVP 线索。

- `docs/maps/icml2026_seoul_maplibre.html`
  - GitHub Pages 版 MapLibre 交互地图资源，从 `data/maps/` 复制生成。

- `data/processed/icml2026_papers_master.csv`
  - 官方 JSON 主表，6628 篇 poster 论文。
  - 包含作者、机构、摘要、OpenReview 链接、官方 poster 链接、KST 时间、poster/oral 关联、spotlight/position/journal 标签。

- `data/processed/icml2026_papers_tagged.csv`
  - 在 master 表基础上加入主题多标签和 `attention_bucket`。
  - `attention_bucket=现场可逛`：当前官方现场日程中有 poster 排期。
  - `attention_bucket=额外关注（未进入当前现场日程）`：已接收但当前不在现场 poster/oral 日程里，后续放入补读/远程关注。

- `data/processed/icml2026_topic_session_summary.csv`
  - 按主题 x poster session 聚合的现场路线密度表。

- `data/processed/icml2026_extra_attention.csv`
  - 753 篇额外关注论文清单。

- `data/processed/icml2026_extra_attention_topic_summary.csv`
  - 额外关注论文的主题统计。

- `data/processed/icml2026_side_events.csv`
  - ICML week 公开 side events / 晚宴 / happy hour / meetup 清单。
  - 主来源为 Team Attention 的 Luma hub，含 46 个活动；网页构建时会额外合入手动核验的 Kuaishou / Qwen 公开 RSVP 页。

- `data/processed/icml2026_side_events_summary.csv`
  - 侧活动按类型统计。

- `data/processed/icml2026_map_places.csv`
  - COEX、酒店、机场、地铁站、side-event 常用区域的 Google Maps 原始查询链接。
  - Luma 只公开到区域级的活动地点标为 `luma_detail_obfuscated_area`，不要当作最终会场地址。

- `data/processed/icml2026_route_links.csv`
  - 15 条可直接打开的 Google Maps directions 链接，覆盖机场到 COEX、COEX 到常用 side-event 区域、COEX 到重点公开活动区域。

- `data/processed/icml2026_transport.csv`
  - 会场交通建议表，附 COEX/CALT/IHG/VisitKorea/Pangyo 官方来源和对应 Google Maps 路径规划链接。

- `data/processed/icml2026_nearby_picks.csv`
  - COEX 周边、Gangnam、Seongsu、Hongdae、Itaewon 等逛会间隙/晚间备选点位。

- `data/processed/icml2026_google_maps_screenshot_targets.csv`
  - 建议截图的关键 Google Maps 路线列表和本地 PNG 文件名。

- `data/processed/icml2026_google_maps_screenshots.csv`
  - 当前已生成截图的 manifest；截图文件在 `data/maps/screenshots/`。

- `data/maps/icml2026_seoul_maplibre.html`
  - MapLibre GL JS 交互地图，底图使用 CARTO/OSM，路线和点位来自本仓库生成的 GeoJSON。
  - 页面文字以中文和英文为主，韩文只作为括号注释。

- `data/maps/icml2026_seoul_maplibre.png`
  - MapLibre 交互地图的静态截图，可用于内部预览。

- `data/maps/icml2026_seoul_schematic.svg`
  - 代码绘制的离线交通示意图，不依赖地图瓦片，适合放进最终指南后再微调排版。

- `data/processed/icml2026_visual_map_points.csv`
  - MapLibre/SVG 共用点位表，含中英韩括注、坐标、Google Maps 链接。

- `data/processed/icml2026_visual_map_routes.csv`
  - MapLibre/SVG 共用路线表，含路线类型、颜色、点序列、Google Maps directions 链接。

- `data/processed/icml2026_practical_info.csv`
  - 逛会实用信息主表，43 条。
  - 覆盖 registration / badge、Help Desk、First Aid、行李寄存、accessibility、poster 作者事项、Wi-Fi 风险、官方 app、签证/酒店/childcare 等。

- `data/processed/icml2026_pretrip_checklist.csv`
  - 行前和每日 checklist，14 条。
  - 用于生成指南首页的 P0/P1 操作清单。

- `data/processed/icml2026_collection_backlog.csv`
  - 还需要会前/现场刷新确认的信息，9 条。
  - 包括 Wi-Fi SSID、booth map、Luma guests-only 精确地址、打印/药店营业时间、天气每日刷新等。

- `data/processed/icml2026_local_essentials.csv`
  - COEX 5 分钟内、机场落地、晚饭/雨天备选的补给表，18 条。
  - 文字以中文和英文为主，韩文只作为括号或 `korean_note` 注释。

- `data/processed/icml2026_onsite_opportunities.csv`
  - 会场内机会表，25 条。
  - 覆盖 ICML Careers、Sponsor/Expo、官方 mentorship / affinity / social / reception，以及招聘线索。

## 当前计数

- 论文总数：6628
- 当前现场 poster session 可逛：5875
- 额外关注：753
- Oral：168
- Spotlight：574
- Position papers：213
- Journal track：74
- Side events：48
  - Dinner：7
  - Evening social：16
  - Cafe / coworking：3
  - Meetup / networking：9
- Practical info：43
- Local essentials：18
- On-site opportunities：25

## 复跑命令

```bash
python3 scripts/parse_icml2026_json.py
python3 scripts/tag_icml2026_topics.py
python3 scripts/summarize_icml2026.py
python3 scripts/extract_extra_attention.py
python3 scripts/parse_icml_side_events.py
python3 scripts/build_icml2026_maps.py
python3 scripts/build_icml2026_visual_maps.py --render
python3 scripts/capture_google_maps_screenshots.py --existing-only
python3 scripts/build_icml2026_practical_info.py
python3 scripts/build_web_data.py
```

## 网页定位

网页定位是“临场攻略层”，不是官方 app 的替代品。官方 app/virtual site 负责完整日程和论文详情；本页优先回答：

1. 现在或接下来先去哪
2. 哪些信息会卡住现场行动
3. 哪些活动/路线出发前必须重新确认
4. 地图、补给、论文路线的快速入口

## 时间说明

官方 JSON 的时间字段带 `-07:00` offset。脚本统一转换为 `Asia/Seoul` / KST，输出字段后缀为 `_kst`。

## Side Events 说明

侧活动信息变化快，不应视为 ICML 官方日程。当前清单来自公开 RSVP 页面：

- Team Attention Luma hub：https://luma.com/7iiqamt2
- Hub 标注更新时间：June 30, 2026 8:20pm KST

参加前应打开 `rsvp_url` 再确认报名状态、地点和入场要求。

## 实用信息说明

实用信息优先使用官方来源：

- ICML At the Conference：https://icml.cc/Conferences/2026/AtTheConference
- ICML Poster Instructions：https://icml.cc/Conferences/2026/PosterInstructions
- ICML virtual schedule：https://icml.cc/virtual/2026/calendar
- ICML sponsor list：https://icml.cc/virtual/2026/sponsor_list
- ICML careers：https://icml.cc/careers/
- COEX floor plan：https://www.coexcenter.com/facilities-floor-plan/
- COEX airport directions：https://www.coexcenter.com/directions-map-airport-2/
- VisitKorea transportation cards：https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=140663
- VisitKorea emergency numbers：https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=140042

会场内机会建议按以下顺序放进逛会指南：

1. ICML Careers 登录和 sponsor/exhibitor 信息
2. Jul 6 Expo talks / demos / workshops
3. 官方 reception / mentorship / affinity / social
4. 外部 Luma side events 和厂商晚宴

周边补给不要写成“景点推荐优先”，而是分成：

1. `会场 5 分钟内`：Starfield COEX Mall、Parnas Mall、地下动线、便利店、药店、打印、ATM
2. `机场落地先办`：SIM/eSIM/Wi-Fi、现金、交通卡、6103 机场巴士
3. `晚饭/雨天备选`：Gangnam / Sinnonhyeon 餐饮区、Gangnam Station Underground Shopping Center

天气和交通营业时间变化快；正式发布前应刷新 `icml2026_collection_backlog.csv` 中标为 `needs_recheck` / `daily_refresh` 的项目。

## 地图与交通说明

Google Maps 链接使用官方 Maps URLs 格式：`https://www.google.com/maps/search/?api=1` 和 `https://www.google.com/maps/dir/?api=1`。这些链接会在打开时使用 Google Maps 实时数据；本仓库不固化实时通勤时长，也不把第三方估算写死。

COEX 官方建议的会场入口：

- Line 2：Samseong Station exits 5/6
- Line 9：Bongeunsa Station exit 7
- Line 7：Cheongdam Station 可步行但距离更远

重点注意：部分 Luma 活动页公开 JSON 会给坐标，但页面同时标记 `geo_address_visibility=guests-only` / `mode=obfuscated`。这类活动在地图表里只作为区域级路线预估，报名通过后应替换成 RSVP 页面展示的精确地址。

正式指南建议使用 MapLibre / SVG 图，而不是 Google Maps 截图：

- `data/maps/icml2026_seoul_maplibre.html`：主交互地图。
- `data/maps/icml2026_seoul_maplibre.png`：交互地图截图。
- `data/maps/icml2026_seoul_schematic.svg`：可离线编辑的示意图。
- `data/maps/icml2026_seoul_schematic.png`：示意图截图。

Google Maps 截图只作为路线核验备份，不建议直接放入正式稿：

- `data/maps/screenshots/01-icn-t1-to-coex.png`
- `data/maps/screenshots/02-gimpo-airport-to-coex.png`
- `data/maps/screenshots/03-coex-to-gangnam-station.png`
- `data/maps/screenshots/04-coex-to-openai-codex-meetup.png`

`scripts/capture_google_maps_screenshots.py` 可尝试刷新截图；Google Maps headless 渲染偶尔会超时，脚本会把可用/缺失状态写入 manifest。



## 参考文案


VALSE 2026 逛会攻略来啦！📌✨
按我比较关注的方向整理了一版「必听 + 备选」路线，希望能帮大家少纠结、多听会、不迷路～🗺️
我主要研究方向为[^视频异常理解]，也非常期待这次在 VALSE 和大家见面交流！如果你也在现场，欢迎来找我聊天、交换想法、约饭约咖啡奶茶 ☕️🧋
想拍照也可以找我！📸 相机已预备，一起拍点有趣的参会日常～
#VALSE2026 #VALSE #武汉 #学术会议 #逛会攻略 #计算机视觉 #视频理解 #视频异常理解 #多模态大模型 #智能体 #具身智能 #可信AI #视觉智能 #会议摄影
