const sources = [
  {
    title: "VISITKOREA：酱蟹 / Soy Sauce Marinated Crab",
    url: "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=178617",
  },
  {
    title: "VISITKOREA：东大门一只鸡街",
    url: "https://english.visitkorea.or.kr/svc/whereToGo/locIntrdn/rgnContentsView.do?vcontsId=62662",
  },
  {
    title: "VISITKOREA：冷面 / Cold Buckwheat Noodles",
    url: "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=178819",
  },
  {
    title: "VISITKOREA：猪蹄 / Braised Pigs' Feet",
    url: "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=178577",
  },
  {
    title: "VISITKOREA：广藏市场美食",
    url: "https://english.visitkorea.or.kr/svc/contents/contentsViewCid.do?cmsCid=2989581",
  },
  {
    title: "VISITKOREA：生拌牛肉 / Yukhoe",
    url: "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=192945",
  },
  {
    title: "VISITKOREA：血肠汤饭 / Sundae-gukbap",
    url: "https://english.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=178196",
  },
  {
    title: "VISITKOREA：长忠洞猪蹄街",
    url: "https://english.visitkorea.or.kr/svc/whereToGo/locIntrdn/rgnContentsView.do?vcontsId=85189",
  },
  {
    title: "VISITKOREA：参鸡汤 / Samgyetang",
    url: "https://english.visitkorea.or.kr/svc/whereToGo/locIntrdn/rgnContentsView.do?vcontsId=99774",
  },
  {
    title: "Visit Seoul：首尔代表餐饮街",
    url: "https://english.visitseoul.net/editorspicks/Legendary-Restaurant-Alleys-That-Everybody-Knows/ENN033616",
  },
  {
    title: "Creative Commons：CC BY 许可说明",
    url: "https://creativecommons.org/licenses/by/2.0/",
  },
  {
    title: "Creative Commons：CC BY-SA 许可说明",
    url: "https://creativecommons.org/licenses/by-sa/2.0/",
  },
  {
    title: "Creative Commons：CC0 许可说明",
    url: "https://creativecommons.org/publicdomain/zero/1.0/",
  },
];

const photoCredits = [
  {
    id: "bbq",
    title: "Dwaeji-galbi",
    author: "egg / Hong, Yun Seon",
    license: "CC BY 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Korean_barbecue-Dwaeji_galbi-01.jpg",
  },
  {
    id: "chicken",
    title: "Yangnyeom Chicken",
    author: "Startandstar",
    license: "CC0",
    page: "https://commons.wikimedia.org/wiki/File:Yangnyeom_Chicken_Korean_fried_chicken.jpg",
  },
  {
    id: "bibimbap",
    title: "Bibimbap",
    author: "Chloe Lim",
    license: "CC BY 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Bibimbap_6.jpg",
  },
  {
    id: "gimbap",
    title: "Gimbap",
    author: "changupn",
    license: "CC0",
    page: "https://commons.wikimedia.org/wiki/File:Gimbap_(pixabay).jpg",
  },
  {
    id: "hanjeongsik",
    title: "Hanjeongsik",
    author: "James and Winnie Maeng",
    license: "CC BY 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Korean_cuisine-Hanjeongsik-01.jpg",
  },
  {
    id: "bingsu",
    title: "Green tea bingsu",
    author: "keepark",
    license: "CC BY 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Korean_shaved_ice-Green_tea_bingsu-04.jpg",
  },
  {
    id: "yukhoe",
    title: "Yukhoe",
    author: "FotoosVanRobin",
    license: "CC BY-SA 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Korean.cuisine-Yukhoe-04.jpg",
  },
  {
    id: "gejang",
    title: "Ganjang gejang",
    author: "egg / Hong, Yun Seon",
    license: "CC BY 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Korean_cuisine-Ganjang_gejang-01.jpg",
  },
  {
    id: "jokbal",
    title: "Jokbal",
    author: "ayustety",
    license: "CC BY-SA 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Korean.food-Jokbal-01.jpg",
  },
  {
    id: "sundae",
    title: "Sundae-gukbap",
    author: "pcamp",
    license: "CC BY 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Korean_soup-Sundae_gukbap-01.jpg",
  },
  {
    id: "gamjatang",
    title: "Gamjatang",
    author: "comicpie",
    license: "CC BY 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Korean.food-Gamjatang-01.jpg",
  },
  {
    id: "agujjim",
    title: "Agujjim",
    author: "Jamie",
    license: "CC BY 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Korean_steamed_food-Agujjim-01.jpg",
  },
  {
    id: "dakhanmari",
    title: "Dak hanmari",
    author: "Larry",
    license: "CC BY 2.5",
    page: "https://commons.wikimedia.org/wiki/File:Korean_cuisine-Dak_hanmari-02.jpg",
  },
  {
    id: "samgyetang",
    title: "Samgyetang",
    author: "Prince Roy",
    license: "CC BY 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Korean_soup-Samgyetang-04.jpg",
  },
  {
    id: "naengmyeon",
    title: "Mul naengmyeon",
    author: "avlxyz",
    license: "CC BY-SA 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Korean.noodles-Mul.naengmyeon-01.jpg",
  },
  {
    id: "kalguksu",
    title: "Kalguksu",
    author: "jslander",
    license: "CC BY 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Korean.noodle-Kalguksu-01.jpg",
  },
  {
    id: "budae",
    title: "Budae-jjigae",
    author: "Jo del Corro",
    license: "CC BY 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Budae-jjigae.jpg",
  },
  {
    id: "gwangjang",
    title: "Gwangjang Market Eats",
    author: "Korea.net / KOCIS, JEON HAN",
    license: "CC BY-SA 2.0",
    page: "https://commons.wikimedia.org/wiki/File:Korea_GwangjangMarket_Eats_01_(13885110035).jpg",
  },
];

