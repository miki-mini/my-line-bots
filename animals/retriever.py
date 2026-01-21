from fastapi import APIRouter
from pydantic import BaseModel
from enum import Enum
import math

router = APIRouter()

class AnimalType(Enum):
    DOG_SMALL = "dog_small"
    DOG_MEDIUM = "dog_medium"
    DOG_LARGE = "dog_large"
    CAT = "cat"
    RABBIT = "rabbit"
    HAMSTER = "hamster"
    BIRD_SMALL = "bird_small"
    BIRD_MEDIUM = "bird_medium"
    BIRD_LARGE = "bird_large"
    TORTOISE = "tortoise"
    GECKO = "gecko"
    ELEPHANT = "elephant"
    GIRAFFE = "giraffe"
    # Project All-Stars
    RACCOON = "raccoon"         # アライグマ
    WHALE = "whale"             # クジラ
    FROG = "frog"               # カエル
    OWL = "owl"                 # フクロウ
    CAPYBARA = "capybara"       # カピバラ
    MOLE = "mole"               # モグラ
    PENGUIN = "penguin"         # ペンギン
    FOX = "fox"                 # キツネ
    BEAVER = "beaver"           # ビーバー
    BAT = "bat"                 # コウモリ
    ALPACA = "alpaca"           # アルパカ
    FLAMINGO = "flamingo"       # フラミンゴ
    BUTTERFLY = "butterfly"     # 蝶々
    SQUIRREL = "squirrel"       # リス
    MEERKAT = "meerkat"         # ミーアキャット
    ROBOT = "robot"             # ロボット (Voidoll)

