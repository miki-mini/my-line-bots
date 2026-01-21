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
            AnimalType.GIRAFFE.value: "🦒"
        }
        return mapping.get(animal_type, "🐾")

    @staticmethod
    def convert_logic(animal_type: str, total_years: float) -> int:
        if animal_type == AnimalType.HAMSTER.value: return int(total_years * 12 * 2.75)

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

        if animal_type == AnimalType.BIRD_SMALL.value: return int(total_years * 6.6)
        if animal_type == AnimalType.BIRD_MEDIUM.value: return int(total_years * 4.0)
        if animal_type == AnimalType.BIRD_LARGE.value: return int(total_years * 1.6)
        if animal_type == AnimalType.TORTOISE.value: return int(total_years * 0.8)
        if animal_type == AnimalType.GECKO.value: return int(total_years * 5.3)
        if animal_type == AnimalType.ELEPHANT.value: return int(total_years * 1.15)
        if animal_type == AnimalType.GIRAFFE.value: return int(total_years * 3.2)

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

        # PT (理学療法士) 視点のアドバイス定型文
        pt_baby = "【PT視点】骨格形成の大事な時期。滑りやすいフローリングは関節形成不全のリスクになります。カーペットなどで足元を安定させましょう。"
        pt_active = "【PT視点】筋肉量維持のため、平坦な道だけでなく、適度な坂道や砂利道など多様な地面を歩かせ、深層筋（インナーマッスル）を刺激しましょう。"
        pt_senior = "【PT視点】関節可動域が狭くなりがちです。無理のない範囲でのストレッチや、温湿布（ホットパック）で血流を促してから動くのがおすすめ。"
        pt_geriatric = "【PT視点】寝返りが減ると床ずれ（褥瘡）のリスクがあります。2-3時間ごとの体位変換や、体圧分散マットの導入を検討してください。"

        # --- 個別 & PTアドバイス ---
        if animal_type == AnimalType.TORTOISE.value:
            advice["title"] = "のんびり亀時間"
            advice["care"] = "非常に寿命が長いです。日光浴で甲羅の形成に必要なカルシウム代謝を促しましょう。"
            advice["checkup"] = f"代謝がゆっくりです。食欲変化は数日遅れて現れることも。{pt_senior if human_age > 60 else ''}"
            return advice

        if animal_type == AnimalType.HAMSTER.value:
            # ハムスター
            if human_age < 20:
                advice["title"] = "エネルギッシュ期"
                advice["care"] = "回し車は脊柱への負担が少ない、直径が十分にあるものを選びましょう。"
                advice["checkup"] = "活発すぎる時期の怪我に注意。"
            elif human_age < 50:
                advice["title"] = "安定期"
                advice["care"] = "適度な運動を。"
            else:
                advice["title"] = "シニアライフ"
                advice["care"] = "段差をなくしバリアフリーに。"
                advice["checkup"] = f"腫瘍チェックだけでなく、歩き方の左右差も観察を。{pt_senior}"
            return advice

        # --- 汎用 (犬猫兎鳥) + PT ---
        if human_age < 12:
            advice["title"] = "遊び盛りのわんぱく期"
            advice["care"] = "好奇心お旺盛な時期。たくさん遊びましょう。"
            advice["checkup"] = f"成長期です。{pt_baby}"
        elif human_age < 20:
            advice["title"] = "青春期"
            advice["care"] = "運動量が最大になる時期です。"
            advice["checkup"] = f"運動器のトラブルがないか確認を。{pt_active}"
        elif human_age < 40:
            advice["title"] = "ベストパートナー期"
            advice["care"] = "体力知力ともに充実しています。"
            advice["checkup"] = f"今の動きを動画に撮っておくと、将来の変化に気づけます。{pt_active}"
        elif human_age < 60:
            advice["title"] = "熟年期"
            advice["care"] = "代謝が落ちてきます。肥満は関節の敵です。"
            advice["checkup"] = f"立ち上がり動作が遅くなっていないかチェックを。{pt_active}"
        elif human_age < 80:
            advice["title"] = "シニアライフ"
            advice["care"] = "寝ている時間が増えます。室温管理を徹底しましょう。"
            advice["checkup"] = f"定期的な検診を。{pt_senior}"
        else:
            advice["title"] = "長寿期"
            advice["care"] = "穏やかな時間を大切に。"
            advice["checkup"] = f"痛みのないケアを。{pt_geriatric}"

        # 大型犬の関節ケア強化
        if animal_type == AnimalType.DOG_LARGE.value and human_age > 30:
            advice["checkup"] += " 特に大型犬は股関節への負担が大きいため、体重管理は理学療法の観点からも必須です。"

        return advice

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

    return {
        "human_age": human_age,
        "stage": stage,
        "advice": advice,
        "emoji": emoji
    }
