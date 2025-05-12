FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app app/

# Create a script to run both the Flask app and the workers
RUN echo '#!/bin/bash\n\
python -m app.deploy_process && \
python -m app.workers &\n\
python -m app.app' > /app/start.sh && \
chmod +x /app/start.sh

CMD ["/app/start.sh"]