const foods = [
  {
    id: "bbq",
    cnName: "韩式烤肉",
    krName: "고기구이 / 돼지갈비",
    enName: "Korean BBQ / Galbi",
    difficulty: "常规",
    image: "./assets/photos/bbq.jpg",
    imageAlt: "韩式烤肉",
    imageCredit: "Wikimedia Commons · CC BY 2.0",
    palette: "linear-gradient(135deg, #4a2a21 0%, #a45a32 50%, #e0a84d 100%)",
    reason: "第一次来首尔大概率会吃，适合作为多人晚餐和社交餐。",
    chinaGap: "国内也常见，首尔优势在肉类选择、炭火/铁板、包菜和小菜组合。",
    flavor: "焦香、油脂香和蒜片辣椒同吃，猪五花、猪排骨、韩牛体验差异很大。",
    areas: ["麻浦", "弘大", "江南", "明洞"],
    audience: "第一次来韩国、同行口味差异大、想稳妥聚餐的人。",
    warning: "热门商圈价格差异大；韩牛预算明显更高。",
    price: "15,000-35,000 韩元 / 人起，约 66-154 元人民币",
  },
  {
    id: "chicken",
    cnName: "韩式炸鸡",
    krName: "치킨",
    enName: "Korean Fried Chicken",
    difficulty: "常规",
    image: "./assets/photos/chicken.jpg",
    imageAlt: "韩式炸鸡",
    imageCredit: "Wikimedia Commons · CC0",
    palette: "linear-gradient(135deg, #8e2f23 0%, #dc6a35 45%, #f0bc58 100%)",
    reason: "不算稀缺，但首尔夜宵、外卖和啤酒文化绕不开它。",
    chinaGap: "差异主要在酱料、半半口味、萝卜泡菜和外卖夜宵场景。",
    flavor: "甜辣、蒜香、酱油、原味都常见；外皮脆，酱料口味偏重。",
    areas: ["弘大", "江南", "明洞", "酒店外卖"],
    audience: "想吃夜宵、同行有保守口味、看球聊天的人。",
    warning: "容易偏甜偏咸；热门连锁不用专门绕远。",
    price: "20,000-28,000 韩元 / 份，约 88-123 元人民币",
  },
  {
    id: "bibimbap",
    cnName: "石锅 / 全州拌饭",
    krName: "비빔밥",
    enName: "Bibimbap",
    difficulty: "常规",
    image: "./assets/photos/bibimbap.jpg",
    imageAlt: "韩式拌饭",
    imageCredit: "Wikimedia Commons · CC BY 2.0",
    palette: "linear-gradient(135deg, #7d3424 0%, #d48338 48%, #627f45 100%)",
    reason: "经典韩餐入门项，适合午餐和不想冒险的一餐。",
    chinaGap: "首尔版本的小菜、辣酱、锅巴和蔬菜处理更完整。",
    flavor: "蔬菜、米饭、辣酱和蛋黄混合，石锅版有锅巴香。",
    areas: ["仁寺洞", "明洞", "北村", "商场餐厅"],
    audience: "素食友好、怕踩雷、需要快速正餐的人。",
    warning: "看似清淡但辣酱可不少；素食者需确认是否有牛肉。",
    price: "10,000-16,000 韩元 / 份，约 44-70 元人民币",
  },
  {
    id: "gimbap",
    cnName: "紫菜包饭",
    krName: "김밥",
    enName: "Gimbap",
    difficulty: "常规",
    image: "./assets/photos/gimbap.jpg",
    imageAlt: "紫菜包饭",
    imageCredit: "Wikimedia Commons · CC0",
    palette: "linear-gradient(135deg, #263f34 0%, #7e8d3f 48%, #e5b44d 100%)",
    reason: "赶行程、坐火车、逛市场时很实用，是韩国日常快餐。",
    chinaGap: "比寿司卷更偏家常，常见腌萝卜、鸡蛋、火腿、牛蒡和芝麻油香。",
    flavor: "咸香、芝麻油香明显，口味轻，适合配泡菜或辣炒年糕。",
    areas: ["便利店", "连锁小店", "传统市场", "高铁站"],
    audience: "赶时间、预算有限、需要轻食补给的人。",
    warning: "不是精致料理；便利店版和现包版差异很大。",
    price: "3,500-7,000 韩元 / 卷，约 15-31 元人民币",
  },
  {
    id: "hanjeongsik",
    cnName: "韩定食",
    krName: "한정식",
    enName: "Hanjeongsik",
    difficulty: "常规",
    image: "./assets/photos/hanjeongsik.jpg",
    imageAlt: "韩定食",
    imageCredit: "Wikimedia Commons · CC BY 2.0",
    palette: "linear-gradient(135deg, #4f3b2d 0%, #bd8744 48%, #e8d3a1 100%)",
    reason: "想一次看见小菜、汤、主菜和摆盘时，韩定食最省心。",
    chinaGap: "国内常缩成套餐饭，首尔更重视小菜数量、上菜顺序和季节感。",
    flavor: "口味跨度大，从清淡小菜到烤鱼、炖肉、酱菜都有。",
    areas: ["仁寺洞", "北村", "景福宫周边", "江南"],
    audience: "家庭旅行、长辈同行、想坐下来慢慢吃的人。",
    warning: "价格跨度大；高端店需预约，低价套餐不必期待仪式感。",
    price: "18,000-60,000 韩元 / 人，约 79-264 元人民币",
  },
  {
    id: "bingsu",
    cnName: "雪冰 / 韩式刨冰",
    krName: "빙수",
    enName: "Bingsu",
    difficulty: "常规",
    image: "./assets/photos/bingsu.jpg",
    imageAlt: "韩式刨冰",
    imageCredit: "Wikimedia Commons · CC BY 2.0",
    palette: "linear-gradient(135deg, #587469 0%, #c7d6ba 48%, #f1d8aa 100%)",
    reason: "逛街空档最实用的甜品，尤其夏天和下午茶时段。",
    chinaGap: "韩国店常见牛奶冰、黄豆粉、红豆、抹茶和季节水果组合。",
    flavor: "冰体细，奶香轻，红豆/黄豆粉/抹茶款比普通刨冰更温和。",
    areas: ["明洞", "弘大", "江南", "圣水"],
    audience: "甜品爱好者、逛街休息、多人分食。",
    warning: "分量大，建议两人以上分；网红店不一定值得排长队。",
    price: "12,000-20,000 韩元 / 份，约 53-88 元人民币",
  },
  {
    id: "yukhoe",
    cnName: "韩式生拌牛肉",
    krName: "육회 / 육회탕탕이",
    enName: "Yukhoe / Korean Beef Tartare",
    difficulty: "挑战",
    image: "./assets/photos/yukhoe.jpg",
    imageAlt: "韩式生拌牛肉",
    imageCredit: "Wikimedia Commons · CC BY-SA 2.0",
    palette: "linear-gradient(135deg, #641f1a 0%, #c44a35 45%, #f3b45b 100%)",
    reason: "广藏市场代表体验，芝麻油、梨丝、蛋黄和鲜切牛肉是关键。",
    chinaGap: "生食级牛肉、当天处理和高翻台供应链更难稳定复刻。",
    flavor: "牛肉软嫩，芝麻油坚果香明显，梨丝清甜；进阶版生牛肉章鱼会有活章鱼的弹跳口感。",
    areas: ["广藏市场", "钟路"],
    audience: "能接受生食、喜欢牛肉原味的人。",
    warning: "生肉食品；肠胃敏感、孕妇、免疫力低者不建议。",
    price: "18,000-35,000 韩元 / 盘，约 79-154 元人民币",
  },
  {
    id: "gejang",
    cnName: "酱蟹",
    krName: "간장게장 / 양념게장",
    enName: "Ganjang-gejang / Soy Sauce Marinated Crab",
    difficulty: "挑战",
    image: "./assets/photos/gejang.jpg",
    imageAlt: "韩式酱油蟹",
    imageCredit: "Wikimedia Commons · CC BY 2.0",
    palette: "linear-gradient(135deg, #6f271f 0%, #d66b36 48%, #f1c161 100%)",
    reason: "韩国代表性生腌海鲜，“饭小偷”的核心体验是蟹黄拌饭。",
    chinaGap: "鲜蟹、冷链和酱油腌制配方决定成败，差一点就容易腥或甜腻。",
    flavor: "咸鲜、微甜、蟹黄浓郁，蟹壳拌饭是重点体验；辣酱蟹比酱油蟹更刺激。",
    areas: ["明洞", "弘大", "新沙 / 狎鸥亭"],
    audience: "海鲜爱好者、能接受生腌的人。",
    warning: "甲壳类过敏、孕妇、免疫力低或肠胃敏感者不建议。",
    price: "25,000-55,000 韩元 / 人份或定食，约 110-242 元人民币",
  },
  {
    id: "jokbal",
    cnName: "韩式酱卤猪蹄",
    krName: "족발",
    enName: "Jokbal / Braised Pig's Feet",
    difficulty: "进阶",
    image: "./assets/photos/jokbal.jpg",
    imageAlt: "韩式酱卤猪蹄",
    imageCredit: "Wikimedia Commons · CC BY-SA 2.0",
    palette: "linear-gradient(135deg, #4a2a21 0%, #a55a2d 50%, #e1b66a 100%)",
    reason: "长忠洞猪蹄街代表首尔夜宵和下酒菜文化。",
    chinaGap: "韩式重点是酱油姜蒜香、胶质切片、虾酱和包菜包食。",
    flavor: "皮筋道、胶质足，肉味甜咸；配蒜、辣椒、虾酱、包菜叶后更清爽。",
    areas: ["东大门 / 长忠洞", "市厅", "圣水"],
    audience: "爱猪蹄、胶质口感和下酒菜的人。",
    warning: "多按大盘卖，单人不友好；肥皮和胶质感明显。",
    price: "35,000-60,000 韩元 / 盘，约 154-264 元人民币",
  },
  {
    id: "sundae",
    cnName: "血肠汤饭 / 米肠",
    krName: "순대국밥 / 순대",
    enName: "Sundae-gukbap / Korean Blood Sausage Soup",
    difficulty: "进阶",
    image: "./assets/photos/sundae.jpg",
    imageAlt: "血肠汤饭",
    imageCredit: "Wikimedia Commons · CC BY 2.0",
    palette: "linear-gradient(135deg, #302923 0%, #8f4b36 52%, #d7ba86 100%)",
    reason: "韩国平民汤饭代表，市场和地铁站周边都常见。",
    chinaGap: "米肠、猪骨汤和紫苏粉组成独立风味，和中式血肠不是一回事。",
    flavor: "汤厚、血肠软糯，紫苏粉有坚果香，可按喜好加辣酱、虾酱和葱。",
    areas: ["新林", "广藏市场", "钟路"],
    audience: "内脏爱好者、预算友好型游客。",
    warning: "可能有肝、心、头肉；可点“순대만”只要血肠。",
    price: "9,000-13,000 韩元 / 碗，约 40-57 元人民币",
  },
  {
    id: "gamjatang",
    cnName: "马铃薯排骨汤",
    krName: "감자탕",
    enName: "Gamjatang / Pork Backbone Stew",
    difficulty: "进阶",
    image: "./assets/photos/gamjatang.jpg",
    imageAlt: "马铃薯排骨汤",
    imageCredit: "Wikimedia Commons · CC BY 2.0",
    palette: "linear-gradient(135deg, #6c261d 0%, #c84a2d 48%, #6f8b54 100%)",
    reason: "韩国夜宵、醒酒和多人锅物代表，猪脊骨和紫苏是灵魂。",
    chinaGap: "常被做成普通排骨锅，少了紫苏香、拆骨吃法和收尾炒饭。",
    flavor: "辣而厚重，猪骨肉软烂，土豆吸汤，紫苏香非常明显。",
    areas: ["钟路", "大学路", "永登浦", "江南"],
    audience: "重口味、爱啃骨头、多人聚餐。",
    warning: "骨头多，紫苏味强；小锅也可能分量很大。",
    price: "10,000-14,000 韩元 / 单人汤；30,000-50,000 韩元 / 锅，约 44-220 元人民币",
  },
  {
    id: "agujjim",
    cnName: "辣炖安康鱼",
    krName: "아귀찜",
    enName: "Agujjim / Spicy Braised Monkfish",
    difficulty: "挑战",
    image: "./assets/photos/agujjim.jpg",
    imageAlt: "辣炖安康鱼",
    imageCredit: "Wikimedia Commons · CC BY 2.0",
    palette: "linear-gradient(135deg, #8b251c 0%, #de3f2e 45%, #d9a23f 100%)",
    reason: "韩国海鲜馆风格很强，豆芽山和重辣蒜香辨识度高。",
    chinaGap: "安康鱼处理、豆芽比例和浓稠辣酱都容易被简化。",
    flavor: "辣、蒜香重、酱汁浓稠，鱼肉紧实，鱼皮和鱼肝部位更有胶质感。",
    areas: ["钟路", "麻浦", "江南", "海鲜专门店街区"],
    audience: "重辣爱好者、海鲜爱好者。",
    warning: "辣度和蒜味都高；软骨和胶质感明显。",
    price: "35,000-70,000 韩元 / 盘，约 154-308 元人民币",
  },
  {
    id: "dakhanmari",
    cnName: "东大门一只鸡",
    krName: "닭한마리",
    enName: "Dak-hanmari / Whole Chicken Stew",
    difficulty: "入门",
    image: "./assets/photos/dakhanmari.jpg",
    imageAlt: "东大门一只鸡",
    imageCredit: "Wikimedia Commons · CC BY 2.5",
    palette: "linear-gradient(135deg, #825f35 0%, #e0b76b 55%, #f5e4bc 100%)",
    reason: "东大门代表锅物，清汤煮整鸡，自己调蘸酱，最后加面。",
    chinaGap: "容易被做成普通鸡火锅，少了酸辣芥末蘸酱和刀切面收尾。",
    flavor: "鸡汤清爽鲜甜，蘸酱可酸、辣、芥末冲；加年糕和面后更有饱足感。",
    areas: ["东大门", "钟路5街"],
    audience: "2-4 人同行、怕太辣、想吃热汤的人。",
    warning: "多按整锅点；人少可能吃不完。",
    price: "28,000-40,000 韩元 / 锅，面或年糕另加约 2,000-4,000 韩元，约 123-176 元人民币",
  },
  {
    id: "samgyetang",
    cnName: "参鸡汤",
    krName: "삼계탕",
    enName: "Samgyetang / Ginseng Chicken Soup",
    difficulty: "入门",
    image: "./assets/photos/samgyetang.jpg",
    imageAlt: "参鸡汤",
    imageCredit: "Wikimedia Commons · CC BY 2.0",
    palette: "linear-gradient(135deg, #7a5a37 0%, #d7b16f 48%, #f4ead2 100%)",
    reason: "韩国夏季伏日进补代表菜，初到首尔也很稳妥。",
    chinaGap: "童子鸡、糯米、人参和整鸡仪式感常被简化成普通鸡汤。",
    flavor: "鸡汤温润，带人参药香，糯米吸汤后像粥，整体清淡不辣。",
    areas: ["景福宫 / 西村", "市厅", "明洞"],
    audience: "老人、小孩、怕辣者、想吃热汤的人。",
    warning: "一人一只鸡分量不小；不喜欢人参味者谨慎。",
    price: "16,000-28,000 韩元 / 份，约 70-123 元人民币；鲍鱼或乌骨鸡版本更高",
  },
  {
    id: "naengmyeon",
    cnName: "韩式冷面",
    krName: "평양냉면 / 함흥냉면",
    enName: "Naengmyeon / Cold Buckwheat Noodles",
    difficulty: "进阶",
    image: "./assets/photos/naengmyeon.jpg",
    imageAlt: "韩式冷面",
    imageCredit: "Wikimedia Commons · CC BY-SA 2.0",
    palette: "linear-gradient(135deg, #355f69 0%, #c5d4c8 52%, #f2ead8 100%)",
    reason: "首尔老派韩餐门类，尤其平壤冷面和甜辣冷面差异很大。",
    chinaGap: "荞麦面、冷肉汤和极淡调味难复刻，常被改成酸甜辣重口。",
    flavor: "冷、清、淡，荞麦香明显，越吃越有肉汤和发酵萝卜汤的回甘；咸兴冷面更筋道、更辣。",
    areas: ["乙支路", "中区", "麻浦", "汝矣岛"],
    audience: "喜欢清淡、面食和老派餐馆的人。",
    warning: "第一次可能觉得淡；荞麦过敏者避开。",
    price: "12,000-18,000 韩元 / 碗，约 53-79 元人民币",
  },
  {
    id: "kalguksu",
    cnName: "韩式刀削面",
    krName: "칼국수",
    enName: "Kalguksu / Knife-cut Noodle Soup",
    difficulty: "入门",
    image: "./assets/photos/kalguksu.jpg",
    imageAlt: "韩式刀削面",
    imageCredit: "Wikimedia Commons · CC BY 2.0",
    palette: "linear-gradient(135deg, #b4743d 0%, #e4bc6a 52%, #fff1d5 100%)",
    reason: "明洞、南大门都容易安排，是首尔日常感很强的午餐。",
    chinaGap: "重点在现切面、汤底、泡菜和饺子搭配，而不是普通汤面。",
    flavor: "面条柔韧，汤底可清鲜或贝类鲜，泡菜通常更酸辣，适合中午快速吃。",
    areas: ["明洞", "南大门", "仁寺洞"],
    audience: "面食党、怕辣者、家庭同行。",
    warning: "有些汤底含贝类或牛肉，忌口者先确认。",
    price: "9,000-13,000 韩元 / 碗，约 40-57 元人民币",
  },
  {
    id: "budae",
    cnName: "部队锅本地吃法",
    krName: "부대찌개",
    enName: "Budae-jjigae / Army Stew",
    difficulty: "入门",
    image: "./assets/photos/budae.jpg",
    imageAlt: "部队锅",
    imageCredit: "Wikimedia Commons · CC BY 2.0",
    palette: "linear-gradient(135deg, #96291e 0%, #d65c35 48%, #e7c159 100%)",
    reason: "国内也常见，但韩国吃法更强调多人锅和加料节奏。",
    chinaGap: "泡菜酸度、午餐肉香肠组合、拉面和收尾主食更完整。",
    flavor: "酸辣咸鲜，泡菜和加工肉香明显，芝士和拉面让汤更厚。",
    areas: ["弘大 / 新村", "江南", "梨泰院", "议政府半日路线"],
    audience: "第一次来韩国、同行口味差异大的人。",
    warning: "钠含量高，加工肉多；清淡饮食者慎选。",
    price: "10,000-15,000 韩元 / 人，约 44-66 元人民币",
  },
  {
    id: "gwangjang",
    cnName: "广藏市场小吃组合",
    krName: "광장시장 먹거리",
    enName: "Gwangjang Market Street Food",
    difficulty: "入门",
    image: "./assets/photos/gwangjang.jpg",
    imageAlt: "广藏市场小吃摊",
    imageCredit: "Wikimedia Commons · CC BY-SA 2.0",
    palette: "linear-gradient(135deg, #b83225 0%, #e5a43b 48%, #2d7257 100%)",
    reason: "绿豆煎饼、紫菜包饭、辣炒年糕等能一次体验市场氛围。",
    chinaGap: "差异在热摊现做、摊位坐吃、泡菜和酱料一起形成的场景。",
    flavor: "油香、甜辣、酱香、发酵酸辣并存；适合多人分食，每样少量尝。",
    areas: ["广藏市场", "钟路5街"],
    audience: "第一次来首尔、喜欢边走边吃的人。",
    warning: "热门时段拥挤；油炸和甜辣多，别一次点太满。",
    price: "3,000-12,000 韩元 / 单品，约 13-53 元人民币",
  },
];

