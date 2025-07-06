from app import create_app

app = create_app()

if __name__ == "__main__":
   import os
   port = int(os.environ.get("PORT", 5000))  # ✅ Use this instead of hardcoded 10000
   app.run(host="0.0.0.0", port=port)
