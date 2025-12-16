from app import app

application = app

print("✅ WSGI cargado. Rutas:", app.url_map)