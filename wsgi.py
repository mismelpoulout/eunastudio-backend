from app import create_app

app = create_app()

print("✅ WSGI cargado. Rutas:", app.url_map)