# ICML 2026 Seoul domestic industry events research notes

Checked on 2026-07-02. This file tracks China-related company and talent events around ICML 2026 Seoul. Use the CSV as the source for integration; this note explains confidence.

## Confidence buckets

- `direct_rsvp`: public page gives event time/location/registration details. Safe for main timeline if still relevant.
- `official_program_page_and_media_report`: an official company/talent page exists, but the ICML dinner detail is only from media. Keep in extra attention unless RSVP is found.
- `media_report`: media says the event exists, but no official RSVP/detail page was found. Do not make it a navigable card.
- `wechat_title_only` / `aggregator_title_only`: title or snippet exists, body/details are blocked or not verified. Use as extra attention only.
- `negative_search`: searched and did not find a public event source.

## Main usable event

快手 / Kuaishou is the only domestic big-company event with a public RSVP page found so far.

- Event: 快手 x ICML 2026 晚宴报名 / K-Star STARRY NIGHT
- Time: 2026-07-08 18:00-21:30 KST
- Place: 韩国首尔汝矣岛码头 / Yeouido Dock, Seoul
- Source: https://www.wjx.cn/vm/rN1U64h.aspx
- Caveat: signup deadline was 2026-07-01 24:00 Beijing time; invite-only, successful applicants notified by 2026-07-03.

## Extra attention, not main timeline yet

- 阿里 / Alibaba: media says Alibaba, Kuaishou, and Tencent held ICML Seoul dinners on the same day. No Alibaba RSVP found. The Grand Hyatt 38F location is media-level only.
- 腾讯 / Tencent 青云: official Qingyun page exists, but no ICML dinner RSVP found. Media mentions Tencent leadership attendance, not official event details.
- 华为 / Huawei: subagent found a LinkedIn public clue for "Huawei Talent Night at ICML 2026"; no text time/location found.
- 小米 / Xiaomi: Sogou web exposed the WeChat title "7月首尔见！小米ICML2026顶尖人才技术交流晚宴报名开启"; body is blocked by WeChat verification, so time/location remain unknown.
- 上海 AI Lab: WeChat search snippets confirm two talent events near ICML: 北极星X星启 on 2026-07-08 and 云帆 ICML 2026 AI Talent Meetup on 2026-07-09 16:00-20:30. Exact venue still needs original article/RSVP.
- 将门创投: WeChat snippet confirms 2026-07-08 18:00-21:30 near COEX, approval-required. This is not Huawei-hosted.
- 上海科技大学: Sogou web result shows a 2026-07-09 Seoul talent meetup around ICML; exact venue missing.

## Not found as public ICML Seoul events

No public ICML 2026 Seoul event source found for ByteDance/Seed, MiniMax, Moonshot/Kimi, Xiaohongshu/REDstar, Baidu, or Ant Group during this pass.

Meituan has only a low-confidence aggregator-title clue from the subagent: "首尔有约，ICML 2026 美团AI顶尖人才校招见面会邀请函". Local searches did not recover an official article or RSVP, so keep it out of the formal timeline.

## Source caveats

WeChat article bodies often trigger environment verification from command-line fetches. For those, the CSV records search-result titles/snippets and source URLs, but details should be rechecked manually in WeChat before publishing exact time/location.
