
FROM python:3.11

ADD main.py .

WORKDIR /maaser

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

#ENV NAME configy.env

# Make ports available to the world outside this container
EXPOSE 5000 6000 6001 6002 6003 6004 6005

# Run main.py when the container launches
CMD ["python", "main.py"]

