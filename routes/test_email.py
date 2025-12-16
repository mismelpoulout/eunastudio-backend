from flask import Blueprint, jsonify
from utils.email_sender import send_verification_email

test_email = Blueprint("test_email", __name__)

@test_email.route("/test-email", methods=["GET"])
def test_email_endpoint():
    ok = send_verification_email(
        "medstudioparato2@gmail.com",
        "123456"
    )

    if ok:
        return jsonify({"msg": "Email enviado correctamente"}), 200
    else:
        return jsonify({"msg": "Fallo enviando email"}), 500