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
    BIRD_SMALL = "bird_small"   # セキセイインコ等
    BIRD_MEDIUM = "bird_medium" # オカメインコ等
    BIRD_LARGE = "bird_large"   # オウム等

    # New Zoo Animals
    TORTOISE = "tortoise"       # 寿命100年〜 リクガメ
    GECKO = "gecko"             # 寿命10-15年 レオパなど
    ELEPHANT = "elephant"       # 寿命60-70年
    GIRAFFE = "giraffe"         # 寿命25年

class AgeConverter:
    @staticmethod
    def convert_logic(animal_type: str, total_years: float) -> int:
        """
        メイン計算ロジック (入力は年単位の小数)
        """
        # --- ハムスター (特殊: 1ヶ月=2.6歳換算) ---
        if animal_type == AnimalType.HAMSTER.value:
            months = total_years * 12
            return int(months * 2.75)

        # --- うさぎ (21-6ルール) ---
        if animal_type == AnimalType.RABBIT.value:
            if total_years < 1: return int(total_years * 21)
            elif total_years < 2: return 21 + int((total_years - 1) * 6)
            else: return 27 + int((total_years - 2) * 6)

        # --- 犬・猫 (基本の15-9-4ルール派生) ---
        if animal_type in [AnimalType.DOG_SMALL.value, AnimalType.DOG_MEDIUM.value, AnimalType.DOG_LARGE.value, AnimalType.CAT.value]:
            if total_years <= 1: return int(total_years * 15)
            if total_years <= 2: return 15 + int((total_years - 1) * 9)

            base_age = 24
            years_after_2 = total_years - 2

            if animal_type == AnimalType.DOG_SMALL.value: return base_age + int(years_after_2 * 4)
            elif animal_type == AnimalType.DOG_MEDIUM.value: return base_age + int(years_after_2 * 5)
            elif animal_type == AnimalType.DOG_LARGE.value: return base_age + int(years_after_2 * 7)
            elif animal_type == AnimalType.CAT.value: return base_age + int(years_after_2 * 4)

        # --- 鳥類 ---
        if animal_type == AnimalType.BIRD_SMALL.value: return int(total_years * 6.6)
        if animal_type == AnimalType.BIRD_MEDIUM.value: return int(total_years * 4.0)
        if animal_type == AnimalType.BIRD_LARGE.value: return int(total_years * 1.6)

        # --- 爬虫類 ---
        if animal_type == AnimalType.TORTOISE.value:
            # 寿命100年〜 -> 人間より少し遅いペース (0.8倍くらい)
            return int(total_years * 0.8)

        if animal_type == AnimalType.GECKO.value:
            # 寿命15年 -> 犬と同じくらい、または少し早い (15年で80歳 -> 5.3倍)
            return int(total_years * 5.3)

        # --- 動物園 ---
        if animal_type == AnimalType.ELEPHANT.value:
            # 寿命60-70年 -> 人間より少し早い (70年で80歳 -> 1.14倍)
            return int(total_years * 1.15)

        if animal_type == AnimalType.GIRAFFE.value:
            # 寿命25年 -> 25年で80歳 -> 3.2倍
            return int(total_years * 3.2)

        return int(total_years * 7) # Fallback

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

        # --- 個別アドバイス ---
        if animal_type == AnimalType.TORTOISE.value:
            advice["title"] = "のんびり亀時間"
            advice["care"] = "非常に寿命が長いです。人間が先に寿命を迎える可能性があるため、次世代へ託す準備も視野に入れましょう。"
            return advice

        if animal_type == AnimalType.ELEPHANT.value:
            advice["title"] = "賢き巨象"
            advice["care"] = "非常に高い知能と感情を持ちます。人間と同じように複雑な社会生活を送っています。"
            return advice

        # --- 汎用アドバイス (再利用) ---
        if human_age < 20:
            advice["title"] = "成長期"
            advice["care"] = "体を作る大切な時期です。"
        elif human_age < 50:
            advice["title"] = "充実期"
            advice["care"] = "活発に活動できる時期です。"
        else:
            advice["title"] = "シニア期"
            advice["care"] = "穏やかに過ごせる環境を整えましょう。"

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

    return {
        "human_age": human_age,
        "stage": stage,
        "advice": advice
    }
