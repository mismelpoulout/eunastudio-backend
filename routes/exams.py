import json
import os
from flask import Blueprint, request, jsonify

from exams.exam_generator import generate_personalized_exam

exams_bp = Blueprint("exams", __name__)

# --------------------------------------------------
# 📥 Cargar questions.json UNA sola vez
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_PATH = os.path.join(BASE_DIR, "data", "questions.json")

with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)


# --------------------------------------------------
# 🧠 EXAMEN PERSONALIZADO CON IA
# --------------------------------------------------
@exams_bp.route("/personalized", methods=["POST"])
def personalized_exam():
    """
    Body opcional:
    {
      "history": [
        {
          "especialidad": "Medicina Interna",
          "correctas": 20,
          "totalPreguntas": 40
        }
      ]
    }
    """

    data = request.get_json(silent=True) or {}
    history = data.get("history", [])

    exam = generate_personalized_exam(history, QUESTIONS)

    return jsonify({
        "type": "personalized_ai",
        "total": len(exam),
        "questions": exam
    })