const routes = [
  {
    title: "第一餐：低风险热汤",
    subtitle: "落地后先用热汤和面食开局",
    picks: ["东大门一只鸡", "参鸡汤", "韩式刀削面"],
    note: "适合刚到首尔、同行有老人小孩或不确定辣度的人。",
  },
  {
    title: "市场半日：广藏市场 + 钟路",
    subtitle: "把小吃、生拌牛肉和传统市场一次串起来",
    picks: ["广藏市场小吃组合", "韩式生拌牛肉", "血肠汤饭"],
    note: "建议每样少量分食，别一开始就排长队点大份。",
  },
  {
    title: "夜宵局：锅物和下酒菜",
    subtitle: "更像首尔本地人的晚餐节奏",
    picks: ["韩式酱卤猪蹄", "马铃薯排骨汤", "部队锅本地吃法"],
    note: "多人同行体验更好，单人可优先选单人汤饭或冷面。",
  },
  {
    title: "进阶挑战：生腌与强风味",
    subtitle: "确认肠胃状态后再安排",
    picks: ["酱蟹", "辣炖安康鱼", "韩式冷面"],
    note: "生腌、生肉和强辣不要连续安排，给行程留一点缓冲。",
  },
];

const areas = [
  {
    name: "明洞 / 南大门",
    tone: "适合刚到首尔、购物间隙和家庭同行。",
    foods: ["韩式刀削面", "参鸡汤", "酱蟹"],
  },
  {
    name: "钟路 / 仁寺洞",
    tone: "老城路线集中，适合传统汤饭、市场和晚餐。",
    foods: ["血肠汤饭", "马铃薯排骨汤", "广藏市场小吃组合"],
  },
  {
    name: "广藏市场",
    tone: "最适合截图分享的市场小吃区，游客多但执行简单。",
    foods: ["广藏市场小吃组合", "韩式生拌牛肉", "血肠汤饭"],
  },
  {
    name: "乙支路 / 东大门",
    tone: "夜景、老店和锅物都方便衔接。",
    foods: ["东大门一只鸡", "韩式冷面", "韩式酱卤猪蹄"],
  },
  {
    name: "弘大 / 新村",
    tone: "年轻人商圈，适合多人锅物、夜宵和不太正式的晚餐。",
    foods: ["部队锅本地吃法", "酱蟹", "马铃薯排骨汤"],
  },
  {
    name: "江南 / 新沙 / 狎鸥亭",
    tone: "餐厅选择多，适合把酱蟹、海鲜和晚餐预算放高一点。",
    foods: ["酱蟹", "辣炖安康鱼", "部队锅本地吃法"],
  },
  {
    name: "景福宫 / 西村 / 北村",
    tone: "宫殿和韩屋路线后，安排一顿温和传统汤品更顺。",
    foods: ["参鸡汤", "韩式冷面", "韩式刀削面"],
  },
];

