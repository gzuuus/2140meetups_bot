FROM python:3.9 
# run this before copying requirements for cache efficiency
RUN pip install --upgrade pip
#set work directory early so remaining paths can be relative
WORKDIR /app
# Adding requirements file to current directory
# just this file first to cache the pip install step when code changes
COPY bot/requirements.txt .
#install dependencies
RUN pip install -r requirements.txt
# copy code itself from context to image
ADD ./bot /app
# Use unbuffered output
# link: https://github.com/moby/moby/issues/12447#issuecomment-263846539
CMD ["python3", "-u", "main.py"]