class AgeConverter:
    @staticmethod
    def get_emoji(animal_type: str) -> str:
        mapping = {
            AnimalType.DOG_SMALL.value: "🐕",
            AnimalType.DOG_MEDIUM.value: "🐕",
            AnimalType.DOG_LARGE.value: "🦮",
            AnimalType.CAT.value: "🐈",
            AnimalType.RABBIT.value: "🐇",
            AnimalType.HAMSTER.value: "🐹",
            AnimalType.BIRD_SMALL.value: "🐦",
            AnimalType.BIRD_MEDIUM.value: "🦜",
            AnimalType.BIRD_LARGE.value: "🦅",
            AnimalType.TORTOISE.value: "🐢",
            AnimalType.GECKO.value: "🦎",
            AnimalType.ELEPHANT.value: "🐘",
            AnimalType.GIRAFFE.value: "🦒",
            # All-Stars
            AnimalType.RACCOON.value: "🦝",
            AnimalType.WHALE.value: "🐋",
            AnimalType.FROG.value: "🐸",
            AnimalType.OWL.value: "🦉",
            AnimalType.CAPYBARA.value: "🛀", # Onsen Capybara
            AnimalType.MOLE.value: "🕳️", # Mole hole
            AnimalType.PENGUIN.value: "🐧",
            AnimalType.FOX.value: "🦊",
            AnimalType.BEAVER.value: "🦫",
            AnimalType.BAT.value: "🦇",
            AnimalType.ALPACA.value: "🦙",
            AnimalType.FLAMINGO.value: "🦩",
            AnimalType.BUTTERFLY.value: "🦋",
            AnimalType.SQUIRREL.value: "🐿️",
            AnimalType.MEERKAT.value: "🧍", # Standing mammal
            AnimalType.ROBOT.value: "🤖"
        }
        return mapping.get(animal_type, "🐾")

    @staticmethod
    def convert_logic(animal_type: str, total_years: float) -> int:
        # --- Short Lived ---
        if animal_type == AnimalType.BUTTERFLY.value:
            # 寿命数ヶ月〜半年。1ヶ月 = 10歳〜20歳?
            # 1ヶ月=13歳くらいと仮定 (6ヶ月で78歳)
            return int(total_years * 12 * 13)

        if animal_type == AnimalType.MOLE.value:
            # 寿命3-5年 -> 5年で80歳 -> x16
            return int(total_years * 16)

        if animal_type == AnimalType.HAMSTER.value: return int(total_years * 12 * 2.75)

        # --- Medium (Most Mammals) ---
        if animal_type == AnimalType.RABBIT.value:
            if total_years < 1: return int(total_years * 21)
            elif total_years < 2: return 21 + int((total_years - 1) * 6)
            else: return 27 + int((total_years - 2) * 6)

        if animal_type in [AnimalType.DOG_SMALL.value, AnimalType.DOG_MEDIUM.value, AnimalType.DOG_LARGE.value, AnimalType.CAT.value]:
            if total_years <= 1: return int(total_years * 15)
            if total_years <= 2: return 15 + int((total_years - 1) * 9)
            base_age = 24
            years_after_2 = total_years - 2
            if animal_type == AnimalType.DOG_SMALL.value: return base_age + int(years_after_2 * 4)
            elif animal_type == AnimalType.DOG_MEDIUM.value: return base_age + int(years_after_2 * 5)
            elif animal_type == AnimalType.DOG_LARGE.value: return base_age + int(years_after_2 * 7)
            elif animal_type == AnimalType.CAT.value: return base_age + int(years_after_2 * 4)

        if animal_type == AnimalType.FOX.value: return int(total_years * 6) # Dog-like but shorter
        if animal_type == AnimalType.RACCOON.value: return int(total_years * 5) # 寿命20年程度?
        if animal_type == AnimalType.BEAVER.value: return int(total_years * 5.5)
        if animal_type == AnimalType.SQUIRREL.value: return int(total_years * 8)
        if animal_type == AnimalType.MEERKAT.value: return int(total_years * 6.5)
        if animal_type == AnimalType.CAPYBARA.value: return int(total_years * 8) # 寿命10年
        if animal_type == AnimalType.ALPACA.value: return int(total_years * 4.5) # 寿命20年
        if animal_type == AnimalType.FROG.value: return int(total_years * 8) # 寿命10年
        if animal_type == AnimalType.BAT.value: return int(total_years * 4) # 30年とか

        # --- Birds ---
        if animal_type == AnimalType.BIRD_SMALL.value: return int(total_years * 6.6)
        if animal_type == AnimalType.BIRD_MEDIUM.value: return int(total_years * 4.0)
        if animal_type == AnimalType.BIRD_LARGE.value: return int(total_years * 1.6)
        if animal_type == AnimalType.OWL.value: return int(total_years * 4) # Medium bird equiv
        if animal_type == AnimalType.FLAMINGO.value: return int(total_years * 2.5) # 寿命30-40年
        if animal_type == AnimalType.PENGUIN.value: return int(total_years * 4) # 寿命20年

        # --- Reptiles / Long Lived ---
        if animal_type == AnimalType.TORTOISE.value: return int(total_years * 0.8)
        if animal_type == AnimalType.GECKO.value: return int(total_years * 5.3)
        if animal_type == AnimalType.ELEPHANT.value: return int(total_years * 1.15)
        if animal_type == AnimalType.GIRAFFE.value: return int(total_years * 3.2)
        if animal_type == AnimalType.WHALE.value: return int(total_years * 1.0) # Human equiv

        # --- Robot ---
        if animal_type == AnimalType.ROBOT.value:
            # 1年 = 1メジャーアップデート = 人間の10歳分くらいの進化?
            return int(total_years * 10)

        return int(total_years * 7)

    @staticmethod
    def convert(animal_type: str, age_years: int, age_months: int) -> int:
        total_years = age_years + (age_months / 12.0)
        return AgeConverter.convert_logic(animal_type, total_years)

    @staticmethod
    def get_stage(human_age: int) -> str:
        if human_age < 4: return "Baby"
        if human_age < 12: return "Child"
        if human_age < 20: return "Teen"
        if human_age < 40: return "Young Adult"
        if human_age < 60: return "Adult"
        if human_age < 80: return "Senior"
        return "Geriatric"

    @staticmethod
    def get_advice(human_age: int, animal_type: str) -> dict:
        advice = {
            "title": "",
            "care": "",
            "checkup": ""
        }

        # All-Stars Advice
        if animal_type == AnimalType.RACCOON.value:
            advice["title"] = "きれい好きな洗い熊"
            advice["care"] = "手先が器用です。いたずら防止の工夫を。水遊びが大好きです。"
        elif animal_type == AnimalType.WHALE.value:
            advice["title"] = "大海の賢者"
            advice["care"] = "広い心で受け止めましょう。歌（コミュニケーション）を大切に。"
        elif animal_type == AnimalType.FROG.value:
            advice["title"] = "雨上がりの貴公子"
            advice["care"] = "乾燥は大敵です。常に適切な湿度を保ちましょう。皮膚からの吸収が良いので水質管理を徹底。"
        elif animal_type == AnimalType.OWL.value:
            advice["title"] = "森の賢者"
            advice["care"] = "音に敏感です。静かな環境を。夜行性なので夜の時間を一緒に楽しみましょう。"
        elif animal_type == AnimalType.CAPYBARA.value:
            advice["title"] = "癒やしの温泉マスター"
            advice["care"] = "のんびり屋ですが水辺が必要です。温かいお湯を用意してあげると喜びます。"
        elif animal_type == AnimalType.MOLE.value:
            advice["title"] = "地中の建築家"
            advice["care"] = "強い光は苦手です。土の感触を楽しめる環境を。"
        elif animal_type == AnimalType.PENGUIN.value:
            advice["title"] = "氷上のタキシード"
            advice["care"] = "涼しい環境を好みます。足裏の健康チェック（バンブルフット予防）を忘れずに。"
        elif animal_type == AnimalType.FOX.value:
            advice["title"] = "野山のトリックスター"
            advice["care"] = "運動量が多く穴掘りが好きです。退屈させない工夫を。"
        elif animal_type == AnimalType.BEAVER.value:
            advice["title"] = "ダム建設の匠"
            advice["care"] = "歯が伸び続けるので、かじり木は必須です。水遊び場もあるとベスト。"
        elif animal_type == AnimalType.BAT.value:
            advice["title"] = "夜空のパトローラー"
            advice["care"] = "ぶら下がれる場所が必要です。繊細な翼（飛膜）のケアを。"
        elif animal_type == AnimalType.ALPACA.value:
            advice["title"] = "アンデスのアイドル"
            advice["care"] = "定期的な毛刈りが必要です。群れで暮らす動物なので寂しがらせないで。"
        elif animal_type == AnimalType.FLAMINGO.value:
            advice["title"] = "紅のダンサー"
            advice["care"] = "片足立ちはリラックスの証。鏡を置くと仲間がいると思って安心することがあります。"
        elif animal_type == AnimalType.BUTTERFLY.value:
            advice["title"] = "儚き美の象徴"
            advice["care"] = "花の蜜（糖分）がエネルギー源。風の強い日は避難させて。"
        elif animal_type == AnimalType.SQUIRREL.value:
            advice["title"] = "森の貯金箱"
            advice["care"] = "貯食行動（隠す）は本能です。探せる楽しみを作ってあげましょう。"
        elif animal_type == AnimalType.MEERKAT.value:
            advice["title"] = "サバンナの監視員"
            advice["care"] = "穴掘りと日光浴が生きがい。砂場とライトを用意しましょう。"
        elif animal_type == AnimalType.ROBOT.value:
            advice["title"] = "電脳空間の守護者"
            advice["care"] = "バッテリー管理（睡眠）と定期的なメンテナンス（検診）が長持ちの秘訣。バグ（ストレス）は早めに対処。"
        elif animal_type == AnimalType.ELEPHANT.value:
            advice["title"] = "賢き巨象"
            advice["care"] = "非常に高い知能と感情を持ちます。人間と同じように複雑な社会生活を送っています。"
        elif animal_type == AnimalType.GIRAFFE.value:
            advice["title"] = "サバンナの展望台"
            advice["care"] = "長い首と脚への負担に注意。滑りにくい床材が必須です。"
        elif animal_type == AnimalType.TORTOISE.value:
            advice["title"] = "のんびり亀時間"
            advice["care"] = "非常に寿命が長いです。日光浴で甲羅の形成に必要なカルシウム代謝を促しましょう。"

        # PT (理学療法士) 視点のアドバイス定型文 (Shared)
        pt_baby = "【PT視点】骨格形成の大事な時期。滑りやすいフローリングは関節形成不全のリスクになります。カーペットなどで足元を安定させましょう。"
        pt_active = "【PT視点】筋肉量維持のため、平坦な道だけでなく、適度な坂道や砂利道など多様な地面を歩かせ、深層筋（インナーマッスル）を刺激しましょう。"
        pt_senior = "【PT視点】関節可動域が狭くなりがちです。無理のない範囲でのストレッチや、温湿布（ホットパック）で血流を促してから動くのがおすすめ。"
        pt_geriatric = "【PT視点】寝返りが減ると床ずれ（褥瘡）のリスクがあります。2-3時間ごとの体位変換や、体圧分散マットの導入を検討してください。"

        # Apply Shared Logic if specific one is empty
        if not advice["care"]:
            if human_age < 20: advice["care"] = "成長期です。栄養バランスに気をつけましょう。"
            elif human_age < 60: advice["care"] = "活動的な時期です。"
            else: advice["care"] = "ゆっくり過ごさせてあげましょう。"

        # Add Checkup (Generic + PT)
        if not advice["checkup"]:
             if human_age < 20: advice["checkup"] = f"成長チェックを。{pt_baby}"
             elif human_age < 60: advice["checkup"] = f"健康診断を定期的に。{pt_active}"
             else: advice["checkup"] = f"体の変化に注意。{pt_senior}"

        # Additional adjustments
        if animal_type == AnimalType.DOG_LARGE.value and human_age > 30:
            advice["checkup"] += " 特に大型犬は股関節への負担が大きいため、体重管理は理学療法の観点からも必須です。"

        return advice

    @staticmethod
    def get_fluffiness(animal_type: str, human_age: int) -> dict:
        score = 80
        label = "モフモフ度"
        comment = "いい感じの肌触り。"

        if animal_type in [AnimalType.DOG_SMALL.value, AnimalType.DOG_MEDIUM.value, AnimalType.DOG_LARGE.value, AnimalType.CAT.value]:
            if human_age < 10: score, comment = 120, "爆発的なモフみ！"
            elif human_age < 60: score, comment = 85, "安定した上質な手触り。"
            else: score, comment = 95, "長年の貫禄が滲み出る奇跡の毛並み。"

        elif animal_type == AnimalType.RABBIT.value: score, comment = 200, "冬毛モード発動中？圧倒的な綿毛感。"
        elif animal_type == AnimalType.HAMSTER.value: score, comment = 100, "手のひらサイズの高密度モフ。"
        elif animal_type == AnimalType.ALPACA.value: score, comment = 300, "高級ニット級の極上モフ。"
        elif animal_type == AnimalType.FOX.value: score, comment = 150, "冬の襟巻きにしたくなる暖かさ。"
        elif animal_type == AnimalType.RACCOON.value: score, comment = 110, "洗いたてのタオルのようなふんわり感。"
        elif animal_type == AnimalType.SQUIRREL.value: # Tail
            label = "しっぽのふさふさ度"
            score, comment = 120, "本体より大きいかもしれない存在感。"
        elif animal_type == AnimalType.OWL.value:
            label = "フェザー度"
            score, comment = 100, "音もなく飛べるシルクタッチ。"
        elif animal_type in [AnimalType.BIRD_SMALL.value, AnimalType.BIRD_MEDIUM.value, AnimalType.BIRD_LARGE.value]:
            label = "フェザー度"
            score, comment = 100, "シルクのような極上の羽ざわり。"
        elif animal_type == AnimalType.PENGUIN.value:
            label = "弾力性"
            score, comment = 100, "水を弾く最高級のラバースーツ感。"
        elif animal_type == AnimalType.CAPYBARA.value:
            label = "タワシ度"
            score, comment = 100, "意外と硬い毛並み。それがまた良い。"
        elif animal_type == AnimalType.BEAVER.value:
            label = "防水性"
            score, comment = 100, "水陸両用の高機能ボディ。"
        elif animal_type == AnimalType.FROG.value:
            label = "潤い度"
            score, comment = 200, "吸い付くような美肌。"
        elif animal_type == AnimalType.ROBOT.value:
            label = "メカメカ度"
            score, comment = 100, "冷たくて硬い金属の質感。最高にかっこいい。"
        elif animal_type == AnimalType.BUTTERFLY.value:
            label = "鱗粉度"
            score, comment = 999, "触ると取れちゃうので見るだけにしてね。"
        elif animal_type == AnimalType.ELEPHANT.value:
            label = "頼もしさ"
            score, comment = 500, "背中に乗りたくなる安心感。"
        elif animal_type == AnimalType.GIRAFFE.value:
            label = "まつげ力"
            score, comment = 100, "誰よりも長いまつげが魅力的。"
        elif animal_type in [AnimalType.TORTOISE.value, AnimalType.GECKO.value]:
            label = "つるつる・硬度"
            score, comment = 100, "この質感こそ至高。"

        return {"label": label, "score": score, "comment": comment}

class CalculateRequest(BaseModel):
    animal_type: str
    age_years: int
    age_months: int = 0

@router.post("/api/retriever/calculate")
async def calculate_age(request: CalculateRequest):
    human_age = AgeConverter.convert(request.animal_type, request.age_years, request.age_months)
    stage = AgeConverter.get_stage(human_age)
    advice = AgeConverter.get_advice(human_age, request.animal_type)
    emoji = AgeConverter.get_emoji(request.animal_type)
    fluffiness = AgeConverter.get_fluffiness(request.animal_type, human_age)

    return {
        "human_age": human_age,
        "stage": stage,
        "advice": advice,
        "emoji": emoji,
        "fluffiness": fluffiness
    }
