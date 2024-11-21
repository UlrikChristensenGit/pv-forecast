FROM python:3.10-slim

# install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# copy files
COPY . .

# run python
CMD ["python", "run_versioned_nwp.py"]