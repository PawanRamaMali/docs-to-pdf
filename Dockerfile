FROM xeden3/docker-office-python-core:v1

# Install FastAPI dependencies
RUN apt-get update && apt-get install -y python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install fastapi uvicorn python-multipart

RUN wineboot --init

WORKDIR /opt/wineprefix/drive_c/
# Copy application files
COPY app/ /opt/wineprefix/drive_c/app/

# Create uploads directory with proper permissions
RUN mkdir -p /root/.wine/drive_c/uploads && \
    chmod 777 /root/.wine/drive_c/uploads

RUN mkdir -p /root/.wine/drive_c/uploads && \
    chmod -R 777 /root/.wine/drive_c/uploads

# Create the entrypoint script
RUN echo '#!/bin/bash\n\
xvfb-run -a uvicorn app.main:app --host 0.0.0.0 --port 8000' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 8000

# Use the entrypoint directly
ENTRYPOINT ["/entrypoint.sh"]