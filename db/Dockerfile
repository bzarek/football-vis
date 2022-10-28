# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8-slim-buster

# Copy local code to the container image.
ENV APP_HOME /app
ENV PYTHONUNBUFFERED True
WORKDIR $APP_HOME

# Install cron
RUN apt-get update && apt-get install cron -y

# Install Python dependencies and Gunicorn
ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN groupadd -r app && useradd -r -g app app

# Copy the rest of the codebase into the image
COPY --chown=app:app ./db ./

# create data directory with correct permissions for app
RUN mkdir /app/data && chown app /app/data
RUN chmod -R g+rwx /app/data 
RUN chmod g+s /app/data

# setup cronjob 
RUN crontab cronfile

# start cron
CMD env >> /etc/environment && exec cron -f
