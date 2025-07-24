FROM python:3.10-slim

# install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# copy files
COPY . .

# expose port
EXPOSE 8050

# run python
CMD ["python", "run_app.py"]