const overviewGroups = [
  {
    name: "重点特色",
    note: "最能拉开和普通韩餐店差异的首尔体验。",
    items: [
      ["韩式生拌牛肉", "육회", "广藏市场 / 钟路", "挑战"],
      ["酱蟹", "간장게장", "明洞 / 新沙 / 弘大", "挑战"],
      ["东大门一只鸡", "닭한마리", "东大门 / 钟路5街", "入门"],
      ["血肠汤饭", "순대국밥", "新林 / 广藏市场", "进阶"],
      ["马铃薯排骨汤", "감자탕", "钟路 / 大学路 / 江南", "进阶"],
      ["辣炖安康鱼", "아귀찜", "麻浦 / 江南 / 海鲜馆", "挑战"],
    ],
  },
  {
    name: "汤饭与面食",
    note: "适合早餐、午餐和不想吃太重的一餐。",
    items: [
      ["参鸡汤", "삼계탕", "景福宫 / 市厅 / 明洞", "入门"],
      ["韩式刀削面", "칼국수", "明洞 / 南大门", "入门"],
      ["韩式冷面", "냉면", "乙支路 / 麻浦 / 汝矣岛", "进阶"],
      ["牛骨汤", "설렁탕", "钟路 / 明洞 / 江南", "入门"],
      ["猪肉汤饭", "돼지국밥", "汤饭店 / 市场周边", "入门"],
      ["泡菜汤 / 大酱汤", "김치찌개 / 된장찌개", "办公区 / 家常饭馆", "入门"],
    ],
  },
  {
    name: "市场小吃",
    note: "适合边逛边分食，别一次点太满。",
    items: [
      ["绿豆煎饼", "빈대떡", "广藏市场", "入门"],
      ["麻药紫菜包饭", "마약김밥", "广藏市场", "入门"],
      ["辣炒年糕", "떡볶이", "市场 / 弘大 / 明洞", "入门"],
      ["鱼糕串", "어묵", "市场 / 路边摊", "入门"],
      ["糖饼", "호떡", "仁寺洞 / 市场", "入门"],
      ["扭结甜甜圈", "꽈배기", "广藏市场 / 传统市场", "入门"],
    ],
  },
  {
    name: "夜宵与锅物",
    note: "多人同行更好点菜，适合晚餐后半场。",
    items: [
      ["韩式猪蹄", "족발", "长忠洞 / 市厅", "进阶"],
      ["牡蛎包肉", "굴보쌈", "钟路3街", "进阶"],
      ["部队锅", "부대찌개", "弘大 / 新村 / 江南", "入门"],
      ["辣炒章鱼", "낙지볶음", "钟路 / 武桥洞", "挑战"],
      ["鸡爪", "닭발", "弘大 / 新村", "挑战"],
      ["海鲜葱饼 + 米酒", "해물파전 + 막걸리", "仁寺洞 / 传统酒馆", "入门"],
    ],
  },
  {
    name: "常规也值得吃",
    note: "不是本页重点，但第一次来首尔仍然实用。",
    items: [
      ["韩式烤肉", "고기구이", "麻浦 / 弘大 / 江南", "常规"],
      ["烤韩牛", "한우구이", "江南 / 狎鸥亭", "常规"],
      ["炸鸡", "치킨", "弘大 / 江南 / 外卖", "常规"],
      ["拌饭", "비빔밥", "仁寺洞 / 明洞", "常规"],
      ["紫菜包饭", "김밥", "连锁小店 / 市场", "常规"],
      ["韩定食", "한정식", "仁寺洞 / 北村 / 江南", "常规"],
    ],
  },
  {
    name: "甜品咖啡与补给",
    note: "放在行程空档，不必专门绕远。",
    items: [
      ["雪冰", "빙수", "明洞 / 弘大 / 江南", "常规"],
      ["韩式年糕", "떡", "传统市场 / 百货地下", "常规"],
      ["盐面包 / 韩式贝果", "소금빵 / 베이글", "圣水 / 安国", "常规"],
      ["烘焙咖啡", "카페", "圣水 / 延南 / 汉南", "常规"],
      ["香蕉牛奶", "바나나맛 우유", "便利店", "常规"],
      ["便利店三角饭团", "삼각김밥", "便利店", "常规"],
    ],
  },
];

