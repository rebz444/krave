# Use an ARMv7 (32-bit) Raspbian Bullseye base image
FROM debian:bullseye

# Set environment variables to avoid some interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-tk python3-pygame python3-pil \
    python3-numpy python3-scipy python3-pandas python3-matplotlib \
    python3-setuptools git libjpeg-dev zlib1g-dev libfreetype6-dev \
    libopenjp2-7 libtiff5 \
    && apt-get clean

# Install x11-apps for testing XQuartz
RUN apt-get update && apt-get install -y x11-apps

# Set up a working directory
WORKDIR /app

# Copy your code into the container
COPY . /app

# Install Python dependencies
RUN pip3 install --upgrade pip setuptools wheel
# RUN pip3 install -r requirements.txt

# Default command (change as needed)
CMD ["python3", "-m", "krave.ui.ui"]