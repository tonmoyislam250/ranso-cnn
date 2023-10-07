FROM python:3.7.9-slim-buster
WORKDIR /code/
COPY req.txt /code/
RUN pip install --upgrade pip
RUN pip install -r req.txt
COPY components/ /code/components/
COPY scripts/ /code/scripts/
COPY main.py README.md /code/
RUN pip install uvicorn
CMD ["uvicorn", "main:app", "--host","localhost","--port","8000"]