const difficultyClass = {
  常规: "regular",
  入门: "easy",
  进阶: "medium",
  挑战: "hard",
};

const detailFoodAliases = {
  血肠汤饭: "血肠汤饭 / 米肠",
  韩式猪蹄: "韩式酱卤猪蹄",
  部队锅: "部队锅本地吃法",
  炸鸡: "韩式炸鸡",
  拌饭: "石锅 / 全州拌饭",
  雪冰: "雪冰 / 韩式刨冰",
};

const overviewImageMap = {
  韩式生拌牛肉: "./assets/photos/yukhoe.jpg",
  酱蟹: "./assets/photos/gejang.jpg",
  东大门一只鸡: "./assets/photos/dakhanmari.jpg",
  血肠汤饭: "./assets/photos/sundae.jpg",
  马铃薯排骨汤: "./assets/photos/gamjatang.jpg",
  辣炖安康鱼: "./assets/photos/agujjim.jpg",
  参鸡汤: "./assets/photos/samgyetang.jpg",
  韩式刀削面: "./assets/photos/kalguksu.jpg",
  韩式冷面: "./assets/photos/naengmyeon.jpg",
  韩式猪蹄: "./assets/photos/jokbal.jpg",
  部队锅: "./assets/photos/budae.jpg",
  韩式烤肉: "./assets/photos/bbq.jpg",
  炸鸡: "./assets/photos/chicken.jpg",
  拌饭: "./assets/photos/bibimbap.jpg",
  紫菜包饭: "./assets/photos/gimbap.jpg",
  韩定食: "./assets/photos/hanjeongsik.jpg",
  雪冰: "./assets/photos/bingsu.jpg",
  牛骨汤: "./assets/photos/generated/seolleongtang.jpg",
  猪肉汤饭: "./assets/photos/generated/dwaeji-gukbap.jpg",
  "泡菜汤 / 大酱汤": "./assets/photos/generated/jjigae-set.jpg",
  绿豆煎饼: "./assets/photos/generated/bindaetteok.jpg",
  麻药紫菜包饭: "./assets/photos/generated/mayak-gimbap.jpg",
  辣炒年糕: "./assets/photos/generated/tteokbokki.jpg",
  鱼糕串: "./assets/photos/generated/eomuk.jpg",
  糖饼: "./assets/photos/generated/hotteok.jpg",
  扭结甜甜圈: "./assets/photos/generated/kkwabaegi.jpg",
  牡蛎包肉: "./assets/photos/generated/gul-bossam.jpg",
  辣炒章鱼: "./assets/photos/generated/nakji-bokkeum.jpg",
  鸡爪: "./assets/photos/generated/dakbal.jpg",
  "海鲜葱饼 + 米酒": "./assets/photos/generated/haemul-pajeon-makgeolli.jpg",
  烤韩牛: "./assets/photos/generated/hanwoo.jpg",
  韩式年糕: "./assets/photos/generated/tteok.jpg",
  "盐面包 / 韩式贝果": "./assets/photos/generated/salt-bread-bagel.jpg",
  烘焙咖啡: "./assets/photos/generated/cafe-pastries.jpg",
  香蕉牛奶: "./assets/photos/generated/banana-milk.jpg",
  便利店三角饭团: "./assets/photos/generated/samgak-gimbap.jpg",
};

