FROM python:3

COPY requirements.txt .

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

RUN apt-get update \
    && apt-get upgrade -y \
    # && apt-get install -y libgl1-mesa-dev \
    # && apt-get install -y libglib2.0-0 \
    && pip install --upgrade pip \
    && pip install setuptools

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /src
COPY /src /src