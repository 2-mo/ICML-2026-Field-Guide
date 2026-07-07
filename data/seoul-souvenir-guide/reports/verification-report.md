# Seoul Souvenir Guide Verification Report

Generated on 2026-07-07.

## Summary

- Status: `needs_review`
- Reason: the webpage and structured data are complete enough for local review and later integration, but item-level bitmap images are currently `placeholder`, not real photos or gpt-image-2 outputs. This avoids copyright and AI-photo confusion, but the original full spec asked for real images where safe or AI generated illustrative images otherwise.
- Data count: 24 souvenir entries.
- Route count: 6 route suggestions.

## Verified

- Each souvenir entry has:
  - `id`
  - category fields
  - Chinese, English, and Korean product names
  - brand/store
  - recommendation reason
  - best-for audience
  - `price_range_krw` with either a range or `待确认`
  - shop name
  - English and Korean address
  - nearest station
  - opening hours or explicit confirmation note
  - source URLs
  - carry/gift/uniqueness scores
  - caution note
  - bring-home suitability note
  - image type and image credit
- Every recommendation is tied to a specific store, mall, or airport location, not just a brand.
- AI/placeholder visuals are visibly marked in the UI and data.
- No item recommends fresh, chilled, meat, seafood, or liquid-heavy goods without a caution note.
- The page includes:
  - search
  - category filter
  - price filter
  - carry-friendliness filter
  - cards
  - detail modal
  - copy-address controls
  - Naver/Kakao/Google map links
  - route suggestions
  - source links

## Needs Review

- Item images: `24` item cards currently use `image_type: "placeholder"`. They should be replaced later by either:
  - safe real photos with source/credit, or
  - gpt-image-2 generated illustrative images marked `image_type: "ai_generated"` and visibly labeled `AI生成示意图 / Not a real photo`.
- Price fields: many entries use `待确认` because official Korean won prices were not consistently available without relying on volatile product pages or unofficial blogs.
- Opening hours: fields marked `待确认` or containing a verification note should be checked again on the travel date.
- Store inventory: brand/store pages confirm locations, but exact item availability should be checked in-store or on the official store page before visiting.

## Removed / Avoided

- Fresh rice cakes and short shelf-life refrigerated foods were not included as standalone recommendations.
- Unclear copyright product images from brand, department store, and IP-character sites were not downloaded.
- Unverified blog-only claims were not used as sole support for address or opening-hour fields.

## Representative Sources

- Visit Seoul: https://english.visitseoul.net/
- Visit Korea: https://english.visitkorea.or.kr/
- Seoul Metropolitan Government Seoul My Soul Shop: https://english.seoul.go.kr/service/amusement/seoul-my-soul-shop/
- Incheon Airport shopping directory: https://www.airport.kr/ap_en/1531/subview.do
- Olive Young Myeongdong Global Town: https://myeongdongtown.oliveyoung.com/
- The Hyundai Seoul: https://www.ehyundai.com/
- TAMBURINS stores: https://www.tamburins.com/en/store/korea/
- National Museum Foundation of Korea museum shop: https://www.nmf.or.kr/enguser/sub/20181203184344817100_contents.do
