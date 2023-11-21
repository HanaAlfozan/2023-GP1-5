FROM python:3.11.4
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install opencv-python