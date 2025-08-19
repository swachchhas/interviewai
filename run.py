# run.py 

from app import create_app  # your __init__.py should have create_app()

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
