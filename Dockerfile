FROM openjdk:slim

COPY --from=python:3.7 / /

# Set the working directory to /app
WORKDIR /app

# COPY requirements to /app dir
COPY requirements.txt /app

# COPY enelvo to /app dir
COPY enelvo/ /app/enelvo/

# COPY sentistrength to /app dir
COPY sentistrength/ /app/sentistrength/

# COPY sentistrength to /app dir
COPY sentimento.py /app

# Install required packages
RUN pip3 install -r requirements.txt
RUN python3 -c "import nltk;nltk.download('punkt')"

# Set the default run command
CMD python3 sentimento.py


