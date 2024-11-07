FROM xeden3/docker-office-python-core:v1

# Install pywin32 in Wine Python
RUN xvfb-run wine pip install pywin32

RUN apt-get update && apt-get install -y locales python3-pip

# Install FastAPI dependencies
RUN pip3 install fastapi uvicorn python-multipart

WORKDIR /opt/wineprefix/drive_c/

# Copy application files
COPY app/ /opt/wineprefix/drive_c/app/
COPY libs/tini /tini
COPY code/entrypoint.sh /entrypoint.sh

# Update entrypoint script to run both the original app and FastAPI
RUN echo '#!/bin/bash\n\
xvfb-run -a wine python /opt/wineprefix/drive_c/app/excel_xlsm_macro_run.py & \n\
xvfb-run -a uvicorn app.main:app --host 0.0.0.0 --port 8000\n' > /entrypoint.sh

RUN chmod +x /tini && \
    chmod +x /entrypoint.sh

EXPOSE 8000

# Use tini with the new entrypoint
ENTRYPOINT ["/tini", "--", "/entrypoint.sh"]