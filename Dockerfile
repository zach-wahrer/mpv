FROM python:3.6
WORKDIR /user/src/mpv

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

EXPOSE 5000

CMD gunicorn --workers=3 --bind 0.0.0.0:5000 app:create_app\(\)
