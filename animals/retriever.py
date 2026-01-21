from fastapi import APIRouter
from pydantic import BaseModel
from enum import Enum

router = APIRouter()

class AnimalType(Enum):
    DOG_SMALL = "dog_small"
    DOG_MEDIUM = "dog_medium"
    DOG_LARGE = "dog_large"
    CAT = "cat"
    RABBIT = "rabbit"

class AgeConverter:
    @staticmethod
    def convert(animal_type: str, age_years: int) -> int:
        """
        動物の年齢を人間に換算します。
        """
        if animal_type == AnimalType.DOG_SMALL.value:
            if age_years == 0: return 0
            if age_years == 1: return 15
            if age_years == 2: return 24
            return 24 + (age_years - 2) * 4

        elif animal_type == AnimalType.DOG_MEDIUM.value:
            if age_years == 0: return 0
            if age_years == 1: return 15
            if age_years == 2: return 24
            return 24 + (age_years - 2) * 5

        elif animal_type == AnimalType.DOG_LARGE.value:
            if age_years == 0: return 0
            if age_years == 1: return 12
            if age_years == 2: return 22
            return 22 + (age_years - 2) * 7

        elif animal_type == AnimalType.CAT.value:
            if age_years == 0: return 0
            if age_years == 1: return 15
            if age_years == 2: return 24
            return 24 + (age_years - 2) * 4

        elif animal_type == AnimalType.RABBIT.value:
            # うさぎの年齢換算（一般的な目安）
            if age_years == 0: return 0
            if age_years == 1: return 20
            if age_years == 2: return 28
            return 28 + (age_years - 2) * 6

        return age_years * 7 # fallback

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

        # 基本的なアドバイス生成（年齢ベース）
        if human_age < 12: # 子供時代
            advice["title"] = "遊び盛りのわんぱく期"
            advice["care"] = "好奇心旺盛で何でも吸収する時期です。トイレトレーニングや社会化に最適なタイミング。たくさん遊んで信頼関係を築きましょう。"
            advice["checkup"] = "ワクチンの接種スケジュールを確認しましょう。"
        elif human_age < 20: # 青春期
            advice["title"] = "反抗期も愛おしい青春期"
            advice["care"] = "自我が芽生え、少し反抗的になることも。根気強くコミュニケーションを取り、運動不足にならないようたっぷり散歩や遊びを取り入れましょう。"
            advice["checkup"] = "年に1回の健康診断を習慣づけ始めましょう。"
        elif human_age < 40: # 青年期
            advice["title"] = "心身ともに充実したベストパートナー"
            advice["care"] = "体力・知力ともにピークの状態です。新しいコマンドを覚えたり、少し遠出をしたり、アクティブな活動を楽しみましょう。食事のカロリー管理も大切に。"
            advice["checkup"] = "今の健康状態を基準値として記録しておくと、将来の変化に気づきやすくなります。"
        elif human_age < 60: # 壮年期
            advice["title"] = "落ち着きが出てきた熟年期"
            advice["care"] = "少しずつ代謝が落ちてきます。食事の量や質を見直し、肥満に気をつけましょう。関節への負担を減らすため、激しい運動は控えめに。"
            advice["checkup"] = "目や歯のチェックを念入りに。半年に1回の検診が理想的です。"
        elif human_age < 80: # シニア期
            advice["title"] = "のんびり過ごすシニアライフ"
            advice["care"] = "寝ている時間が増えてきます。寝床を快適にし、室内の段差を減らすなどのバリアフリー対策を。寒暖差にも敏感になるので、室温管理を徹底しましょう。"
            advice["checkup"] = "血液検査やレントゲンなど、定期的なドックを活用して病気の早期発見を。関節ケアのサプリメントも検討時期です。"
        else: # 高齢期
            advice["title"] = "寄り添う時間が宝物の長寿期"
            advice["care"] = "視力や聴力が衰えているかもしれません。急に触れず、優しく声をかけてから接しましょう。食事は消化に良いものを少しずつ。日々の穏やかな時間を大切に。"
            advice["checkup"] = "無理な通院は避けつつ、獣医師と相談しながら痛みや苦しみのないケアを最優先しましょう。"

        # 大型犬への配慮
        if animal_type == AnimalType.DOG_LARGE.value and human_age > 40:
             advice["care"] += " 特に大型犬は関節への負担が大きいため、滑りにくい床材への変更をお勧めします。"

        return advice

class CalculateRequest(BaseModel):
    animal_type: str
    age_years: int

@router.post("/api/retriever/calculate")
async def calculate_age(request: CalculateRequest):
    human_age = AgeConverter.convert(request.animal_type, request.age_years)
    stage = AgeConverter.get_stage(human_age)
    advice = AgeConverter.get_advice(human_age, request.animal_type)

    return {
        "human_age": human_age,
        "stage": stage,
        "advice": advice
    }
