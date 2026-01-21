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
    BIRD_SMALL = "bird_small"   # セキセイインコ等 (寿命10-15年)
    BIRD_MEDIUM = "bird_medium" # オカメインコ等 (寿命15-25年)
    BIRD_LARGE = "bird_large"   # オウム等 (寿命50年〜)

class AgeConverter:
    @staticmethod
    def convert_logic(animal_type: str, total_years: float) -> int:
        """
        メイン計算ロジック (入力は年単位の小数)
        """
        # --- ハムスター (特殊: 1ヶ月=2.6歳換算) ---
        if animal_type == AnimalType.HAMSTER.value:
            # 寿命2.5〜3年 -> 人間80歳
            # 3年(36ヶ月) = 80歳 -> 1ヶ月 約2.2歳
            # ユーザー指定: 1ヶ月 = 2.5〜3歳 -> 間をとって2.75歳/月とする
            months = total_years * 12
            return int(months * 2.75)

        # --- うさぎ (21-6ルール) ---
        if animal_type == AnimalType.RABBIT.value:
            # 1年=21, 2年=27 (+6), 以降+6
            if total_years < 1:
                return int(total_years * 21) # 1歳未満は比例
            elif total_years < 2:
                # 1歳〜2歳: 21 + (経過分 * 6)
                return 21 + int((total_years - 1) * 6)
            else:
                # 2歳以降: 27 + (経過分 * 6)
                return 27 + int((total_years - 2) * 6)

        # --- 犬・猫 (基本の15-9-4ルール派生) ---
        if animal_type in [AnimalType.DOG_SMALL.value, AnimalType.DOG_MEDIUM.value, AnimalType.DOG_LARGE.value, AnimalType.CAT.value]:

            # 1年目: 15歳
            if total_years <= 1:
                return int(total_years * 15)

            # 2年目: +9歳 (計24歳)
            if total_years <= 2:
                return 15 + int((total_years - 1) * 9)

            # 3年目以降
            base_age = 24
            years_after_2 = total_years - 2

            if animal_type == AnimalType.DOG_SMALL.value:
                return base_age + int(years_after_2 * 4)
            elif animal_type == AnimalType.DOG_MEDIUM.value:
                return base_age + int(years_after_2 * 5)
            elif animal_type == AnimalType.DOG_LARGE.value:
                return base_age + int(years_after_2 * 7)
            elif animal_type == AnimalType.CAT.value:
                return base_age + int(years_after_2 * 4)

        # --- 鳥類 (寿命比率計算) ---
        # 人間の寿命80年として計算
        if animal_type == AnimalType.BIRD_SMALL.value:
            # 寿命約12年 -> 80/12 = 6.6倍
            return int(total_years * 6.6)

        if animal_type == AnimalType.BIRD_MEDIUM.value:
            # 寿命約20年 -> 80/20 = 4倍
            return int(total_years * 4.0)

        if animal_type == AnimalType.BIRD_LARGE.value:
            #ヨウム・大型オウム 寿命50年〜 -> 1.5〜2倍程度
            # 大型は成長が遅い。
            # 幼鳥期間を加味するか比例かの議論はあるが、シンプルに
            return int(total_years * 1.6)

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

        # --- ハムスター特別アドバイス ---
        if animal_type == AnimalType.HAMSTER.value:
            if human_age < 20:
                advice["title"] = "エネルギッシュな活動期"
                advice["care"] = "回し車でたくさん走る時期です。タンパク質を多めに。"
            elif human_age < 50:
                advice["title"] = "落ち着きのある大人"
                advice["care"] = "少し寝る時間が増えるかも。おやつのあげすぎに注意。"
            else:
                advice["title"] = "のんびりシニアライフ"
                advice["care"] = "段差をなくし、温度管理を厳密に。柔らかいペレットに変えてあげるのも良いでしょう。"
                advice["checkup"] = "腫瘍などができやすい時期です。しこりがないかスキンシップで確認を。"
            return advice

        # --- 一般アドバイス (犬猫兎鳥) ---
        if human_age < 12: # 子供時代
            advice["title"] = "遊び盛りのわんぱく期"
            advice["care"] = "好奇心旺盛で何でも吸収する時期です。しつけや社会化に最適なタイミング。信頼関係を築きましょう。"
            advice["checkup"] = "成長期なので、定期的な体重測定とワクチンの接種スケジュールを確認しましょう。"
        elif human_age < 20: # 青春期
            advice["title"] = "反抗期も愛おしい青春期"
            advice["care"] = "自我が芽生え、少し活発すぎることも。運動不足にならないようたっぷり遊びを取り入れましょう。"
        elif human_age < 40: # 青年期
            advice["title"] = "心身ともに充実したベストパートナー"
            advice["care"] = "体力・知力ともにピークの状態です。一緒に新しいことに挑戦するのも良いでしょう。"
            advice["checkup"] = "今の健康状態を基準値として記録しておくと、将来の変化に気づきやすくなります。"
        elif human_age < 60: # 壮年期
            advice["title"] = "落ち着きが出てきた熟年期"
            advice["care"] = "少しずつ代謝が落ちてきます。食事の量や質を見直し、肥満に気をつけましょう。"
            advice["checkup"] = "目や歯のチェックを念入りに。定期的な検診が理想的です。"
        elif human_age < 80: # シニア期
            advice["title"] = "のんびり過ごすシニアライフ"
            advice["care"] = "寝ている時間が増えてきます。寝床を快適にし、室内の段差を減らすなどのバリアフリー対策を。"
            advice["checkup"] = "血液検査など、定期的なドックを活用して病気の早期発見を。"
        else: # 高齢期
            advice["title"] = "寄り添う時間が宝物の長寿期"
            advice["care"] = "感覚器官が衰えているかもしれません。急に触れず、優しく声をかけてから接しましょう。日々の穏やかな時間を大切に。"
            advice["checkup"] = "無理な通院は避けつつ、痛みや苦しみのないケアを獣医師と相談しましょう。"

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
