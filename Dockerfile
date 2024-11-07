FROM xeden3/docker-office-python-core:v1

# Install dependencies
RUN apt-get update && apt-get install -y \
    xvfb \
    wine \
    python3-pip \
    locales \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for the Linux environment
RUN pip install fastapi uvicorn python-multipart

# Configure locale
RUN sed -i -e 's/# zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=zh_CN.UTF-8
ENV LC_ALL=zh_CN.UTF-8

# Set up Wine
ENV WINEARCH=win32
ENV WINEPREFIX=/opt/wineprefix
RUN mkdir -p /opt/wineprefix/drive_c/uploads && \
    winecfg

# Download and install Python for Windows under Wine
RUN wget https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe && \
    xvfb-run wine python-3.8.10.exe /quiet InstallAllUsers=1 PrependPath=1 && \
    rm python-3.8.10.exe

# Install pywin32 using Wine's Python pip
RUN xvfb-run wine pip install pywin32==228

# Working directory
WORKDIR /opt/wineprefix/drive_c/

# Copy application files
COPY ./app /opt/wineprefix/drive_c/app/

# Expose port
EXPOSE 8000

# Create a startup script
RUN echo '#!/bin/bash\n\
xvfb-run -a uvicorn app.main:app --host 0.0.0.0 --port 8000' > /start.sh && \
chmod +x /start.sh

# Command to run the FastAPI application
CMD ["/start.sh"]