# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the conda environment file into the container
COPY environment.yml .

# Create a conda environment
RUN conda env create -f environment.yml

# Activate the conda environment
SHELL ["conda", "run", "-n", "your_env_name", "/bin/bash", "-c"]

# Copy the rest of the application code into the container
COPY . .

# Expose the port your FastAPI application will run on
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