const generatedImagePrompts = {
  牛骨汤: "polished 3D render of Korean seolleongtang ox bone soup in a white bowl, sliced beef, scallions, rice and kimchi side dishes, warm Seoul restaurant table, no text",
  猪肉汤饭: "polished 3D render of Korean dwaeji-gukbap pork rice soup, milky broth, sliced pork, rice bowl, kimchi side dishes, warm restaurant lighting, no text",
  "泡菜汤 / 大酱汤": "polished 3D render of Korean kimchi jjigae and doenjang jjigae home-style stew set, bubbling earthenware bowls, rice and banchan, no text",
  绿豆煎饼: "polished 3D render of Korean bindaetteok mung bean pancake on a market plate, soy onion dipping sauce, Gwangjang market mood, no text",
  麻药紫菜包饭: "polished 3D render of mini Korean mayak gimbap rolls with mustard dipping sauce, market snack styling, no text",
  辣炒年糕: "polished 3D render of Korean tteokbokki in glossy red sauce with fish cake and scallions, street food tray, no text",
  鱼糕串: "polished 3D render of Korean eomuk fish cake skewers in hot broth, street market stall mood, no text",
  糖饼: "polished 3D render of Korean hotteok sweet pancake, cinnamon sugar filling, winter market paper cup, no text",
  扭结甜甜圈: "polished 3D render of Korean twisted doughnuts kkwabaegi with sugar coating, market bakery tray, no text",
  牡蛎包肉: "polished 3D render of Korean gul bossam, sliced pork belly, fresh oysters, kimchi, napa wraps, restaurant table, no text",
  辣炒章鱼: "polished 3D render of Korean nakji bokkeum spicy stir-fried octopus, red sauce, bean sprouts, sesame, no text",
  鸡爪: "polished 3D render of Korean spicy chicken feet dakbal in red sauce, late-night pojangmacha table, no text",
  "海鲜葱饼 + 米酒": "polished 3D render of Korean haemul pajeon seafood scallion pancake with makgeolli bowl, traditional pub table, no text",
  烤韩牛: "polished 3D render of Korean hanwoo beef grilling on tabletop barbecue, lettuce wraps and banchan, upscale Seoul restaurant, no text",
  韩式年糕: "polished 3D render of assorted Korean tteok rice cakes in pastel colors on a traditional tray, tea setting, no text",
  "盐面包 / 韩式贝果": "polished 3D render of Seoul cafe salt bread and Korean-style bagels on a minimal cafe table, no text",
  烘焙咖啡: "polished 3D render of Seoul specialty coffee and pastries on a cafe table, warm modern cafe lighting, no text",
  香蕉牛奶: "polished 3D render of Korean banana milk bottle with convenience store snack mood, no brand logo, no text",
  便利店三角饭团: "polished 3D render of Korean convenience store triangle gimbap, clean wrapper shape without brand text, store shelf mood, no text",
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function getDetailedFood(cnName) {
  const targetName = detailFoodAliases[cnName] || cnName;
  return foods.find((food) => food.cnName === targetName);
}

function renderFoodCard(food) {
  const imageMarkup = food.image
    ? `<img src="${escapeHtml(food.image)}" alt="${escapeHtml(food.imageAlt)}" loading="lazy">`
    : `<div class="placeholder-art" aria-hidden="true"><div class="plate"></div></div>`;

  return `
    <article class="food-card" data-difficulty="${escapeHtml(food.difficulty)}">
      <div class="image-frame" style="--placeholder: ${food.palette}">
        ${imageMarkup}
        <div class="image-label">${escapeHtml(food.cnName)} · ${escapeHtml(food.krName)}</div>
      </div>
      <div class="food-body">
        <div class="food-topline">
          <div>
            <h3 class="food-title">${escapeHtml(food.cnName)}</h3>
            <div class="names">
              <span>韩文：${escapeHtml(food.krName)}</span>
              <span>英文：${escapeHtml(food.enName)}</span>
            </div>
          </div>
          <span class="difficulty ${difficultyClass[food.difficulty]}">${escapeHtml(food.difficulty)}</span>
        </div>
        <p class="food-summary">${escapeHtml(food.reason)}</p>
        <div class="detail-grid">
          <div class="detail full">
            <span class="detail-label">国内差异</span>
            <p>${escapeHtml(food.chinaGap)}</p>
          </div>
          <div class="detail">
            <span class="detail-label">口味特点</span>
            <p>${escapeHtml(food.flavor)}</p>
          </div>
          <div class="detail">
            <span class="detail-label">推荐尝试地区</span>
            <p>${escapeHtml(food.areas.join(" / "))}</p>
          </div>
          <div class="detail">
            <span class="detail-label">适合人群</span>
            <p>${escapeHtml(food.audience)}</p>
          </div>
          <div class="detail">
            <span class="detail-label">避雷提醒</span>
            <p>${escapeHtml(food.warning)}</p>
          </div>
        </div>
        <div class="card-footer">
          <div class="price">${escapeHtml(food.price)}</div>
          <div class="credit">${escapeHtml(food.imageCredit)}</div>
        </div>
      </div>
    </article>
  `;
}

function renderRoutes() {
  const routeList = document.querySelector("#route-list");
  routeList.innerHTML = routes
    .map(
      (route, index) => `
        <article class="route-card">
          <span class="route-step">${index + 1}</span>
          <h3>${escapeHtml(route.title)}</h3>
          <p>${escapeHtml(route.subtitle)}</p>
          <ul>
            ${route.picks.map((pick) => `<li>${escapeHtml(pick)}</li>`).join("")}
          </ul>
          <p class="section-note">${escapeHtml(route.note)}</p>
        </article>
      `,
    )
    .join("");
}

function renderAreas() {
  const areaGrid = document.querySelector("#area-grid");
  areaGrid.innerHTML = areas
    .map(
      (area) => `
        <article class="area-card">
          <h3>${escapeHtml(area.name)}</h3>
          <p>${escapeHtml(area.tone)}</p>
          <div class="area-foods">
            ${area.foods.map((food) => `<span class="area-pill">${escapeHtml(food)}</span>`).join("")}
          </div>
        </article>
      `,
    )
    .join("");
}

function flattenOverviewItems() {
  return overviewGroups.flatMap((group) =>
    group.items.map(([cnName, krName, area, level]) => {
      const food = getDetailedFood(cnName);
      return {
        cnName,
        krName,
        area,
        level,
        group: group.name,
        groupNote: group.note,
        food,
        image: food?.image || overviewImageMap[cnName],
        prompt: generatedImagePrompts[cnName],
      };
    }),
  );
}

function renderOverviewThumb(item) {
  if (item.image) {
    return `<img src="${escapeHtml(item.image)}" alt="${escapeHtml(item.cnName)}" loading="lazy">`;
  }

  return `
    <div class="overview-thumb pending" title="${escapeHtml(item.prompt || "待生成 3D 图")}">
      <span>3D</span>
      <small>待生成</small>
    </div>
  `;
}

function renderOverviewListItem(item) {
  return `
    <article class="overview-item${item.image ? "" : " needs-image"}">
      ${renderOverviewThumb(item)}
      <div class="overview-name">
        <b>${escapeHtml(item.cnName)}</b>
        <span>${escapeHtml(item.krName)}</span>
      </div>
      <p>${escapeHtml(item.area)}</p>
      <em class="${difficultyClass[item.level]}">${escapeHtml(item.level)}</em>
    </article>
  `;
}

function renderOverviewGroups(items) {
  const itemsByName = new Map(items.map((item) => [item.cnName, item]));

  return overviewGroups
    .map(
      (group) => `
        <article class="overview-card">
          <div class="overview-card-head">
            <h3>${escapeHtml(group.name)}</h3>
            <p>${escapeHtml(group.note)}</p>
          </div>
          <div class="overview-list">
            ${group.items.map(([cnName]) => renderOverviewListItem(itemsByName.get(cnName))).join("")}
          </div>
        </article>
      `,
    )
    .join("");
}

function renderGeneratedFoodCard(item) {
  return `
    <article class="food-card generated-card" data-difficulty="${escapeHtml(item.level)}">
      <div class="image-frame generated-frame">
        <div class="generated-art" role="img" aria-label="${escapeHtml(item.cnName)} 3D 图片待生成">
          <span>3D</span>
          <strong>专属图片待生成</strong>
          <small>不借用其他美食图片</small>
        </div>
        <div class="image-label">${escapeHtml(item.cnName)} · ${escapeHtml(item.krName)}</div>
      </div>
      <div class="food-body">
        <div class="food-topline">
          <div>
            <h3 class="food-title">${escapeHtml(item.cnName)}</h3>
            <div class="names">
              <span>韩文：${escapeHtml(item.krName)}</span>
              <span>分类：${escapeHtml(item.group)}</span>
            </div>
          </div>
          <span class="difficulty ${difficultyClass[item.level]}">${escapeHtml(item.level)}</span>
        </div>
        <p class="food-summary">${escapeHtml(item.groupNote)}</p>
        <div class="detail-grid">
          <div class="detail">
            <span class="detail-label">推荐尝试地区</span>
            <p>${escapeHtml(item.area)}</p>
          </div>
          <div class="detail">
            <span class="detail-label">图片状态</span>
            <p>当前缺少可安全使用的实拍图，已预留精致 3D 风格图片位。</p>
          </div>
        </div>
        <div class="card-footer">
          <div class="price">价格：建议按现场菜单确认</div>
          <div class="credit">3D image placeholder</div>
        </div>
      </div>
    </article>
  `;
}

function renderOverview() {
  const overviewGrid = document.querySelector("#overview-grid");
  const items = flattenOverviewItems();

  if (currentFilter === "全部") {
    overviewGrid.className = "overview-grid";
    overviewGrid.innerHTML = renderOverviewGroups(items);
    return;
  }

  const filtered = items.filter((item) => item.level === currentFilter);
  overviewGrid.className = "food-grid category-card-grid";
  overviewGrid.innerHTML = filtered.map((item) => (item.food ? renderFoodCard(item.food) : renderGeneratedFoodCard(item))).join("");
}

function renderSources() {
  const sourceLinks = document.querySelector("#source-links");
  sourceLinks.innerHTML = sources
    .map(
      (source) => `
        <a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">
          ${escapeHtml(source.title)}
        </a>
      `,
    )
    .join("");

  const photoCreditList = document.querySelector("#photo-credit-list");
  photoCreditList.innerHTML = photoCredits
    .map(
      (photo) => `
        <a href="${escapeHtml(photo.page)}" target="_blank" rel="noreferrer">
          <b>${escapeHtml(photo.title)}</b>
          <span>${escapeHtml(photo.author)} · ${escapeHtml(photo.license)}</span>
        </a>
      `,
    )
    .join("");
}

function bindFilters() {
  document.querySelectorAll(".filter-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".filter-button").forEach((item) => item.classList.remove("is-active"));
      button.classList.add("is-active");
      currentFilter = button.dataset.filter;
      renderOverview();
    });
  });
}

function getInitialFilter() {
  const params = new URLSearchParams(window.location.search);
  const filter = params.get("filter") || "全部";
  return ["全部", "常规", "入门", "进阶", "挑战"].includes(filter) ? filter : "全部";
}

let currentFilter = getInitialFilter();
renderRoutes();
renderAreas();
renderOverview();
renderSources();
bindFilters();
document.querySelectorAll(".filter-button").forEach((button) => {
  button.classList.toggle("is-active", button.dataset.filter === currentFilter);
});
