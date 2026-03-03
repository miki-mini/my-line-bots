"""
station_data.py - 駅データ一覧（ODPT API + 手動補完）
合計: 721駅
更新日: 2025-12-14 19:50:05
"""

STATIONS = [
    {
        "name": "あざみ野",
        "id": "odpt.Station:Tokyu.DenEnToshi.Azamino",
        "railway": "Tokyu"
    },
    {
        "name": "あざみ野",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Azamino",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "お台場海浜公園",
        "id": "odpt.Station:Yurikamome.Yurikamome.OdaibaKaihinkoen",
        "railway": "Yurikamome"
    },
    {
        "name": "かしわ台",
        "id": "odpt.Station:Sotetsu.Main.Kashiwadai",
        "railway": "Sotetsu"
    },
    {
        "name": "つくば",
        "id": "odpt.Station:MIR.TsukubaExpress.Tsukuba",
        "railway": "MIR"
    },
    {
        "name": "つつじヶ丘",
        "id": "odpt.Station:Keio.Keio.Tsutsujigaoka",
        "railway": "Keio"
    },
    {
        "name": "みどりの",
        "id": "odpt.Station:MIR.TsukubaExpress.Midorino",
        "railway": "MIR"
    },
    {
        "name": "みらい平",
        "id": "odpt.Station:MIR.TsukubaExpress.Miraidaira",
        "railway": "MIR"
    },
    {
        "name": "センター北",
        "id": "odpt.Station:YokohamaMunicipal.Blue.CenterKita",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "センター北",
        "id": "odpt.Station:YokohamaMunicipal.Green.CenterKita",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "センター南",
        "id": "odpt.Station:YokohamaMunicipal.Blue.CenterMinami",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "センター南",
        "id": "odpt.Station:YokohamaMunicipal.Green.CenterMinami",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "テレコムセンター",
        "id": "odpt.Station:Yurikamome.Yurikamome.TelecomCenter",
        "railway": "Yurikamome"
    },
    {
        "name": "一之江",
        "id": "odpt.Station:Toei.Shinjuku.Ichinoe",
        "railway": "Toei"
    },
    {
        "name": "万博記念公園",
        "id": "odpt.Station:MIR.TsukubaExpress.BampakuKinenKoen",
        "railway": "MIR"
    },
    {
        "name": "万願寺",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.Manganji",
        "railway": "TamaMonorail"
    },
    {
        "name": "三ツ沢上町",
        "id": "odpt.Station:YokohamaMunicipal.Blue.MitsuzawaKamicho",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "三ツ沢下町",
        "id": "odpt.Station:YokohamaMunicipal.Blue.MitsuzawaShimocho",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "三ノ輪",
        "id": "odpt.Station:TokyoMetro.Hibiya.Minowa",
        "railway": "TokyoMetro"
    },
    {
        "name": "三ノ輪橋",
        "id": "odpt.Station:Toei.Arakawa.Minowabashi",
        "railway": "Toei"
    },
    {
        "name": "三崎口",
        "id": "odpt.Station:Keikyu.Kurihama.Misakiguchi",
        "railway": "Keikyu"
    },
    {
        "name": "三浦海岸",
        "id": "odpt.Station:Keikyu.Kurihama.Miurakaigan",
        "railway": "Keikyu"
    },
    {
        "name": "三田",
        "id": "odpt.Station:Toei.Asakusa.Mita",
        "railway": "Toei"
    },
    {
        "name": "三田",
        "id": "odpt.Station:Toei.Mita.Mita",
        "railway": "Toei"
    },
    {
        "name": "三越前",
        "id": "odpt.Station:TokyoMetro.Ginza.Mitsukoshimae",
        "railway": "TokyoMetro"
    },
    {
        "name": "三越前",
        "id": "odpt.Station:TokyoMetro.Hanzomon.Mitsukoshimae",
        "railway": "TokyoMetro"
    },
    {
        "name": "三郷中央",
        "id": "odpt.Station:MIR.TsukubaExpress.MisatoChuo",
        "railway": "MIR"
    },
    {
        "name": "三鷹",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Mitaka",
        "railway": "JR-East"
    },
    {
        "name": "上北台",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.Kamikitadai",
        "railway": "TamaMonorail"
    },
    {
        "name": "上大岡",
        "id": "odpt.Station:Keikyu.Main.Kamiooka",
        "railway": "Keikyu"
    },
    {
        "name": "上大岡",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Kamiooka",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "上永谷",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Kaminagaya",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "上野",
        "id": "odpt.Station:JR-East.JobanRapid.Ueno",
        "railway": "JR-East"
    },
    {
        "name": "上野",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Ueno",
        "railway": "JR-East"
    },
    {
        "name": "上野",
        "id": "odpt.Station:JR-East.Takasaki.Ueno",
        "railway": "JR-East"
    },
    {
        "name": "上野",
        "id": "odpt.Station:JR-East.Utsunomiya.Ueno",
        "railway": "JR-East"
    },
    {
        "name": "上野",
        "id": "odpt.Station:JR-East.Yamanote.Ueno",
        "railway": "JR-East"
    },
    {
        "name": "上野",
        "id": "odpt.Station:JR-East.AkitaShinkansen.Ueno",
        "railway": "JR-East"
    },
    {
        "name": "上野",
        "id": "odpt.Station:JR-East.HokurikuShinkansen.Ueno",
        "railway": "JR-East"
    },
    {
        "name": "上野",
        "id": "odpt.Station:JR-East.JoetsuShinkansen.Ueno",
        "railway": "JR-East"
    },
    {
        "name": "上野",
        "id": "odpt.Station:JR-East.TohokuShinkansen.Ueno",
        "railway": "JR-East"
    },
    {
        "name": "上野",
        "id": "odpt.Station:JR-East.YamagataShinkansen.Ueno",
        "railway": "JR-East"
    },
    {
        "name": "上野",
        "id": "odpt.Station:TokyoMetro.Ginza.Ueno",
        "railway": "TokyoMetro"
    },
    {
        "name": "上野",
        "id": "odpt.Station:TokyoMetro.Hibiya.Ueno",
        "railway": "TokyoMetro"
    },
    {
        "name": "上野広小路",
        "id": "odpt.Station:TokyoMetro.Ginza.UenoHirokoji",
        "railway": "TokyoMetro"
    },
    {
        "name": "上野御徒町",
        "id": "odpt.Station:Toei.Oedo.UenoOkachimachi",
        "railway": "Toei"
    },
    {
        "name": "下永谷",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Shimonagaya",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "下飯田",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Shimoiida",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "両国",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Ryogoku",
        "railway": "JR-East"
    },
    {
        "name": "両国",
        "id": "odpt.Station:Toei.Oedo.Ryogoku",
        "railway": "Toei"
    },
    {
        "name": "中井",
        "id": "odpt.Station:Seibu.Shinjuku.Nakai",
        "railway": "Seibu"
    },
    {
        "name": "中井",
        "id": "odpt.Station:Toei.Oedo.Nakai",
        "railway": "Toei"
    },
    {
        "name": "中央大学・明星大学",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.ChuoDaigakuMeiseiDaigaku",
        "railway": "TamaMonorail"
    },
    {
        "name": "中央林間",
        "id": "odpt.Station:Tokyu.DenEnToshi.ChuoRinkan",
        "railway": "Tokyu"
    },
    {
        "name": "中山",
        "id": "odpt.Station:JR-East.Yokohama.Nakayama",
        "railway": "JR-East"
    },
    {
        "name": "中山",
        "id": "odpt.Station:YokohamaMunicipal.Green.Nakayama",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "中川",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Nakagawa",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "中延",
        "id": "odpt.Station:Tokyu.Oimachi.Nakanobu",
        "railway": "Tokyu"
    },
    {
        "name": "中延",
        "id": "odpt.Station:Toei.Asakusa.Nakanobu",
        "railway": "Toei"
    },
    {
        "name": "中田",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Nakada",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "中目黒",
        "id": "odpt.Station:TokyoMetro.Hibiya.NakaMeguro",
        "railway": "TokyoMetro"
    },
    {
        "name": "中目黒",
        "id": "odpt.Station:Tokyu.Toyoko.NakaMeguro",
        "railway": "Tokyu"
    },
    {
        "name": "中野",
        "id": "odpt.Station:JR-East.ChuoRapid.Nakano",
        "railway": "JR-East"
    },
    {
        "name": "中野",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Nakano",
        "railway": "JR-East"
    },
    {
        "name": "中野",
        "id": "odpt.Station:TokyoMetro.Tozai.Nakano",
        "railway": "TokyoMetro"
    },
    {
        "name": "中野坂上",
        "id": "odpt.Station:TokyoMetro.Marunouchi.NakanoSakaue",
        "railway": "TokyoMetro"
    },
    {
        "name": "中野坂上",
        "id": "odpt.Station:TokyoMetro.MarunouchiBranch.NakanoSakaue",
        "railway": "TokyoMetro"
    },
    {
        "name": "中野坂上",
        "id": "odpt.Station:Toei.Oedo.NakanoSakaue",
        "railway": "Toei"
    },
    {
        "name": "中野富士見町",
        "id": "odpt.Station:TokyoMetro.MarunouchiBranch.NakanoFujimicho",
        "railway": "TokyoMetro"
    },
    {
        "name": "中野新橋",
        "id": "odpt.Station:TokyoMetro.MarunouchiBranch.NakanoShimbashi",
        "railway": "TokyoMetro"
    },
    {
        "name": "乃木坂",
        "id": "odpt.Station:TokyoMetro.Chiyoda.Nogizaka",
        "railway": "TokyoMetro"
    },
    {
        "name": "久喜",
        "id": "odpt.Station:Tobu.Isesaki.Kuki",
        "railway": "Tobu"
    },
    {
        "name": "九段下",
        "id": "odpt.Station:TokyoMetro.Hanzomon.Kudanshita",
        "railway": "TokyoMetro"
    },
    {
        "name": "九段下",
        "id": "odpt.Station:TokyoMetro.Tozai.Kudanshita",
        "railway": "TokyoMetro"
    },
    {
        "name": "九段下",
        "id": "odpt.Station:Toei.Shinjuku.Kudanshita",
        "railway": "Toei"
    },
    {
        "name": "二俣川",
        "id": "odpt.Station:Sotetsu.Main.Futamatagawa",
        "railway": "Sotetsu"
    },
    {
        "name": "二子玉川",
        "id": "odpt.Station:Tokyu.DenEnToshi.FutakoTamagawa",
        "railway": "Tokyu"
    },
    {
        "name": "二重橋前〈丸の内〉",
        "id": "odpt.Station:TokyoMetro.Chiyoda.Nijubashimae",
        "railway": "TokyoMetro"
    },
    {
        "name": "五反田",
        "id": "odpt.Station:JR-East.Yamanote.Gotanda",
        "railway": "JR-East"
    },
    {
        "name": "五反田",
        "id": "odpt.Station:Tokyu.Ikegami.Gotanda",
        "railway": "Tokyu"
    },
    {
        "name": "五反田",
        "id": "odpt.Station:Toei.Asakusa.Gotanda",
        "railway": "Toei"
    },
    {
        "name": "京急久里浜",
        "id": "odpt.Station:Keikyu.Kurihama.KeikyuKurihama",
        "railway": "Keikyu"
    },
    {
        "name": "京急川崎",
        "id": "odpt.Station:Keikyu.Main.KeikyuKawasaki",
        "railway": "Keikyu"
    },
    {
        "name": "京急蒲田",
        "id": "odpt.Station:Keikyu.Main.KeikyuKamata",
        "railway": "Keikyu"
    },
    {
        "name": "京成上野",
        "id": "odpt.Station:Keisei.Main.KeiseiUeno",
        "railway": "Keisei"
    },
    {
        "name": "京成佐倉",
        "id": "odpt.Station:Keisei.Main.KeiseiSakura",
        "railway": "Keisei"
    },
    {
        "name": "京成八幡",
        "id": "odpt.Station:Keisei.Main.KeiseiYawata",
        "railway": "Keisei"
    },
    {
        "name": "京成成田",
        "id": "odpt.Station:Keisei.Main.KeiseiNarita",
        "railway": "Keisei"
    },
    {
        "name": "京成西船",
        "id": "odpt.Station:Keisei.Main.KeiseiNishifuna",
        "railway": "Keisei"
    },
    {
        "name": "京成高砂",
        "id": "odpt.Station:Keisei.Main.KeiseiTakasago",
        "railway": "Keisei"
    },
    {
        "name": "京橋",
        "id": "odpt.Station:TokyoMetro.Ginza.Kyobashi",
        "railway": "TokyoMetro"
    },
    {
        "name": "京王八王子",
        "id": "odpt.Station:Keio.Keio.KeioHachioji",
        "railway": "Keio"
    },
    {
        "name": "京王多摩センター",
        "id": "odpt.Station:Keio.Sagamihara.KeioTamaCenter",
        "railway": "Keio"
    },
    {
        "name": "人形町",
        "id": "odpt.Station:TokyoMetro.Hibiya.Ningyocho",
        "railway": "TokyoMetro"
    },
    {
        "name": "人形町",
        "id": "odpt.Station:Toei.Asakusa.Ningyocho",
        "railway": "Toei"
    },
    {
        "name": "代々木",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Yoyogi",
        "railway": "JR-East"
    },
    {
        "name": "代々木",
        "id": "odpt.Station:JR-East.Yamanote.Yoyogi",
        "railway": "JR-East"
    },
    {
        "name": "代々木",
        "id": "odpt.Station:Toei.Oedo.Yoyogi",
        "railway": "Toei"
    },
    {
        "name": "代々木上原",
        "id": "odpt.Station:Odakyu.Odawara.YoyogiUehara",
        "railway": "Odakyu"
    },
    {
        "name": "代々木上原",
        "id": "odpt.Station:TokyoMetro.Chiyoda.YoyogiUehara",
        "railway": "TokyoMetro"
    },
    {
        "name": "代々木公園",
        "id": "odpt.Station:TokyoMetro.Chiyoda.YoyogiKoen",
        "railway": "TokyoMetro"
    },
    {
        "name": "仲御徒町",
        "id": "odpt.Station:TokyoMetro.Hibiya.NakaOkachimachi",
        "railway": "TokyoMetro"
    },
    {
        "name": "仲町台",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Nakamachidai",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "伊勢佐木長者町",
        "id": "odpt.Station:YokohamaMunicipal.Blue.IsezakiChojamachi",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "伊勢原",
        "id": "odpt.Station:Odakyu.Odawara.Isehara",
        "railway": "Odakyu"
    },
    {
        "name": "住吉",
        "id": "odpt.Station:TokyoMetro.Hanzomon.Sumiyoshi",
        "railway": "TokyoMetro"
    },
    {
        "name": "住吉",
        "id": "odpt.Station:Toei.Shinjuku.Sumiyoshi",
        "railway": "Toei"
    },
    {
        "name": "保谷",
        "id": "odpt.Station:Seibu.Ikebukuro.Hoya",
        "railway": "Seibu"
    },
    {
        "name": "元住吉",
        "id": "odpt.Station:Tokyu.Meguro.Motosumiyoshi",
        "railway": "Tokyu"
    },
    {
        "name": "元住吉",
        "id": "odpt.Station:Tokyu.Toyoko.Motosumiyoshi",
        "railway": "Tokyu"
    },
    {
        "name": "元町・中華街",
        "id": "odpt.Station:Minatomirai.Minatomirai.MotomachiChukagai",
        "railway": "Minatomirai"
    },
    {
        "name": "光が丘",
        "id": "odpt.Station:Toei.Oedo.Hikarigaoka",
        "railway": "Toei"
    },
    {
        "name": "入谷",
        "id": "odpt.Station:TokyoMetro.Hibiya.Iriya",
        "railway": "TokyoMetro"
    },
    {
        "name": "八丁堀",
        "id": "odpt.Station:JR-East.Keiyo.Hatchobori",
        "railway": "JR-East"
    },
    {
        "name": "八丁堀",
        "id": "odpt.Station:TokyoMetro.Hibiya.Hatchobori",
        "railway": "TokyoMetro"
    },
    {
        "name": "八千代緑が丘",
        "id": "odpt.Station:ToyoRapid.ToyoRapid.YachiyoMidorigaoka",
        "railway": "ToyoRapid"
    },
    {
        "name": "八幡山",
        "id": "odpt.Station:Keio.Keio.HachimanYama",
        "railway": "Keio"
    },
    {
        "name": "八潮",
        "id": "odpt.Station:MIR.TsukubaExpress.Yashio",
        "railway": "MIR"
    },
    {
        "name": "六本木",
        "id": "odpt.Station:TokyoMetro.Hibiya.Roppongi",
        "railway": "TokyoMetro"
    },
    {
        "name": "六本木",
        "id": "odpt.Station:Toei.Oedo.Roppongi",
        "railway": "Toei"
    },
    {
        "name": "六本木一丁目",
        "id": "odpt.Station:TokyoMetro.Namboku.RoppongiItchome",
        "railway": "TokyoMetro"
    },
    {
        "name": "六町",
        "id": "odpt.Station:MIR.TsukubaExpress.Rokucho",
        "railway": "MIR"
    },
    {
        "name": "内幸町",
        "id": "odpt.Station:Toei.Mita.Uchisaiwaicho",
        "railway": "Toei"
    },
    {
        "name": "勝どき",
        "id": "odpt.Station:Toei.Oedo.Kachidoki",
        "railway": "Toei"
    },
    {
        "name": "北千住",
        "id": "odpt.Station:JR-East.JobanRapid.KitaSenju",
        "railway": "JR-East"
    },
    {
        "name": "北千住",
        "id": "odpt.Station:MIR.TsukubaExpress.KitaSenju",
        "railway": "MIR"
    },
    {
        "name": "北千住",
        "id": "odpt.Station:Tobu.TobuSkytree.KitaSenju",
        "railway": "Tobu"
    },
    {
        "name": "北千住",
        "id": "odpt.Station:TokyoMetro.Chiyoda.KitaSenju",
        "railway": "TokyoMetro"
    },
    {
        "name": "北千住",
        "id": "odpt.Station:TokyoMetro.Hibiya.KitaSenju",
        "railway": "TokyoMetro"
    },
    {
        "name": "北参道",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.KitaSando",
        "railway": "TokyoMetro"
    },
    {
        "name": "北山田",
        "id": "odpt.Station:YokohamaMunicipal.Green.KitaYamata",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "北新横浜",
        "id": "odpt.Station:YokohamaMunicipal.Blue.KitaShinYokohama",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "北春日部",
        "id": "odpt.Station:Tobu.TobuSkytree.KitaKasukabe",
        "railway": "Tobu"
    },
    {
        "name": "北綾瀬",
        "id": "odpt.Station:TokyoMetro.Chiyoda.KitaAyase",
        "railway": "TokyoMetro"
    },
    {
        "name": "北越谷",
        "id": "odpt.Station:Tobu.TobuSkytree.KitaKoshigaya",
        "railway": "Tobu"
    },
    {
        "name": "千川",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.Senkawa",
        "railway": "TokyoMetro"
    },
    {
        "name": "千川",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Senkawa",
        "railway": "TokyoMetro"
    },
    {
        "name": "千石",
        "id": "odpt.Station:Toei.Mita.Sengoku",
        "railway": "Toei"
    },
    {
        "name": "千駄木",
        "id": "odpt.Station:TokyoMetro.Chiyoda.Sendagi",
        "railway": "TokyoMetro"
    },
    {
        "name": "半蔵門",
        "id": "odpt.Station:TokyoMetro.Hanzomon.Hanzomon",
        "railway": "TokyoMetro"
    },
    {
        "name": "南千住",
        "id": "odpt.Station:JR-East.JobanRapid.MinamiSenju",
        "railway": "JR-East"
    },
    {
        "name": "南千住",
        "id": "odpt.Station:MIR.TsukubaExpress.MinamiSenju",
        "railway": "MIR"
    },
    {
        "name": "南千住",
        "id": "odpt.Station:TokyoMetro.Hibiya.MinamiSenju",
        "railway": "TokyoMetro"
    },
    {
        "name": "南栗橋",
        "id": "odpt.Station:Tobu.Nikko.MinamiKurihashi",
        "railway": "Tobu"
    },
    {
        "name": "南流山",
        "id": "odpt.Station:JR-East.Musashino.MinamiNagareyama",
        "railway": "JR-East"
    },
    {
        "name": "南流山",
        "id": "odpt.Station:MIR.TsukubaExpress.MinamiNagareyama",
        "railway": "MIR"
    },
    {
        "name": "南砂町",
        "id": "odpt.Station:TokyoMetro.Tozai.MinamiSunamachi",
        "railway": "TokyoMetro"
    },
    {
        "name": "南行徳",
        "id": "odpt.Station:TokyoMetro.Tozai.MinamiGyotoku",
        "railway": "TokyoMetro"
    },
    {
        "name": "南阿佐ケ谷",
        "id": "odpt.Station:TokyoMetro.Marunouchi.MinamiAsagaya",
        "railway": "TokyoMetro"
    },
    {
        "name": "印旛日本医大",
        "id": "odpt.Station:Hokuso.Hokuso.ImbaNihonIdai",
        "railway": "Hokuso"
    },
    {
        "name": "印西牧の原",
        "id": "odpt.Station:Hokuso.Hokuso.InzaiMakinohara",
        "railway": "Hokuso"
    },
    {
        "name": "原宿",
        "id": "odpt.Station:JR-East.Yamanote.Harajuku",
        "railway": "JR-East"
    },
    {
        "name": "原木中山",
        "id": "odpt.Station:TokyoMetro.Tozai.BarakiNakayama",
        "railway": "TokyoMetro"
    },
    {
        "name": "取手",
        "id": "odpt.Station:JR-East.JobanLocal.Toride",
        "railway": "JR-East"
    },
    {
        "name": "台場",
        "id": "odpt.Station:Yurikamome.Yurikamome.Daiba",
        "railway": "Yurikamome"
    },
    {
        "name": "吉祥寺",
        "id": "odpt.Station:JR-East.ChuoRapid.Kichijoji",
        "railway": "JR-East"
    },
    {
        "name": "吉祥寺",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Kichijoji",
        "railway": "JR-East"
    },
    {
        "name": "吉祥寺",
        "id": "odpt.Station:Keio.Inokashira.Kichijoji",
        "railway": "Keio"
    },
    {
        "name": "吉野町",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Yoshinocho",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "向ヶ丘遊園",
        "id": "odpt.Station:Odakyu.Odawara.MukogaokaYuen",
        "railway": "Odakyu"
    },
    {
        "name": "向原",
        "id": "odpt.Station:Toei.Arakawa.Mukohara",
        "railway": "Toei"
    },
    {
        "name": "和光市",
        "id": "odpt.Station:Tobu.Tojo.Wakoshi",
        "railway": "Tobu"
    },
    {
        "name": "和光市",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.Wakoshi",
        "railway": "TokyoMetro"
    },
    {
        "name": "和光市",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Wakoshi",
        "railway": "TokyoMetro"
    },
    {
        "name": "品川",
        "id": "odpt.Station:Keikyu.Main.Shinagawa",
        "railway": "Keikyu"
    },
    {
        "name": "品川シーサイド",
        "id": "odpt.Station:TWR.Rinkai.ShinagawaSeaside",
        "railway": "TWR"
    },
    {
        "name": "唐木田",
        "id": "odpt.Station:Odakyu.Tama.Karakida",
        "railway": "Odakyu"
    },
    {
        "name": "四ツ谷",
        "id": "odpt.Station:JR-East.ChuoRapid.Yotsuya",
        "railway": "JR-East"
    },
    {
        "name": "四ツ谷",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Yotsuya",
        "railway": "JR-East"
    },
    {
        "name": "四ツ谷",
        "id": "odpt.Station:TokyoMetro.Marunouchi.Yotsuya",
        "railway": "TokyoMetro"
    },
    {
        "name": "四ツ谷",
        "id": "odpt.Station:TokyoMetro.Namboku.Yotsuya",
        "railway": "TokyoMetro"
    },
    {
        "name": "四谷三丁目",
        "id": "odpt.Station:TokyoMetro.Marunouchi.YotsuyaSanchome",
        "railway": "TokyoMetro"
    },
    {
        "name": "国会議事堂前",
        "id": "odpt.Station:TokyoMetro.Chiyoda.KokkaiGijidomae",
        "railway": "TokyoMetro"
    },
    {
        "name": "国会議事堂前",
        "id": "odpt.Station:TokyoMetro.Marunouchi.KokkaiGijidomae",
        "railway": "TokyoMetro"
    },
    {
        "name": "国立競技場",
        "id": "odpt.Station:Toei.Oedo.KokuritsuKyogijo",
        "railway": "Toei"
    },
    {
        "name": "国際展示場",
        "id": "odpt.Station:TWR.Rinkai.KokusaiTenjijo",
        "railway": "TWR"
    },
    {
        "name": "地下鉄成増",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.ChikatetsuNarimasu",
        "railway": "TokyoMetro"
    },
    {
        "name": "地下鉄成増",
        "id": "odpt.Station:TokyoMetro.Yurakucho.ChikatetsuNarimasu",
        "railway": "TokyoMetro"
    },
    {
        "name": "地下鉄赤塚",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.ChikatetsuAkatsuka",
        "railway": "TokyoMetro"
    },
    {
        "name": "地下鉄赤塚",
        "id": "odpt.Station:TokyoMetro.Yurakucho.ChikatetsuAkatsuka",
        "railway": "TokyoMetro"
    },
    {
        "name": "外苑前",
        "id": "odpt.Station:TokyoMetro.Ginza.Gaiemmae",
        "railway": "TokyoMetro"
    },
    {
        "name": "多摩センター",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.TamaCenter",
        "railway": "TamaMonorail"
    },
    {
        "name": "多摩動物公園",
        "id": "odpt.Station:Keio.Dobutsuen.TamaDobutsukoen",
        "railway": "Keio"
    },
    {
        "name": "多摩動物公園",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.TamaDobutsukoen",
        "railway": "TamaMonorail"
    },
    {
        "name": "大井町",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Oimachi",
        "railway": "JR-East"
    },
    {
        "name": "大井町",
        "id": "odpt.Station:TWR.Rinkai.Oimachi",
        "railway": "TWR"
    },
    {
        "name": "大井町",
        "id": "odpt.Station:Tokyu.Oimachi.Oimachi",
        "railway": "Tokyu"
    },
    {
        "name": "大和",
        "id": "odpt.Station:Sotetsu.Main.Yamato",
        "railway": "Sotetsu"
    },
    {
        "name": "大塚",
        "id": "odpt.Station:JR-East.Yamanote.Otsuka",
        "railway": "JR-East"
    },
    {
        "name": "大塚・帝京大学",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.OtsukaTeikyoDaigaku",
        "railway": "TamaMonorail"
    },
    {
        "name": "大塚駅前",
        "id": "odpt.Station:Toei.Arakawa.OtsukaEkimae",
        "railway": "Toei"
    },
    {
        "name": "大宮",
        "id": "odpt.Station:JR-East.SaikyoKawagoe.Omiya",
        "railway": "JR-East"
    },
    {
        "name": "大岡山",
        "id": "odpt.Station:Tokyu.Meguro.Ookayama",
        "railway": "Tokyu"
    },
    {
        "name": "大島",
        "id": "odpt.Station:Toei.Shinjuku.Ojima",
        "railway": "Toei"
    },
    {
        "name": "大崎",
        "id": "odpt.Station:JR-East.SaikyoKawagoe.Osaki",
        "railway": "JR-East"
    },
    {
        "name": "大崎",
        "id": "odpt.Station:JR-East.ShonanShinjuku.Osaki",
        "railway": "JR-East"
    },
    {
        "name": "大崎",
        "id": "odpt.Station:JR-East.SotetsuDirect.Osaki",
        "railway": "JR-East"
    },
    {
        "name": "大崎",
        "id": "odpt.Station:JR-East.Yamanote.Osaki",
        "railway": "JR-East"
    },
    {
        "name": "大崎",
        "id": "odpt.Station:TWR.Rinkai.Osaki",
        "railway": "TWR"
    },
    {
        "name": "大手町",
        "id": "odpt.Station:TokyoMetro.Chiyoda.Otemachi",
        "railway": "TokyoMetro"
    },
    {
        "name": "大手町",
        "id": "odpt.Station:TokyoMetro.Hanzomon.Otemachi",
        "railway": "TokyoMetro"
    },
    {
        "name": "大手町",
        "id": "odpt.Station:TokyoMetro.Marunouchi.Otemachi",
        "railway": "TokyoMetro"
    },
    {
        "name": "大手町",
        "id": "odpt.Station:TokyoMetro.Tozai.Otemachi",
        "railway": "TokyoMetro"
    },
    {
        "name": "大手町",
        "id": "odpt.Station:Toei.Mita.Otemachi",
        "railway": "Toei"
    },
    {
        "name": "大門",
        "id": "odpt.Station:Toei.Asakusa.Daimon",
        "railway": "Toei"
    },
    {
        "name": "大門",
        "id": "odpt.Station:Toei.Oedo.Daimon",
        "railway": "Toei"
    },
    {
        "name": "天王洲アイル",
        "id": "odpt.Station:TWR.Rinkai.TennozuIsle",
        "railway": "TWR"
    },
    {
        "name": "天王洲アイル",
        "id": "odpt.Station:TokyoMonorail.HanedaAirport.TennozuIsle",
        "railway": "TokyoMonorail"
    },
    {
        "name": "奥沢",
        "id": "odpt.Station:Tokyu.Meguro.Okusawa",
        "railway": "Tokyu"
    },
    {
        "name": "妙典",
        "id": "odpt.Station:TokyoMetro.Tozai.Myoden",
        "railway": "TokyoMetro"
    },
    {
        "name": "学習院下",
        "id": "odpt.Station:Toei.Arakawa.Gakushuinshita",
        "railway": "Toei"
    },
    {
        "name": "守谷",
        "id": "odpt.Station:MIR.TsukubaExpress.Moriya",
        "railway": "MIR"
    },
    {
        "name": "守谷",
        "id": "odpt.Station:KantoRailway.Joso.Moriya",
        "railway": "KantoRailway"
    },
    {
        "name": "宗吾参道",
        "id": "odpt.Station:Keisei.Main.Sogosando",
        "railway": "Keisei"
    },
    {
        "name": "宝町",
        "id": "odpt.Station:Toei.Asakusa.Takaracho",
        "railway": "Toei"
    },
    {
        "name": "宮ノ前",
        "id": "odpt.Station:Toei.Arakawa.Miyanomae",
        "railway": "Toei"
    },
    {
        "name": "小伝馬町",
        "id": "odpt.Station:TokyoMetro.Hibiya.Kodemmacho",
        "railway": "TokyoMetro"
    },
    {
        "name": "小台",
        "id": "odpt.Station:Toei.Arakawa.Odai",
        "railway": "Toei"
    },
    {
        "name": "小川町",
        "id": "odpt.Station:Tobu.Tojo.Ogawamachi",
        "railway": "Tobu"
    },
    {
        "name": "小川町",
        "id": "odpt.Station:Toei.Shinjuku.Ogawamachi",
        "railway": "Toei"
    },
    {
        "name": "小手指",
        "id": "odpt.Station:Seibu.Ikebukuro.Kotesashi",
        "railway": "Seibu"
    },
    {
        "name": "小田急多摩センター",
        "id": "odpt.Station:Odakyu.Tama.OdakyuTamaCenter",
        "railway": "Odakyu"
    },
    {
        "name": "小竹向原",
        "id": "odpt.Station:Seibu.SeibuYurakucho.KotakeMukaihara",
        "railway": "Seibu"
    },
    {
        "name": "小竹向原",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.KotakeMukaihara",
        "railway": "TokyoMetro"
    },
    {
        "name": "小竹向原",
        "id": "odpt.Station:TokyoMetro.Yurakucho.KotakeMukaihara",
        "railway": "TokyoMetro"
    },
    {
        "name": "岩本町",
        "id": "odpt.Station:Toei.Shinjuku.Iwamotocho",
        "railway": "Toei"
    },
    {
        "name": "岸根公園",
        "id": "odpt.Station:YokohamaMunicipal.Blue.KishineKoen",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "川和町",
        "id": "odpt.Station:YokohamaMunicipal.Green.Kawawacho",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "川越",
        "id": "odpt.Station:JR-East.SaikyoKawagoe.Kawagoe",
        "railway": "JR-East"
    },
    {
        "name": "川越市",
        "id": "odpt.Station:Tobu.Tojo.Kawagoeshi",
        "railway": "Tobu"
    },
    {
        "name": "巣鴨",
        "id": "odpt.Station:JR-East.Yamanote.Sugamo",
        "railway": "JR-East"
    },
    {
        "name": "巣鴨",
        "id": "odpt.Station:Toei.Mita.Sugamo",
        "railway": "Toei"
    },
    {
        "name": "巣鴨新田",
        "id": "odpt.Station:Toei.Arakawa.Sugamoshinden",
        "railway": "Toei"
    },
    {
        "name": "市ケ谷",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Ichigaya",
        "railway": "JR-East"
    },
    {
        "name": "市ケ谷",
        "id": "odpt.Station:TokyoMetro.Namboku.Ichigaya",
        "railway": "TokyoMetro"
    },
    {
        "name": "市ケ谷",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Ichigaya",
        "railway": "TokyoMetro"
    },
    {
        "name": "市ヶ谷",
        "id": "odpt.Station:Toei.Shinjuku.Ichigaya",
        "railway": "Toei"
    },
    {
        "name": "市場前",
        "id": "odpt.Station:Yurikamome.Yurikamome.ShijoMae",
        "railway": "Yurikamome"
    },
    {
        "name": "平和台",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.Heiwadai",
        "railway": "TokyoMetro"
    },
    {
        "name": "平和台",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Heiwadai",
        "railway": "TokyoMetro"
    },
    {
        "name": "広尾",
        "id": "odpt.Station:TokyoMetro.Hibiya.HiroO",
        "railway": "TokyoMetro"
    },
    {
        "name": "庚申塚",
        "id": "odpt.Station:Toei.Arakawa.Koshinzuka",
        "railway": "Toei"
    },
    {
        "name": "府中競馬正門前",
        "id": "odpt.Station:Keio.Keibajo.FuchukeibaSeimommae",
        "railway": "Keio"
    },
    {
        "name": "弘明寺",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Gumyoji",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "後楽園",
        "id": "odpt.Station:TokyoMetro.Marunouchi.Korakuen",
        "railway": "TokyoMetro"
    },
    {
        "name": "後楽園",
        "id": "odpt.Station:TokyoMetro.Namboku.Korakuen",
        "railway": "TokyoMetro"
    },
    {
        "name": "御徒町",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Okachimachi",
        "railway": "JR-East"
    },
    {
        "name": "御徒町",
        "id": "odpt.Station:JR-East.Yamanote.Okachimachi",
        "railway": "JR-East"
    },
    {
        "name": "御成門",
        "id": "odpt.Station:Toei.Mita.Onarimon",
        "railway": "Toei"
    },
    {
        "name": "御茶ノ水",
        "id": "odpt.Station:JR-East.ChuoRapid.Ochanomizu",
        "railway": "JR-East"
    },
    {
        "name": "御茶ノ水",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Ochanomizu",
        "railway": "JR-East"
    },
    {
        "name": "御茶ノ水",
        "id": "odpt.Station:TokyoMetro.Marunouchi.Ochanomizu",
        "railway": "TokyoMetro"
    },
    {
        "name": "志木",
        "id": "odpt.Station:Tobu.Tojo.Shiki",
        "railway": "Tobu"
    },
    {
        "name": "志村三丁目",
        "id": "odpt.Station:Toei.Mita.ShimuraSanchome",
        "railway": "Toei"
    },
    {
        "name": "志村坂上",
        "id": "odpt.Station:Toei.Mita.ShimuraSakaue",
        "railway": "Toei"
    },
    {
        "name": "志茂",
        "id": "odpt.Station:TokyoMetro.Namboku.Shimo",
        "railway": "TokyoMetro"
    },
    {
        "name": "恵比寿",
        "id": "odpt.Station:JR-East.SaikyoKawagoe.Ebisu",
        "railway": "JR-East"
    },
    {
        "name": "恵比寿",
        "id": "odpt.Station:JR-East.ShonanShinjuku.Ebisu",
        "railway": "JR-East"
    },
    {
        "name": "恵比寿",
        "id": "odpt.Station:JR-East.Yamanote.Ebisu",
        "railway": "JR-East"
    },
    {
        "name": "恵比寿",
        "id": "odpt.Station:TokyoMetro.Hibiya.Ebisu",
        "railway": "TokyoMetro"
    },
    {
        "name": "成城学園前",
        "id": "odpt.Station:Odakyu.Odawara.SeijogakuenMae",
        "railway": "Odakyu"
    },
    {
        "name": "成田空港",
        "id": "odpt.Station:Keisei.Main.NaritaAirportTerminal1",
        "railway": "Keisei"
    },
    {
        "name": "成田空港",
        "id": "odpt.Station:Keisei.NaritaSkyAccess.NaritaAirportTerminal1",
        "railway": "Keisei"
    },
    {
        "name": "我孫子",
        "id": "odpt.Station:JR-East.JobanLocal.Abiko",
        "railway": "JR-East"
    },
    {
        "name": "戸塚",
        "id": "odpt.Station:JR-East.ShonanShinjuku.Totsuka",
        "railway": "JR-East"
    },
    {
        "name": "戸塚",
        "id": "odpt.Station:JR-East.Tokaido.Totsuka",
        "railway": "JR-East"
    },
    {
        "name": "戸塚",
        "id": "odpt.Station:JR-East.Yokosuka.Totsuka",
        "railway": "JR-East"
    },
    {
        "name": "戸塚",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Totsuka",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "戸越",
        "id": "odpt.Station:Toei.Asakusa.Togoshi",
        "railway": "Toei"
    },
    {
        "name": "戸越銀座",
        "id": "odpt.Station:Tokyu.Ikegami.TogoshiGinza",
        "railway": "Tokyu"
    },
    {
        "name": "所沢",
        "id": "odpt.Station:Seibu.Ikebukuro.Tokorozawa",
        "railway": "Seibu"
    },
    {
        "name": "扇大橋",
        "id": "odpt.Station:Toei.NipporiToneri.OgiOhashi",
        "railway": "Toei"
    },
    {
        "name": "押上",
        "id": "odpt.Station:Keisei.Oshiage.Oshiage",
        "railway": "Keisei"
    },
    {
        "name": "押上",
        "id": "odpt.Station:Tobu.TobuSkytreeBranch.Oshiage",
        "railway": "Tobu"
    },
    {
        "name": "押上",
        "id": "odpt.Station:Toei.Asakusa.Oshiage",
        "railway": "Toei"
    },
    {
        "name": "押上〈スカイツリー前〉",
        "id": "odpt.Station:TokyoMetro.Hanzomon.Oshiage",
        "railway": "TokyoMetro"
    },
    {
        "name": "指扇",
        "id": "odpt.Station:JR-East.SaikyoKawagoe.Sashiogi",
        "railway": "JR-East"
    },
    {
        "name": "新中野",
        "id": "odpt.Station:TokyoMetro.Marunouchi.ShinNakano",
        "railway": "TokyoMetro"
    },
    {
        "name": "新大塚",
        "id": "odpt.Station:TokyoMetro.Marunouchi.ShinOtsuka",
        "railway": "TokyoMetro"
    },
    {
        "name": "新宿",
        "id": "odpt.Station:JR-East.ChuoRapid.Shinjuku",
        "railway": "JR-East"
    },
    {
        "name": "新宿",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Shinjuku",
        "railway": "JR-East"
    },
    {
        "name": "新宿",
        "id": "odpt.Station:JR-East.SaikyoKawagoe.Shinjuku",
        "railway": "JR-East"
    },
    {
        "name": "新宿",
        "id": "odpt.Station:JR-East.ShonanShinjuku.Shinjuku",
        "railway": "JR-East"
    },
    {
        "name": "新宿",
        "id": "odpt.Station:JR-East.Yamanote.Shinjuku",
        "railway": "JR-East"
    },
    {
        "name": "新宿",
        "id": "odpt.Station:Keio.Keio.Shinjuku",
        "railway": "Keio"
    },
    {
        "name": "新宿",
        "id": "odpt.Station:Keio.KeioNew.Shinjuku",
        "railway": "Keio"
    },
    {
        "name": "新宿",
        "id": "odpt.Station:Odakyu.Odawara.Shinjuku",
        "railway": "Odakyu"
    },
    {
        "name": "新宿",
        "id": "odpt.Station:TokyoMetro.Marunouchi.Shinjuku",
        "railway": "TokyoMetro"
    },
    {
        "name": "新宿",
        "id": "odpt.Station:Toei.Oedo.Shinjuku",
        "railway": "Toei"
    },
    {
        "name": "新宿",
        "id": "odpt.Station:Toei.Shinjuku.Shinjuku",
        "railway": "Toei"
    },
    {
        "name": "新宿三丁目",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.ShinjukuSanchome",
        "railway": "TokyoMetro"
    },
    {
        "name": "新宿三丁目",
        "id": "odpt.Station:TokyoMetro.Marunouchi.ShinjukuSanchome",
        "railway": "TokyoMetro"
    },
    {
        "name": "新宿三丁目",
        "id": "odpt.Station:Toei.Shinjuku.ShinjukuSanchome",
        "railway": "Toei"
    },
    {
        "name": "新宿御苑前",
        "id": "odpt.Station:TokyoMetro.Marunouchi.ShinjukuGyoemmae",
        "railway": "TokyoMetro"
    },
    {
        "name": "新宿西口",
        "id": "odpt.Station:Toei.Oedo.ShinjukuNishiguchi",
        "railway": "Toei"
    },
    {
        "name": "新富町",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Shintomicho",
        "railway": "TokyoMetro"
    },
    {
        "name": "新庚申塚",
        "id": "odpt.Station:Toei.Arakawa.ShinKoshinzuka",
        "railway": "Toei"
    },
    {
        "name": "新御徒町",
        "id": "odpt.Station:MIR.TsukubaExpress.ShinOkachimachi",
        "railway": "MIR"
    },
    {
        "name": "新御徒町",
        "id": "odpt.Station:Toei.Oedo.ShinOkachimachi",
        "railway": "Toei"
    },
    {
        "name": "新御茶ノ水",
        "id": "odpt.Station:TokyoMetro.Chiyoda.ShinOchanomizu",
        "railway": "TokyoMetro"
    },
    {
        "name": "新日本橋",
        "id": "odpt.Station:JR-East.SobuRapid.ShinNihombashi",
        "railway": "JR-East"
    },
    {
        "name": "新木場",
        "id": "odpt.Station:JR-East.Keiyo.ShinKiba",
        "railway": "JR-East"
    },
    {
        "name": "新木場",
        "id": "odpt.Station:TWR.Rinkai.ShinKiba",
        "railway": "TWR"
    },
    {
        "name": "新木場",
        "id": "odpt.Station:TokyoMetro.Yurakucho.ShinKiba",
        "railway": "TokyoMetro"
    },
    {
        "name": "新板橋",
        "id": "odpt.Station:Toei.Mita.ShinItabashi",
        "railway": "Toei"
    },
    {
        "name": "新横浜",
        "id": "odpt.Station:JR-Central.TokaidoShinkansen.ShinYokohama",
        "railway": "JR-Central"
    },
    {
        "name": "新横浜",
        "id": "odpt.Station:JR-East.Yokohama.ShinYokohama",
        "railway": "JR-East"
    },
    {
        "name": "新横浜",
        "id": "odpt.Station:Sotetsu.SotetsuShinYokohama.ShinYokohama",
        "railway": "Sotetsu"
    },
    {
        "name": "新横浜",
        "id": "odpt.Station:Tokyu.TokyuShinYokohama.ShinYokohama",
        "railway": "Tokyu"
    },
    {
        "name": "新横浜",
        "id": "odpt.Station:YokohamaMunicipal.Blue.ShinYokohama",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "新橋",
        "id": "odpt.Station:JR-East.JobanRapid.Shimbashi",
        "railway": "JR-East"
    },
    {
        "name": "新橋",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Shimbashi",
        "railway": "JR-East"
    },
    {
        "name": "新橋",
        "id": "odpt.Station:JR-East.Tokaido.Shimbashi",
        "railway": "JR-East"
    },
    {
        "name": "新橋",
        "id": "odpt.Station:JR-East.Yamanote.Shimbashi",
        "railway": "JR-East"
    },
    {
        "name": "新橋",
        "id": "odpt.Station:JR-East.Yokosuka.Shimbashi",
        "railway": "JR-East"
    },
    {
        "name": "新橋",
        "id": "odpt.Station:TokyoMetro.Ginza.Shimbashi",
        "railway": "TokyoMetro"
    },
    {
        "name": "新橋",
        "id": "odpt.Station:Toei.Asakusa.Shimbashi",
        "railway": "Toei"
    },
    {
        "name": "新橋",
        "id": "odpt.Station:Yurikamome.Yurikamome.Shimbashi",
        "railway": "Yurikamome"
    },
    {
        "name": "新江古田",
        "id": "odpt.Station:Toei.Oedo.ShinEgota",
        "railway": "Toei"
    },
    {
        "name": "新百合ヶ丘",
        "id": "odpt.Station:Odakyu.Odawara.ShinYurigaoka",
        "railway": "Odakyu"
    },
    {
        "name": "新羽",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Nippa",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "新豊洲",
        "id": "odpt.Station:Yurikamome.Yurikamome.ShinToyosu",
        "railway": "Yurikamome"
    },
    {
        "name": "新高円寺",
        "id": "odpt.Station:TokyoMetro.Marunouchi.ShinKoenji",
        "railway": "TokyoMetro"
    },
    {
        "name": "新高島平",
        "id": "odpt.Station:Toei.Mita.ShinTakashimadaira",
        "railway": "Toei"
    },
    {
        "name": "方南町",
        "id": "odpt.Station:TokyoMetro.MarunouchiBranch.Honancho",
        "railway": "TokyoMetro"
    },
    {
        "name": "日の出",
        "id": "odpt.Station:Yurikamome.Yurikamome.Hinode",
        "railway": "Yurikamome"
    },
    {
        "name": "日吉",
        "id": "odpt.Station:Tokyu.Meguro.Hiyoshi",
        "railway": "Tokyu"
    },
    {
        "name": "日吉",
        "id": "odpt.Station:Tokyu.TokyuShinYokohama.Hiyoshi",
        "railway": "Tokyu"
    },
    {
        "name": "日吉",
        "id": "odpt.Station:Tokyu.Toyoko.Hiyoshi",
        "railway": "Tokyu"
    },
    {
        "name": "日吉",
        "id": "odpt.Station:YokohamaMunicipal.Green.Hiyoshi",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "日吉本町",
        "id": "odpt.Station:YokohamaMunicipal.Green.HiyoshiHoncho",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "日暮里",
        "id": "odpt.Station:JR-East.JobanRapid.Nippori",
        "railway": "JR-East"
    },
    {
        "name": "日暮里",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Nippori",
        "railway": "JR-East"
    },
    {
        "name": "日暮里",
        "id": "odpt.Station:JR-East.Yamanote.Nippori",
        "railway": "JR-East"
    },
    {
        "name": "日暮里",
        "id": "odpt.Station:Keisei.Main.Nippori",
        "railway": "Keisei"
    },
    {
        "name": "日暮里",
        "id": "odpt.Station:Toei.NipporiToneri.Nippori",
        "railway": "Toei"
    },
    {
        "name": "日本橋",
        "id": "odpt.Station:TokyoMetro.Ginza.Nihombashi",
        "railway": "TokyoMetro"
    },
    {
        "name": "日本橋",
        "id": "odpt.Station:TokyoMetro.Tozai.Nihombashi",
        "railway": "TokyoMetro"
    },
    {
        "name": "日本橋",
        "id": "odpt.Station:Toei.Asakusa.Nihombashi",
        "railway": "Toei"
    },
    {
        "name": "日比谷",
        "id": "odpt.Station:TokyoMetro.Chiyoda.Hibiya",
        "railway": "TokyoMetro"
    },
    {
        "name": "日比谷",
        "id": "odpt.Station:TokyoMetro.Hibiya.Hibiya",
        "railway": "TokyoMetro"
    },
    {
        "name": "日比谷",
        "id": "odpt.Station:Toei.Mita.Hibiya",
        "railway": "Toei"
    },
    {
        "name": "早稲田",
        "id": "odpt.Station:TokyoMetro.Tozai.Waseda",
        "railway": "TokyoMetro"
    },
    {
        "name": "早稲田",
        "id": "odpt.Station:Toei.Arakawa.Waseda",
        "railway": "Toei"
    },
    {
        "name": "明治神宮前〈原宿〉",
        "id": "odpt.Station:TokyoMetro.Chiyoda.MeijiJingumae",
        "railway": "TokyoMetro"
    },
    {
        "name": "明治神宮前〈原宿〉",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.MeijiJingumae",
        "railway": "TokyoMetro"
    },
    {
        "name": "春日",
        "id": "odpt.Station:Toei.Mita.Kasuga",
        "railway": "Toei"
    },
    {
        "name": "春日",
        "id": "odpt.Station:Toei.Oedo.Kasuga",
        "railway": "Toei"
    },
    {
        "name": "曙橋",
        "id": "odpt.Station:Toei.Shinjuku.Akebonobashi",
        "railway": "Toei"
    },
    {
        "name": "月島",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Tsukishima",
        "railway": "TokyoMetro"
    },
    {
        "name": "月島",
        "id": "odpt.Station:Toei.Oedo.Tsukishima",
        "railway": "Toei"
    },
    {
        "name": "有明",
        "id": "odpt.Station:Yurikamome.Yurikamome.Ariake",
        "railway": "Yurikamome"
    },
    {
        "name": "有明テニスの森",
        "id": "odpt.Station:Yurikamome.Yurikamome.AriakeTennisNoMori",
        "railway": "Yurikamome"
    },
    {
        "name": "有楽町",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Yurakucho",
        "railway": "JR-East"
    },
    {
        "name": "有楽町",
        "id": "odpt.Station:JR-East.Yamanote.Yurakucho",
        "railway": "JR-East"
    },
    {
        "name": "有楽町",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Yurakucho",
        "railway": "TokyoMetro"
    },
    {
        "name": "木場",
        "id": "odpt.Station:TokyoMetro.Tozai.Kiba",
        "railway": "TokyoMetro"
    },
    {
        "name": "末広町",
        "id": "odpt.Station:TokyoMetro.Ginza.Suehirocho",
        "railway": "TokyoMetro"
    },
    {
        "name": "本八幡",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.MotoYawata",
        "railway": "JR-East"
    },
    {
        "name": "本八幡",
        "id": "odpt.Station:Toei.Shinjuku.Motoyawata",
        "railway": "Toei"
    },
    {
        "name": "本厚木",
        "id": "odpt.Station:Odakyu.Odawara.HonAtsugi",
        "railway": "Odakyu"
    },
    {
        "name": "本所吾妻橋",
        "id": "odpt.Station:Toei.Asakusa.HonjoAzumabashi",
        "railway": "Toei"
    },
    {
        "name": "本蓮沼",
        "id": "odpt.Station:Toei.Mita.Motohasunuma",
        "railway": "Toei"
    },
    {
        "name": "本郷三丁目",
        "id": "odpt.Station:TokyoMetro.Marunouchi.HongoSanchome",
        "railway": "TokyoMetro"
    },
    {
        "name": "本郷三丁目",
        "id": "odpt.Station:Toei.Oedo.HongoSanchome",
        "railway": "Toei"
    },
    {
        "name": "本駒込",
        "id": "odpt.Station:TokyoMetro.Namboku.HonKomagome",
        "railway": "TokyoMetro"
    },
    {
        "name": "東中野",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.HigashiNakano",
        "railway": "JR-East"
    },
    {
        "name": "東中野",
        "id": "odpt.Station:Toei.Oedo.HigashiNakano",
        "railway": "Toei"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-Central.TokaidoShinkansen.Tokyo",
        "railway": "JR-Central"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.Keiyo.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.ChuoRapid.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.JobanRapid.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.SobuRapid.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.Takasaki.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.Tokaido.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.Utsunomiya.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.Yamanote.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.Yokosuka.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.AkitaShinkansen.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.HokurikuShinkansen.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.JoetsuShinkansen.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.TohokuShinkansen.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:JR-East.YamagataShinkansen.Tokyo",
        "railway": "JR-East"
    },
    {
        "name": "東京",
        "id": "odpt.Station:TokyoMetro.Marunouchi.Tokyo",
        "railway": "TokyoMetro"
    },
    {
        "name": "東京テレポート",
        "id": "odpt.Station:TWR.Rinkai.TokyoTeleport",
        "railway": "TWR"
    },
    {
        "name": "東京ビッグサイト",
        "id": "odpt.Station:Yurikamome.Yurikamome.TokyoBigSight",
        "railway": "Yurikamome"
    },
    {
        "name": "東京国際クルーズターミナル",
        "id": "odpt.Station:Yurikamome.Yurikamome.TokyoInternationalCruiseTerminal",
        "railway": "Yurikamome"
    },
    {
        "name": "東大前",
        "id": "odpt.Station:TokyoMetro.Namboku.Todaimae",
        "railway": "TokyoMetro"
    },
    {
        "name": "東大島",
        "id": "odpt.Station:Toei.Shinjuku.HigashiOjima",
        "railway": "Toei"
    },
    {
        "name": "東尾久三丁目",
        "id": "odpt.Station:Toei.Arakawa.HigashiOguSanchome",
        "railway": "Toei"
    },
    {
        "name": "東山田",
        "id": "odpt.Station:YokohamaMunicipal.Green.HigashiYamata",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "東新宿",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.HigashiShinjuku",
        "railway": "TokyoMetro"
    },
    {
        "name": "東新宿",
        "id": "odpt.Station:Toei.Oedo.HigashiShinjuku",
        "railway": "Toei"
    },
    {
        "name": "東日本橋",
        "id": "odpt.Station:Toei.Asakusa.HigashiNihombashi",
        "railway": "Toei"
    },
    {
        "name": "東武動物公園",
        "id": "odpt.Station:Tobu.TobuSkytree.TobuDobutsuKoen",
        "railway": "Tobu"
    },
    {
        "name": "東池袋",
        "id": "odpt.Station:TokyoMetro.Yurakucho.HigashiIkebukuro",
        "railway": "TokyoMetro"
    },
    {
        "name": "東池袋四丁目",
        "id": "odpt.Station:Toei.Arakawa.HigashiIkebukuroYonchome",
        "railway": "Toei"
    },
    {
        "name": "東葉勝田台",
        "id": "odpt.Station:ToyoRapid.ToyoRapid.ToyoKatsutadai",
        "railway": "ToyoRapid"
    },
    {
        "name": "東銀座",
        "id": "odpt.Station:TokyoMetro.Hibiya.HigashiGinza",
        "railway": "TokyoMetro"
    },
    {
        "name": "東銀座",
        "id": "odpt.Station:Toei.Asakusa.HigashiGinza",
        "railway": "Toei"
    },
    {
        "name": "東陽町",
        "id": "odpt.Station:TokyoMetro.Tozai.Toyocho",
        "railway": "TokyoMetro"
    },
    {
        "name": "東雲",
        "id": "odpt.Station:TWR.Rinkai.Shinonome",
        "railway": "TWR"
    },
    {
        "name": "東高円寺",
        "id": "odpt.Station:TokyoMetro.Marunouchi.HigashiKoenji",
        "railway": "TokyoMetro"
    },
    {
        "name": "松が谷",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.Matsugaya",
        "railway": "TamaMonorail"
    },
    {
        "name": "松戸",
        "id": "odpt.Station:JR-East.JobanLocal.Matsudo",
        "railway": "JR-East"
    },
    {
        "name": "板橋",
        "id": "odpt.Station:JR-East.SaikyoKawagoe.Itabashi",
        "railway": "JR-East"
    },
    {
        "name": "板橋区役所前",
        "id": "odpt.Station:Toei.Mita.ItabashiKuyakushomae",
        "railway": "Toei"
    },
    {
        "name": "板橋本町",
        "id": "odpt.Station:Toei.Mita.Itabashihoncho",
        "railway": "Toei"
    },
    {
        "name": "柏",
        "id": "odpt.Station:JR-East.JobanLocal.Kashiwa",
        "railway": "JR-East"
    },
    {
        "name": "柏たなか",
        "id": "odpt.Station:MIR.TsukubaExpress.KashiwaTanaka",
        "railway": "MIR"
    },
    {
        "name": "柏の葉キャンパス",
        "id": "odpt.Station:MIR.TsukubaExpress.KashiwanohaCampus",
        "railway": "MIR"
    },
    {
        "name": "柴崎体育館",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.ShibasakiTaiikukan",
        "railway": "TamaMonorail"
    },
    {
        "name": "栄町",
        "id": "odpt.Station:Toei.Arakawa.Sakaecho",
        "railway": "Toei"
    },
    {
        "name": "根津",
        "id": "odpt.Station:TokyoMetro.Chiyoda.Nezu",
        "railway": "TokyoMetro"
    },
    {
        "name": "桜上水",
        "id": "odpt.Station:Keio.Keio.Sakurajosui",
        "railway": "Keio"
    },
    {
        "name": "桜木町",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Sakuragicho",
        "railway": "JR-East"
    },
    {
        "name": "桜木町",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Sakuragicho",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "桜田門",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Sakuradamon",
        "railway": "TokyoMetro"
    },
    {
        "name": "桜街道",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.Sakurakaido",
        "railway": "TamaMonorail"
    },
    {
        "name": "梶原",
        "id": "odpt.Station:Toei.Arakawa.Kajiwara",
        "railway": "Toei"
    },
    {
        "name": "森下",
        "id": "odpt.Station:Toei.Oedo.Morishita",
        "railway": "Toei"
    },
    {
        "name": "森下",
        "id": "odpt.Station:Toei.Shinjuku.Morishita",
        "railway": "Toei"
    },
    {
        "name": "森林公園",
        "id": "odpt.Station:Tobu.Tojo.ShinrinKoen",
        "railway": "Tobu"
    },
    {
        "name": "横浜",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Yokohama",
        "railway": "JR-East"
    },
    {
        "name": "横浜",
        "id": "odpt.Station:JR-East.ShonanShinjuku.Yokohama",
        "railway": "JR-East"
    },
    {
        "name": "横浜",
        "id": "odpt.Station:JR-East.Tokaido.Yokohama",
        "railway": "JR-East"
    },
    {
        "name": "横浜",
        "id": "odpt.Station:JR-East.Yokosuka.Yokohama",
        "railway": "JR-East"
    },
    {
        "name": "横浜",
        "id": "odpt.Station:Keikyu.Main.Yokohama",
        "railway": "Keikyu"
    },
    {
        "name": "横浜",
        "id": "odpt.Station:Minatomirai.Minatomirai.Yokohama",
        "railway": "Minatomirai"
    },
    {
        "name": "横浜",
        "id": "odpt.Station:Sotetsu.Main.Yokohama",
        "railway": "Sotetsu"
    },
    {
        "name": "横浜",
        "id": "odpt.Station:Tokyu.Toyoko.Yokohama",
        "railway": "Tokyu"
    },
    {
        "name": "横浜",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Yokohama",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "橋本",
        "id": "odpt.Station:Keio.Sagamihara.Hashimoto",
        "railway": "Keio"
    },
    {
        "name": "武蔵小山",
        "id": "odpt.Station:Tokyu.Meguro.MusashiKoyama",
        "railway": "Tokyu"
    },
    {
        "name": "武蔵小杉",
        "id": "odpt.Station:Tokyu.Meguro.MusashiKosugi",
        "railway": "Tokyu"
    },
    {
        "name": "武蔵小杉",
        "id": "odpt.Station:Tokyu.Toyoko.MusashiKosugi",
        "railway": "Tokyu"
    },
    {
        "name": "武蔵浦和",
        "id": "odpt.Station:JR-East.SaikyoKawagoe.MusashiUrawa",
        "railway": "JR-East"
    },
    {
        "name": "水天宮前",
        "id": "odpt.Station:TokyoMetro.Hanzomon.Suitengumae",
        "railway": "TokyoMetro"
    },
    {
        "name": "水道橋",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Suidobashi",
        "railway": "JR-East"
    },
    {
        "name": "水道橋",
        "id": "odpt.Station:Toei.Mita.Suidobashi",
        "railway": "Toei"
    },
    {
        "name": "氷川台",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.Hikawadai",
        "railway": "TokyoMetro"
    },
    {
        "name": "氷川台",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Hikawadai",
        "railway": "TokyoMetro"
    },
    {
        "name": "永田町",
        "id": "odpt.Station:TokyoMetro.Hanzomon.Nagatacho",
        "railway": "TokyoMetro"
    },
    {
        "name": "永田町",
        "id": "odpt.Station:TokyoMetro.Namboku.Nagatacho",
        "railway": "TokyoMetro"
    },
    {
        "name": "永田町",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Nagatacho",
        "railway": "TokyoMetro"
    },
    {
        "name": "汐留",
        "id": "odpt.Station:Toei.Oedo.Shiodome",
        "railway": "Toei"
    },
    {
        "name": "汐留",
        "id": "odpt.Station:Yurikamome.Yurikamome.Shiodome",
        "railway": "Yurikamome"
    },
    {
        "name": "江北",
        "id": "odpt.Station:Toei.NipporiToneri.Kohoku",
        "railway": "Toei"
    },
    {
        "name": "江戸川橋",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Edogawabashi",
        "railway": "TokyoMetro"
    },
    {
        "name": "池袋",
        "id": "odpt.Station:JR-East.SaikyoKawagoe.Ikebukuro",
        "railway": "JR-East"
    },
    {
        "name": "池袋",
        "id": "odpt.Station:JR-East.ShonanShinjuku.Ikebukuro",
        "railway": "JR-East"
    },
    {
        "name": "池袋",
        "id": "odpt.Station:JR-East.Yamanote.Ikebukuro",
        "railway": "JR-East"
    },
    {
        "name": "池袋",
        "id": "odpt.Station:Seibu.Ikebukuro.Ikebukuro",
        "railway": "Seibu"
    },
    {
        "name": "池袋",
        "id": "odpt.Station:Tobu.Tojo.Ikebukuro",
        "railway": "Tobu"
    },
    {
        "name": "池袋",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.Ikebukuro",
        "railway": "TokyoMetro"
    },
    {
        "name": "池袋",
        "id": "odpt.Station:TokyoMetro.Marunouchi.Ikebukuro",
        "railway": "TokyoMetro"
    },
    {
        "name": "池袋",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Ikebukuro",
        "railway": "TokyoMetro"
    },
    {
        "name": "泉体育館",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.IzumiTaiikukan",
        "railway": "TamaMonorail"
    },
    {
        "name": "泉岳寺",
        "id": "odpt.Station:Keikyu.Main.Sengakuji",
        "railway": "Keikyu"
    },
    {
        "name": "泉岳寺",
        "id": "odpt.Station:Toei.Asakusa.Sengakuji",
        "railway": "Toei"
    },
    {
        "name": "津田沼",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Tsudanuma",
        "railway": "JR-East"
    },
    {
        "name": "流山おおたかの森",
        "id": "odpt.Station:MIR.TsukubaExpress.NagareyamaOtakanomori",
        "railway": "MIR"
    },
    {
        "name": "流山おおたかの森",
        "id": "odpt.Station:Tobu.TobuUrbanPark.NagareyamaOtakanomori",
        "railway": "Tobu"
    },
    {
        "name": "流山セントラルパーク",
        "id": "odpt.Station:MIR.TsukubaExpress.NagareyamaCentralPark",
        "railway": "MIR"
    },
    {
        "name": "浅草",
        "id": "odpt.Station:MIR.TsukubaExpress.Asakusa",
        "railway": "MIR"
    },
    {
        "name": "浅草",
        "id": "odpt.Station:Tobu.TobuSkytree.Asakusa",
        "railway": "Tobu"
    },
    {
        "name": "浅草",
        "id": "odpt.Station:TokyoMetro.Ginza.Asakusa",
        "railway": "TokyoMetro"
    },
    {
        "name": "浅草",
        "id": "odpt.Station:Toei.Asakusa.Asakusa",
        "railway": "Toei"
    },
    {
        "name": "浅草橋",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Asakusabashi",
        "railway": "JR-East"
    },
    {
        "name": "浅草橋",
        "id": "odpt.Station:Toei.Asakusa.Asakusabashi",
        "railway": "Toei"
    },
    {
        "name": "浜松町",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Hamamatsucho",
        "railway": "JR-East"
    },
    {
        "name": "浜松町",
        "id": "odpt.Station:JR-East.Yamanote.Hamamatsucho",
        "railway": "JR-East"
    },
    {
        "name": "浜松町",
        "id": "odpt.Station:TokyoMonorail.HanedaAirport.Hamamatsucho",
        "railway": "TokyoMonorail"
    },
    {
        "name": "浜町",
        "id": "odpt.Station:Toei.Shinjuku.Hamacho",
        "railway": "Toei"
    },
    {
        "name": "浦和美園",
        "id": "odpt.Station:SaitamaRailway.SaitamaRailway.UrawaMisono",
        "railway": "SaitamaRailway"
    },
    {
        "name": "浦安",
        "id": "odpt.Station:TokyoMetro.Tozai.Urayasu",
        "railway": "TokyoMetro"
    },
    {
        "name": "浦賀",
        "id": "odpt.Station:Keikyu.Main.Uraga",
        "railway": "Keikyu"
    },
    {
        "name": "海老名",
        "id": "odpt.Station:Odakyu.Odawara.Ebina",
        "railway": "Odakyu"
    },
    {
        "name": "海老名",
        "id": "odpt.Station:Sotetsu.Main.Ebina",
        "railway": "Sotetsu"
    },
    {
        "name": "淡路町",
        "id": "odpt.Station:TokyoMetro.Marunouchi.Awajicho",
        "railway": "TokyoMetro"
    },
    {
        "name": "清澄白河",
        "id": "odpt.Station:TokyoMetro.Hanzomon.KiyosumiShirakawa",
        "railway": "TokyoMetro"
    },
    {
        "name": "清澄白河",
        "id": "odpt.Station:Toei.Oedo.KiyosumiShirakawa",
        "railway": "Toei"
    },
    {
        "name": "清瀬",
        "id": "odpt.Station:Seibu.Ikebukuro.Kiyose",
        "railway": "Seibu"
    },
    {
        "name": "渋谷",
        "id": "odpt.Station:JR-East.SaikyoKawagoe.Shibuya",
        "railway": "JR-East"
    },
    {
        "name": "渋谷",
        "id": "odpt.Station:JR-East.ShonanShinjuku.Shibuya",
        "railway": "JR-East"
    },
    {
        "name": "渋谷",
        "id": "odpt.Station:JR-East.Yamanote.Shibuya",
        "railway": "JR-East"
    },
    {
        "name": "渋谷",
        "id": "odpt.Station:Keio.Inokashira.Shibuya",
        "railway": "Keio"
    },
    {
        "name": "渋谷",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.Shibuya",
        "railway": "TokyoMetro"
    },
    {
        "name": "渋谷",
        "id": "odpt.Station:TokyoMetro.Ginza.Shibuya",
        "railway": "TokyoMetro"
    },
    {
        "name": "渋谷",
        "id": "odpt.Station:TokyoMetro.Hanzomon.Shibuya",
        "railway": "TokyoMetro"
    },
    {
        "name": "渋谷",
        "id": "odpt.Station:Tokyu.DenEnToshi.Shibuya",
        "railway": "Tokyu"
    },
    {
        "name": "渋谷",
        "id": "odpt.Station:Tokyu.Toyoko.Shibuya",
        "railway": "Tokyu"
    },
    {
        "name": "港南中央",
        "id": "odpt.Station:YokohamaMunicipal.Blue.KonanChuo",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "湘南台",
        "id": "odpt.Station:Odakyu.Enoshima.Shonandai",
        "railway": "Odakyu"
    },
    {
        "name": "湘南台",
        "id": "odpt.Station:Sotetsu.Izumino.Shonandai",
        "railway": "Sotetsu"
    },
    {
        "name": "湘南台",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Shonandai",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "湯島",
        "id": "odpt.Station:TokyoMetro.Chiyoda.Yushima",
        "railway": "TokyoMetro"
    },
    {
        "name": "溜池山王",
        "id": "odpt.Station:TokyoMetro.Ginza.TameikeSanno",
        "railway": "TokyoMetro"
    },
    {
        "name": "溜池山王",
        "id": "odpt.Station:TokyoMetro.Namboku.TameikeSanno",
        "railway": "TokyoMetro"
    },
    {
        "name": "滝野川一丁目",
        "id": "odpt.Station:Toei.Arakawa.TakinogawaItchome",
        "railway": "Toei"
    },
    {
        "name": "熊野前",
        "id": "odpt.Station:Toei.Arakawa.Kumanomae",
        "railway": "Toei"
    },
    {
        "name": "熊野前",
        "id": "odpt.Station:Toei.NipporiToneri.Kumanomae",
        "railway": "Toei"
    },
    {
        "name": "片倉町",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Katakuracho",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "牛込柳町",
        "id": "odpt.Station:Toei.Oedo.UshigomeYanagicho",
        "railway": "Toei"
    },
    {
        "name": "牛込神楽坂",
        "id": "odpt.Station:Toei.Oedo.UshigomeKagurazaka",
        "railway": "Toei"
    },
    {
        "name": "玉川上水",
        "id": "odpt.Station:Seibu.Haijima.TamagawaJosui",
        "railway": "Seibu"
    },
    {
        "name": "玉川上水",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.TamagawaJosui",
        "railway": "TamaMonorail"
    },
    {
        "name": "王子",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Oji",
        "railway": "JR-East"
    },
    {
        "name": "王子",
        "id": "odpt.Station:TokyoMetro.Namboku.Oji",
        "railway": "TokyoMetro"
    },
    {
        "name": "王子神谷",
        "id": "odpt.Station:TokyoMetro.Namboku.OjiKamiya",
        "railway": "TokyoMetro"
    },
    {
        "name": "王子駅前",
        "id": "odpt.Station:Toei.Arakawa.OjiEkimae",
        "railway": "Toei"
    },
    {
        "name": "瑞江",
        "id": "odpt.Station:Toei.Shinjuku.Mizue",
        "railway": "Toei"
    },
    {
        "name": "田原町",
        "id": "odpt.Station:TokyoMetro.Ginza.Tawaramachi",
        "railway": "TokyoMetro"
    },
    {
        "name": "田町",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Tamachi",
        "railway": "JR-East"
    },
    {
        "name": "田町",
        "id": "odpt.Station:JR-East.Yamanote.Tamachi",
        "railway": "JR-East"
    },
    {
        "name": "甲州街道",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.Koshukaido",
        "railway": "TamaMonorail"
    },
    {
        "name": "町屋",
        "id": "odpt.Station:Keisei.Main.Machiya",
        "railway": "Keisei"
    },
    {
        "name": "町屋",
        "id": "odpt.Station:TokyoMetro.Chiyoda.Machiya",
        "railway": "TokyoMetro"
    },
    {
        "name": "町屋二丁目",
        "id": "odpt.Station:Toei.Arakawa.MachiyaNichome",
        "railway": "Toei"
    },
    {
        "name": "町屋駅前",
        "id": "odpt.Station:Toei.Arakawa.MachiyaEkimae",
        "railway": "Toei"
    },
    {
        "name": "町田",
        "id": "odpt.Station:Odakyu.Odawara.Machida",
        "railway": "Odakyu"
    },
    {
        "name": "白山",
        "id": "odpt.Station:Toei.Mita.Hakusan",
        "railway": "Toei"
    },
    {
        "name": "白金台",
        "id": "odpt.Station:TokyoMetro.Namboku.Shirokanedai",
        "railway": "TokyoMetro"
    },
    {
        "name": "白金台",
        "id": "odpt.Station:Toei.Mita.Shirokanedai",
        "railway": "Toei"
    },
    {
        "name": "白金高輪",
        "id": "odpt.Station:TokyoMetro.Namboku.ShirokaneTakanawa",
        "railway": "TokyoMetro"
    },
    {
        "name": "白金高輪",
        "id": "odpt.Station:Toei.Mita.ShirokaneTakanawa",
        "railway": "Toei"
    },
    {
        "name": "目黒",
        "id": "odpt.Station:JR-East.Yamanote.Meguro",
        "railway": "JR-East"
    },
    {
        "name": "目黒",
        "id": "odpt.Station:TokyoMetro.Namboku.Meguro",
        "railway": "TokyoMetro"
    },
    {
        "name": "目黒",
        "id": "odpt.Station:Tokyu.Meguro.Meguro",
        "railway": "Tokyu"
    },
    {
        "name": "目黒",
        "id": "odpt.Station:Toei.Mita.Meguro",
        "railway": "Toei"
    },
    {
        "name": "相模大野",
        "id": "odpt.Station:Odakyu.Odawara.SagamiOno",
        "railway": "Odakyu"
    },
    {
        "name": "石神井公園",
        "id": "odpt.Station:Seibu.Ikebukuro.ShakujiiKoen",
        "railway": "Seibu"
    },
    {
        "name": "砂川七番",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.SunagawaNanaban",
        "railway": "TamaMonorail"
    },
    {
        "name": "研究学園",
        "id": "odpt.Station:MIR.TsukubaExpress.KenkyuGakuen",
        "railway": "MIR"
    },
    {
        "name": "神保町",
        "id": "odpt.Station:TokyoMetro.Hanzomon.Jimbocho",
        "railway": "TokyoMetro"
    },
    {
        "name": "神保町",
        "id": "odpt.Station:Toei.Mita.Jimbocho",
        "railway": "Toei"
    },
    {
        "name": "神保町",
        "id": "odpt.Station:Toei.Shinjuku.Jimbocho",
        "railway": "Toei"
    },
    {
        "name": "神奈川新町",
        "id": "odpt.Station:Keikyu.Main.KanagawaShimmachi",
        "railway": "Keikyu"
    },
    {
        "name": "神楽坂",
        "id": "odpt.Station:TokyoMetro.Tozai.Kagurazaka",
        "railway": "TokyoMetro"
    },
    {
        "name": "神田",
        "id": "odpt.Station:JR-East.ChuoRapid.Kanda",
        "railway": "JR-East"
    },
    {
        "name": "神田",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Kanda",
        "railway": "JR-East"
    },
    {
        "name": "神田",
        "id": "odpt.Station:JR-East.Yamanote.Kanda",
        "railway": "JR-East"
    },
    {
        "name": "神田",
        "id": "odpt.Station:TokyoMetro.Ginza.Kanda",
        "railway": "TokyoMetro"
    },
    {
        "name": "神谷町",
        "id": "odpt.Station:TokyoMetro.Hibiya.Kamiyacho",
        "railway": "TokyoMetro"
    },
    {
        "name": "秋葉原",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Akihabara",
        "railway": "JR-East"
    },
    {
        "name": "秋葉原",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Akihabara",
        "railway": "JR-East"
    },
    {
        "name": "秋葉原",
        "id": "odpt.Station:JR-East.Yamanote.Akihabara",
        "railway": "JR-East"
    },
    {
        "name": "秋葉原",
        "id": "odpt.Station:MIR.TsukubaExpress.Akihabara",
        "railway": "MIR"
    },
    {
        "name": "秋葉原",
        "id": "odpt.Station:TokyoMetro.Hibiya.Akihabara",
        "railway": "TokyoMetro"
    },
    {
        "name": "程久保",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.Hodokubo",
        "railway": "TamaMonorail"
    },
    {
        "name": "稲荷町",
        "id": "odpt.Station:TokyoMetro.Ginza.Inaricho",
        "railway": "TokyoMetro"
    },
    {
        "name": "立場",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Tateba",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "立川",
        "id": "odpt.Station:JR-East.ChuoRapid.Tachikawa",
        "railway": "JR-East"
    },
    {
        "name": "立川",
        "id": "odpt.Station:JR-East.Nambu.Tachikawa",
        "railway": "JR-East"
    },
    {
        "name": "立川",
        "id": "odpt.Station:JR-East.Ome.Tachikawa",
        "railway": "JR-East"
    },
    {
        "name": "立川北",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.TachikawaKita",
        "railway": "TamaMonorail"
    },
    {
        "name": "立川南",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.TachikawaMinami",
        "railway": "TamaMonorail"
    },
    {
        "name": "立飛",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.Tachihi",
        "railway": "TamaMonorail"
    },
    {
        "name": "竹ノ塚",
        "id": "odpt.Station:Tobu.TobuSkytree.Takenotsuka",
        "railway": "Tobu"
    },
    {
        "name": "竹橋",
        "id": "odpt.Station:TokyoMetro.Tozai.Takebashi",
        "railway": "TokyoMetro"
    },
    {
        "name": "竹芝",
        "id": "odpt.Station:Yurikamome.Yurikamome.Takeshiba",
        "railway": "Yurikamome"
    },
    {
        "name": "笹塚",
        "id": "odpt.Station:Keio.KeioNew.Sasazuka",
        "railway": "Keio"
    },
    {
        "name": "箱根湯本",
        "id": "odpt.Station:OdakyuHakone.HakoneTozan.HakoneYumoto",
        "railway": "OdakyuHakone"
    },
    {
        "name": "築地",
        "id": "odpt.Station:TokyoMetro.Hibiya.Tsukiji",
        "railway": "TokyoMetro"
    },
    {
        "name": "築地市場",
        "id": "odpt.Station:Toei.Oedo.Tsukijishijo",
        "railway": "Toei"
    },
    {
        "name": "篠崎",
        "id": "odpt.Station:Toei.Shinjuku.Shinozaki",
        "railway": "Toei"
    },
    {
        "name": "綾瀬",
        "id": "odpt.Station:JR-East.JobanLocal.Ayase",
        "railway": "JR-East"
    },
    {
        "name": "綾瀬",
        "id": "odpt.Station:TokyoMetro.Chiyoda.Ayase",
        "railway": "TokyoMetro"
    },
    {
        "name": "練馬",
        "id": "odpt.Station:Seibu.Ikebukuro.Nerima",
        "railway": "Seibu"
    },
    {
        "name": "練馬",
        "id": "odpt.Station:Seibu.SeibuYurakucho.Nerima",
        "railway": "Seibu"
    },
    {
        "name": "練馬",
        "id": "odpt.Station:Seibu.Toshima.Nerima",
        "railway": "Seibu"
    },
    {
        "name": "練馬",
        "id": "odpt.Station:Toei.Oedo.Nerima",
        "railway": "Toei"
    },
    {
        "name": "練馬春日町",
        "id": "odpt.Station:Toei.Oedo.NerimaKasugacho",
        "railway": "Toei"
    },
    {
        "name": "羽田空港第１・第２ターミナル",
        "id": "odpt.Station:Keikyu.Airport.HanedaAirportTerminal1and2",
        "railway": "Keikyu"
    },
    {
        "name": "自由が丘",
        "id": "odpt.Station:Tokyu.Toyoko.Jiyugaoka",
        "railway": "Tokyu"
    },
    {
        "name": "舎人",
        "id": "odpt.Station:Toei.NipporiToneri.Toneri",
        "railway": "Toei"
    },
    {
        "name": "舎人公園",
        "id": "odpt.Station:Toei.NipporiToneri.ToneriKoen",
        "railway": "Toei"
    },
    {
        "name": "舞岡",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Maioka",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "船堀",
        "id": "odpt.Station:Toei.Shinjuku.Funabori",
        "railway": "Toei"
    },
    {
        "name": "芝公園",
        "id": "odpt.Station:Toei.Mita.Shibakoen",
        "railway": "Toei"
    },
    {
        "name": "芝山千代田",
        "id": "odpt.Station:Shibayama.Shibayama.ShibayamaChiyoda",
        "railway": "Shibayama"
    },
    {
        "name": "芝浦ふ頭",
        "id": "odpt.Station:Yurikamome.Yurikamome.ShibauraFuto",
        "railway": "Yurikamome"
    },
    {
        "name": "若松河田",
        "id": "odpt.Station:Toei.Oedo.WakamatsuKawada",
        "railway": "Toei"
    },
    {
        "name": "若葉台",
        "id": "odpt.Station:Keio.Sagamihara.Wakabadai",
        "railway": "Keio"
    },
    {
        "name": "茅場町",
        "id": "odpt.Station:TokyoMetro.Hibiya.Kayabacho",
        "railway": "TokyoMetro"
    },
    {
        "name": "茅場町",
        "id": "odpt.Station:TokyoMetro.Tozai.Kayabacho",
        "railway": "TokyoMetro"
    },
    {
        "name": "茗荷谷",
        "id": "odpt.Station:TokyoMetro.Marunouchi.Myogadani",
        "railway": "TokyoMetro"
    },
    {
        "name": "草加",
        "id": "odpt.Station:Tobu.TobuSkytree.Soka",
        "railway": "Tobu"
    },
    {
        "name": "荒川一中前",
        "id": "odpt.Station:Toei.Arakawa.ArakawaItchumae",
        "railway": "Toei"
    },
    {
        "name": "荒川七丁目",
        "id": "odpt.Station:Toei.Arakawa.ArakawaNanachome",
        "railway": "Toei"
    },
    {
        "name": "荒川二丁目",
        "id": "odpt.Station:Toei.Arakawa.ArakawaNichome",
        "railway": "Toei"
    },
    {
        "name": "荒川区役所前",
        "id": "odpt.Station:Toei.Arakawa.Arakawakuyakushomae",
        "railway": "Toei"
    },
    {
        "name": "荒川車庫前",
        "id": "odpt.Station:Toei.Arakawa.ArakawaShakomae",
        "railway": "Toei"
    },
    {
        "name": "荒川遊園地前",
        "id": "odpt.Station:Toei.Arakawa.ArakawaYuenchimae",
        "railway": "Toei"
    },
    {
        "name": "荻窪",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Ogikubo",
        "railway": "JR-East"
    },
    {
        "name": "荻窪",
        "id": "odpt.Station:JR-East.ChuoRapid.Ogikubo",
        "railway": "JR-East"
    },
    {
        "name": "荻窪",
        "id": "odpt.Station:TokyoMetro.Marunouchi.Ogikubo",
        "railway": "TokyoMetro"
    },
    {
        "name": "菊名",
        "id": "odpt.Station:Tokyu.Toyoko.Kikuna",
        "railway": "Tokyu"
    },
    {
        "name": "菊川",
        "id": "odpt.Station:Toei.Shinjuku.Kikukawa",
        "railway": "Toei"
    },
    {
        "name": "落合",
        "id": "odpt.Station:TokyoMetro.Tozai.Ochiai",
        "railway": "TokyoMetro"
    },
    {
        "name": "落合南長崎",
        "id": "odpt.Station:Toei.Oedo.OchiaiMinamiNagasaki",
        "railway": "Toei"
    },
    {
        "name": "葛西",
        "id": "odpt.Station:TokyoMetro.Tozai.Kasai",
        "railway": "TokyoMetro"
    },
    {
        "name": "蒔田",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Maita",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "蓮根",
        "id": "odpt.Station:Toei.Mita.Hasune",
        "railway": "Toei"
    },
    {
        "name": "蔵前",
        "id": "odpt.Station:Toei.Asakusa.Kuramae",
        "railway": "Toei"
    },
    {
        "name": "蔵前",
        "id": "odpt.Station:Toei.Oedo.Kuramae",
        "railway": "Toei"
    },
    {
        "name": "虎ノ門",
        "id": "odpt.Station:TokyoMetro.Ginza.Toranomon",
        "railway": "TokyoMetro"
    },
    {
        "name": "虎ノ門ヒルズ",
        "id": "odpt.Station:TokyoMetro.Hibiya.ToranomonHills",
        "railway": "TokyoMetro"
    },
    {
        "name": "行徳",
        "id": "odpt.Station:TokyoMetro.Tozai.Gyotoku",
        "railway": "TokyoMetro"
    },
    {
        "name": "表参道",
        "id": "odpt.Station:TokyoMetro.Chiyoda.OmoteSando",
        "railway": "TokyoMetro"
    },
    {
        "name": "表参道",
        "id": "odpt.Station:TokyoMetro.Ginza.OmoteSando",
        "railway": "TokyoMetro"
    },
    {
        "name": "表参道",
        "id": "odpt.Station:TokyoMetro.Hanzomon.OmoteSando",
        "railway": "TokyoMetro"
    },
    {
        "name": "西ケ原",
        "id": "odpt.Station:TokyoMetro.Namboku.Nishigahara",
        "railway": "TokyoMetro"
    },
    {
        "name": "西ヶ原四丁目",
        "id": "odpt.Station:Toei.Arakawa.NishigaharaYonchome",
        "railway": "Toei"
    },
    {
        "name": "西台",
        "id": "odpt.Station:Toei.Mita.Nishidai",
        "railway": "Toei"
    },
    {
        "name": "西大島",
        "id": "odpt.Station:Toei.Shinjuku.NishiOjima",
        "railway": "Toei"
    },
    {
        "name": "西巣鴨",
        "id": "odpt.Station:Toei.Mita.NishiSugamo",
        "railway": "Toei"
    },
    {
        "name": "西所沢",
        "id": "odpt.Station:Seibu.Ikebukuro.NishiTokorozawa",
        "railway": "Seibu"
    },
    {
        "name": "西新井大師西",
        "id": "odpt.Station:Toei.NipporiToneri.NishiaraidaishiNishi",
        "railway": "Toei"
    },
    {
        "name": "西新宿",
        "id": "odpt.Station:TokyoMetro.Marunouchi.NishiShinjuku",
        "railway": "TokyoMetro"
    },
    {
        "name": "西新宿五丁目",
        "id": "odpt.Station:Toei.Oedo.NishiShinjukuGochome",
        "railway": "Toei"
    },
    {
        "name": "西日暮里",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.NishiNippori",
        "railway": "JR-East"
    },
    {
        "name": "西日暮里",
        "id": "odpt.Station:JR-East.Yamanote.NishiNippori",
        "railway": "JR-East"
    },
    {
        "name": "西日暮里",
        "id": "odpt.Station:TokyoMetro.Chiyoda.NishiNippori",
        "railway": "TokyoMetro"
    },
    {
        "name": "西日暮里",
        "id": "odpt.Station:Toei.NipporiToneri.NishiNippori",
        "railway": "Toei"
    },
    {
        "name": "西早稲田",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.NishiWaseda",
        "railway": "TokyoMetro"
    },
    {
        "name": "西武新宿",
        "id": "odpt.Station:Seibu.Shinjuku.SeibuShinjuku",
        "railway": "Seibu"
    },
    {
        "name": "西武球場前",
        "id": "odpt.Station:Seibu.Sayama.SeibukyujoMae",
        "railway": "Seibu"
    },
    {
        "name": "西武秩父",
        "id": "odpt.Station:Seibu.SeibuChichibu.SeibuChichibu",
        "railway": "Seibu"
    },
    {
        "name": "西船橋",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.NishiFunabashi",
        "railway": "JR-East"
    },
    {
        "name": "西船橋",
        "id": "odpt.Station:JR-East.Keiyo.NishiFunabashi",
        "railway": "JR-East"
    },
    {
        "name": "西船橋",
        "id": "odpt.Station:JR-East.Musashino.NishiFunabashi",
        "railway": "JR-East"
    },
    {
        "name": "西船橋",
        "id": "odpt.Station:TokyoMetro.Tozai.NishiFunabashi",
        "railway": "TokyoMetro"
    },
    {
        "name": "西船橋",
        "id": "odpt.Station:ToyoRapid.ToyoRapid.NishiFunabashi",
        "railway": "ToyoRapid"
    },
    {
        "name": "西葛西",
        "id": "odpt.Station:TokyoMetro.Tozai.NishiKasai",
        "railway": "TokyoMetro"
    },
    {
        "name": "西谷",
        "id": "odpt.Station:Sotetsu.SotetsuShinYokohama.Nishiya",
        "railway": "Sotetsu"
    },
    {
        "name": "西馬込",
        "id": "odpt.Station:Toei.Asakusa.NishiMagome",
        "railway": "Toei"
    },
    {
        "name": "西高島平",
        "id": "odpt.Station:Toei.Mita.NishiTakashimadaira",
        "railway": "Toei"
    },
    {
        "name": "要町",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.Kanamecho",
        "railway": "TokyoMetro"
    },
    {
        "name": "要町",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Kanamecho",
        "railway": "TokyoMetro"
    },
    {
        "name": "見沼代親水公園",
        "id": "odpt.Station:Toei.NipporiToneri.MinumadaiShinsuikoen",
        "railway": "Toei"
    },
    {
        "name": "調布",
        "id": "odpt.Station:Keio.Keio.Chofu",
        "railway": "Keio"
    },
    {
        "name": "護国寺",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Gokokuji",
        "railway": "TokyoMetro"
    },
    {
        "name": "谷在家",
        "id": "odpt.Station:Toei.NipporiToneri.Yazaike",
        "railway": "Toei"
    },
    {
        "name": "豊島園",
        "id": "odpt.Station:Seibu.Toshima.Toshimaen",
        "railway": "Seibu"
    },
    {
        "name": "豊島園",
        "id": "odpt.Station:Toei.Oedo.Toshimaen",
        "railway": "Toei"
    },
    {
        "name": "豊洲",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Toyosu",
        "railway": "TokyoMetro"
    },
    {
        "name": "豊洲",
        "id": "odpt.Station:Yurikamome.Yurikamome.Toyosu",
        "railway": "Yurikamome"
    },
    {
        "name": "赤土小学校前",
        "id": "odpt.Station:Toei.NipporiToneri.AkadoShogakkomae",
        "railway": "Toei"
    },
    {
        "name": "赤坂",
        "id": "odpt.Station:TokyoMetro.Chiyoda.Akasaka",
        "railway": "TokyoMetro"
    },
    {
        "name": "赤坂見附",
        "id": "odpt.Station:TokyoMetro.Ginza.AkasakaMitsuke",
        "railway": "TokyoMetro"
    },
    {
        "name": "赤坂見附",
        "id": "odpt.Station:TokyoMetro.Marunouchi.AkasakaMitsuke",
        "railway": "TokyoMetro"
    },
    {
        "name": "赤羽",
        "id": "odpt.Station:JR-East.SaikyoKawagoe.Akabane",
        "railway": "JR-East"
    },
    {
        "name": "赤羽岩淵",
        "id": "odpt.Station:SaitamaRailway.SaitamaRailway.AkabaneIwabuchi",
        "railway": "SaitamaRailway"
    },
    {
        "name": "赤羽岩淵",
        "id": "odpt.Station:TokyoMetro.Namboku.AkabaneIwabuchi",
        "railway": "TokyoMetro"
    },
    {
        "name": "赤羽橋",
        "id": "odpt.Station:Toei.Oedo.Akabanebashi",
        "railway": "Toei"
    },
    {
        "name": "足立小台",
        "id": "odpt.Station:Toei.NipporiToneri.AdachiOdai",
        "railway": "Toei"
    },
    {
        "name": "踊場",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Odoriba",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "辰巳",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Tatsumi",
        "railway": "TokyoMetro"
    },
    {
        "name": "逗子・葉山",
        "id": "odpt.Station:Keikyu.Zushi.ZushiHayama",
        "railway": "Keikyu"
    },
    {
        "name": "都庁前",
        "id": "odpt.Station:Toei.Oedo.Tochomae",
        "railway": "Toei"
    },
    {
        "name": "都筑ふれあいの丘",
        "id": "odpt.Station:YokohamaMunicipal.Green.TsuzukiFureainooka",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "都電雑司ヶ谷",
        "id": "odpt.Station:Toei.Arakawa.TodenZoshigaya",
        "railway": "Toei"
    },
    {
        "name": "金沢文庫",
        "id": "odpt.Station:Keikyu.Main.KanazawaBunko",
        "railway": "Keikyu"
    },
    {
        "name": "銀座",
        "id": "odpt.Station:TokyoMetro.Ginza.Ginza",
        "railway": "TokyoMetro"
    },
    {
        "name": "銀座",
        "id": "odpt.Station:TokyoMetro.Hibiya.Ginza",
        "railway": "TokyoMetro"
    },
    {
        "name": "銀座",
        "id": "odpt.Station:TokyoMetro.Marunouchi.Ginza",
        "railway": "TokyoMetro"
    },
    {
        "name": "銀座一丁目",
        "id": "odpt.Station:TokyoMetro.Yurakucho.GinzaItchome",
        "railway": "TokyoMetro"
    },
    {
        "name": "錦糸町",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Kinshicho",
        "railway": "JR-East"
    },
    {
        "name": "錦糸町",
        "id": "odpt.Station:JR-East.SobuRapid.Kinshicho",
        "railway": "JR-East"
    },
    {
        "name": "錦糸町",
        "id": "odpt.Station:TokyoMetro.Hanzomon.Kinshicho",
        "railway": "TokyoMetro"
    },
    {
        "name": "長津田",
        "id": "odpt.Station:Tokyu.DenEnToshi.Nagatsuta",
        "railway": "Tokyu"
    },
    {
        "name": "門前仲町",
        "id": "odpt.Station:TokyoMetro.Tozai.MonzenNakacho",
        "railway": "TokyoMetro"
    },
    {
        "name": "門前仲町",
        "id": "odpt.Station:Toei.Oedo.MonzenNakacho",
        "railway": "Toei"
    },
    {
        "name": "関内",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.Kannai",
        "railway": "JR-East"
    },
    {
        "name": "関内",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Kannai",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "阪東橋",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Bandobashi",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "雑司が谷",
        "id": "odpt.Station:TokyoMetro.Fukutoshin.Zoshigaya",
        "railway": "TokyoMetro"
    },
    {
        "name": "霞ケ関",
        "id": "odpt.Station:TokyoMetro.Chiyoda.Kasumigaseki",
        "railway": "TokyoMetro"
    },
    {
        "name": "霞ケ関",
        "id": "odpt.Station:TokyoMetro.Hibiya.Kasumigaseki",
        "railway": "TokyoMetro"
    },
    {
        "name": "霞ケ関",
        "id": "odpt.Station:TokyoMetro.Marunouchi.Kasumigaseki",
        "railway": "TokyoMetro"
    },
    {
        "name": "青井",
        "id": "odpt.Station:MIR.TsukubaExpress.Aoi",
        "railway": "MIR"
    },
    {
        "name": "青山一丁目",
        "id": "odpt.Station:TokyoMetro.Ginza.AoyamaItchome",
        "railway": "TokyoMetro"
    },
    {
        "name": "青山一丁目",
        "id": "odpt.Station:TokyoMetro.Hanzomon.AoyamaItchome",
        "railway": "TokyoMetro"
    },
    {
        "name": "青山一丁目",
        "id": "odpt.Station:Toei.Oedo.AoyamaItchome",
        "railway": "Toei"
    },
    {
        "name": "青海",
        "id": "odpt.Station:Yurikamome.Yurikamome.Aomi",
        "railway": "Yurikamome"
    },
    {
        "name": "青砥",
        "id": "odpt.Station:Keisei.Oshiage.Aoto",
        "railway": "Keisei"
    },
    {
        "name": "面影橋",
        "id": "odpt.Station:Toei.Arakawa.Omokagebashi",
        "railway": "Toei"
    },
    {
        "name": "飛鳥山",
        "id": "odpt.Station:Toei.Arakawa.Asukayama",
        "railway": "Toei"
    },
    {
        "name": "飯田橋",
        "id": "odpt.Station:JR-East.ChuoSobuLocal.Iidabashi",
        "railway": "JR-East"
    },
    {
        "name": "飯田橋",
        "id": "odpt.Station:TokyoMetro.Namboku.Iidabashi",
        "railway": "TokyoMetro"
    },
    {
        "name": "飯田橋",
        "id": "odpt.Station:TokyoMetro.Tozai.Iidabashi",
        "railway": "TokyoMetro"
    },
    {
        "name": "飯田橋",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Iidabashi",
        "railway": "TokyoMetro"
    },
    {
        "name": "飯田橋",
        "id": "odpt.Station:Toei.Oedo.Iidabashi",
        "railway": "Toei"
    },
    {
        "name": "飯能",
        "id": "odpt.Station:Seibu.Ikebukuro.Hanno",
        "railway": "Seibu"
    },
    {
        "name": "馬喰横山",
        "id": "odpt.Station:Toei.Shinjuku.BakuroYokoyama",
        "railway": "Toei"
    },
    {
        "name": "馬喰町",
        "id": "odpt.Station:JR-East.SobuRapid.Bakurocho",
        "railway": "JR-East"
    },
    {
        "name": "馬込",
        "id": "odpt.Station:Toei.Asakusa.Magome",
        "railway": "Toei"
    },
    {
        "name": "駒込",
        "id": "odpt.Station:JR-East.Yamanote.Komagome",
        "railway": "JR-East"
    },
    {
        "name": "駒込",
        "id": "odpt.Station:TokyoMetro.Namboku.Komagome",
        "railway": "TokyoMetro"
    },
    {
        "name": "高尾",
        "id": "odpt.Station:Keio.Takao.Takao",
        "railway": "Keio"
    },
    {
        "name": "高尾山口",
        "id": "odpt.Station:Keio.Takao.Takaosanguchi",
        "railway": "Keio"
    },
    {
        "name": "高島平",
        "id": "odpt.Station:Toei.Mita.Takashimadaira",
        "railway": "Toei"
    },
    {
        "name": "高島町",
        "id": "odpt.Station:YokohamaMunicipal.Blue.Takashimacho",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "高幡不動",
        "id": "odpt.Station:Keio.Dobutsuen.Takahatafudo",
        "railway": "Keio"
    },
    {
        "name": "高幡不動",
        "id": "odpt.Station:Keio.Keio.Takahatafudo",
        "railway": "Keio"
    },
    {
        "name": "高幡不動",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.Takahatafudo",
        "railway": "TamaMonorail"
    },
    {
        "name": "高松",
        "id": "odpt.Station:TamaMonorail.TamaMonorail.Takamatsu",
        "railway": "TamaMonorail"
    },
    {
        "name": "高田",
        "id": "odpt.Station:YokohamaMunicipal.Green.Takata",
        "railway": "YokohamaMunicipal"
    },
    {
        "name": "高田馬場",
        "id": "odpt.Station:JR-East.Yamanote.Takadanobaba",
        "railway": "JR-East"
    },
    {
        "name": "高田馬場",
        "id": "odpt.Station:Seibu.Shinjuku.Takadanobaba",
        "railway": "Seibu"
    },
    {
        "name": "高田馬場",
        "id": "odpt.Station:TokyoMetro.Tozai.Takadanobaba",
        "railway": "TokyoMetro"
    },
    {
        "name": "高輪ゲートウェイ",
        "id": "odpt.Station:JR-East.KeihinTohokuNegishi.TakanawaGateway",
        "railway": "JR-East"
    },
    {
        "name": "高輪ゲートウェイ",
        "id": "odpt.Station:JR-East.Yamanote.TakanawaGateway",
        "railway": "JR-East"
    },
    {
        "name": "高輪台",
        "id": "odpt.Station:Toei.Asakusa.Takanawadai",
        "railway": "Toei"
    },
    {
        "name": "高野",
        "id": "odpt.Station:Toei.NipporiToneri.Koya",
        "railway": "Toei"
    },
    {
        "name": "鬼子母神前",
        "id": "odpt.Station:Toei.Arakawa.Kishibojimmae",
        "railway": "Toei"
    },
    {
        "name": "鳩ヶ谷",
        "id": "odpt.Station:SaitamaRailway.SaitamaRailway.Hatogaya",
        "railway": "SaitamaRailway"
    },
    {
        "name": "鷺沼",
        "id": "odpt.Station:Tokyu.DenEnToshi.Saginuma",
        "railway": "Tokyu"
    },
    {
        "name": "麴町",
        "id": "odpt.Station:TokyoMetro.Yurakucho.Kojimachi",
        "railway": "TokyoMetro"
    },
    {
        "name": "麻布十番",
        "id": "odpt.Station:TokyoMetro.Namboku.AzabuJuban",
        "railway": "TokyoMetro"
    },
    {
        "name": "麻布十番",
        "id": "odpt.Station:Toei.Oedo.AzabuJuban",
        "railway": "Toei"
    },
]
