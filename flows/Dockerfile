FROM prefecthq/prefect:3-python3.12

# Install additional ML dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy bundled flows
COPY train_model.py /app/flows/train_model.py

# Set working directory
WORKDIR /app/flows

# Default command
CMD ["python", "train_model.py"]
