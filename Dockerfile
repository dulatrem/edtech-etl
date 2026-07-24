FROM public.ecr.aws/lambda/python:3.12

# Install Python dependencies into the Lambda task root
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy application code into the Lambda task root
COPY lambda_function.py main.py ${LAMBDA_TASK_ROOT}
COPY src/ ${LAMBDA_TASK_ROOT}/src/
COPY config/ ${LAMBDA_TASK_ROOT}/config/

# Set the Lambda entry point
CMD ["lambda_function.lambda_handler"]
