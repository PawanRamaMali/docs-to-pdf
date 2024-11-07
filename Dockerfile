FROM xeden3/docker-office-python-core:v1

# Install FastAPI dependencies
RUN apt-get update && apt-get install -y python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install fastapi uvicorn python-multipart

# Initialize Wine and install pywin32 in Wine Python
RUN wineboot --init && \
    wget https://github.com/mhammond/pywin32/releases/download/b228/pywin32-228.win32-py3.8.exe && \
    xvfb-run wine easy_install pywin32-228.win32-py3.8.exe && \
    rm pywin32-228.win32-py3.8.exe

WORKDIR /opt/wineprefix/drive_c/

# Copy application files
COPY app/ /opt/wineprefix/drive_c/app/

# Create entrypoint script
RUN echo '#!/bin/bash\n\
xvfb-run -a uvicorn app.main:app --host 0.0.0.0 --port 8000' > /entrypoint.sh && \
chmod +x /entrypoint.sh

# Run the FastAPI application
ENTRYPOINT ["/entrypoint.sh"]