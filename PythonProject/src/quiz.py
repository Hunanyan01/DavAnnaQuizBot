import json

# Ներած՝ JSON ֆայլ կամ տվյալ
questions = [
    {
        "id": 2,
        "topic": "Java",
        "question": "Ի՞նչ է անում final keyword-ը class-ի վրա օգտագործելու դեպքում։",
        "options": [
            "Նշում է, որ class-ը չպետք է ունենա constructor",
            "Նշում է, որ class-ից հնարավոր չէ ստեղծել օբյեկտ",
            "Նշում է, որ class-ը չի կարող ժառանգվել",
            "Նշում է, որ class-ը չի կարող ունենալ static method"
        ],
        "correct": 3,
        "explanations": {
            "1": "⚠️ Constructor-ը class-ի մաս է և final-ը չի արգելում դա։",
            "2": "⚠️ Օբյեկտ ստեղծելը թույլատրված է final class-ից։",
            "4": "⚠️ Static մեթոդը կապ չունի final-ի հետ։",
            "3": "✅ Ճիշտ է։ Final class-ը չի կարող ժառանգվել։"
        },
        "short_explanation": "🔒 final class-երը փակ են ժառանգման համար։"
    }
]

# Ֆունկցիա՝ հարցը տպելու համար
def display_question(q):
    print(f"❓ {q['question']}\n")
    for i, option in enumerate(q['options'], start=1):
        print(f"{i}️⃣ {option}")
    print("\n👉 Պատասխանիր միայն թիվը (օր.՝ 3)\n")

# Ֆունկցիա՝ պատասխանը ստուգելու համար
def check_answer(q, answer):
    correct = str(q["correct"])
    explanation = q["explanations"].get(str(answer), "❌ Սխալ տարբերակ։")
    print("\n📣 Պատասխանդ՝", "Ճիշտ է ✅" if str(answer) == correct else "Սխալ ❌")
    print(explanation)
    print("\n📌", q["short_explanation"])

# Օգտագործում
display_question(questions[0])
user_answer = input("✍️ Քո պատասխանը: ")
check_answer(questions[0], user_answer)
