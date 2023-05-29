# book-blog-
Book Blog, created using Flask

https://www.robertsrandomreviews.com/

STEPS TO RUN LOCALLY:

1. Make sure you are using Python 3.8

2. In the terminal of the project directory (or VS Code terminal), run:
- Mac/Linux: ```. .venv/bin/activate```
- Windows: ```.venv\Scripts\activate```

3. In your .venv environment, run ```pip install -r requirements.txt```

4. In a seperate terminal session, run: ```npx tailwindcss -i ./bookblog/static/stylesheet.css -o ./bookblog/static/output.css --watch```

5. Set secret key, Google auth credentials, and master email in __init__.py and routes.py
- Get google auth credentials from the Google Cloud Console.
- Should be under auth credentials.

6. In your .venv environment, run ```python run.py```

7. In the future, you ONLY need to run step 4 if you want to make CSS changes, but step 2 and 6 is mandatory. All other steps can be ignored!

7. You're done! Enjoy! Please put a PR if you want to contribute! Insert an issue if there are any issues configuring.