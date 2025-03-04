# Use the official Apache Flink image as the base
FROM flink:latest

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Copy the requirements file and install dependencies
COPY requirements.txt /opt/flink/requirements.txt
RUN pip3 install -r /opt/flink/requirements.txt

# Copy your PyFlink job script
COPY flink_job.py /opt/flink/flink_job.py

# Set the working directory
WORKDIR /opt/flink

# Set the entrypoint to run the Flink job
ENTRYPOINT ["python3", "flink_job.py"]