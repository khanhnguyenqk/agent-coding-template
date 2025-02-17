# AI Agent Guide: Adapting Evaluation Projects to Evaluation Framework

This guide explains how to adapt evaluation projects to use the evaluation framework defined in `eval_core_utils.datamodel.evaluation` and `eval_core_utils.interfaces.evaluation_job_launcher`. This framework provides a standardized way to define and execute evaluation jobs across different types of evaluations.

## Core Concepts

The following code blocks demonstrate the core data models used in the evaluation framework.

### Key Imports

```python
from typing import Dict, List, Optional
from eval_core_utils.datamodel.evaluation.entities import (
    EvaluationJob, EvaluationConfig, EvaluationTarget, 
    EvaluationResult, Model
)
from eval_core_utils.datamodel.evaluation.values import (
    TaskConfig, MetricConfig, TaskResult, MetricResult, Score
)
from eval_core_utils.datamodel.evaluation.enums import (
    EvaluationType, TargetType, TaskType, MetricType
)
from eval_core_utils.datamodel.datastore.datasets import Dataset
from eval_core_utils.datamodel.datastore.models.values import APIEndpointData
from eval_core_utils.interfaces.evaluation_job_launcher import (
    EvaluationJobLauncher, ValidationResult
)
```

### EvaluationJob

```python
# EvaluationJob is the central entity representing an evaluation task
job = EvaluationJob(
    # Unique identifier for the job
    id="eval_001",  
    
    # EvaluationConfig defining what to evaluate
    config=EvaluationConfig(
        type=EvaluationType.CUSTOM,
        tasks={...}  # Dictionary of TaskConfig objects
    ),
    
    # EvaluationTarget defining what is being evaluated
    target=EvaluationTarget(...)
)
```

### EvaluationConfig

```python
# EvaluationConfig defines the evaluation parameters
config = EvaluationConfig(
    # Type of evaluation (e.g., CUSTOM)
    type=EvaluationType.CUSTOM,
    
    # Dictionary mapping task names to TaskConfig objects
    tasks={
        "main_task": TaskConfig(
            type=TaskType.CUSTOM,
            dataset=Dataset(...),
            metrics=[MetricConfig(...)],
            params={"key": "value"}
        )
    }
)
```

### TaskConfig

```python
# TaskConfig specifies parameters for an individual evaluation task
task_config = TaskConfig(
    # Type of task (e.g., CUSTOM, BEIR)
    type=TaskType.CUSTOM,
    
    # Dataset configuration
    dataset=Dataset(
        dataset_format="format_name",
        dataset_path="/path/to/data"
    ),
    
    # List of metrics to compute
    metrics=[
        MetricConfig(
            type=MetricType.CUSTOM,
            params={"name": "accuracy"}
        )
    ],
    
    # Additional task-specific parameters
    params={
        "batch_size": 32,
        "max_length": 512
    }
)
```

### EvaluationTarget

```python
# EvaluationTarget defines what is being evaluated
target = EvaluationTarget(
    # Type of target (e.g., MODEL)
    type=TargetType.MODEL,
    
    # Model configuration
    model=Model(
        api_endpoint=APIEndpointData(
            url="https://api.example.com/v1",
            model_id="model-v1",
            api_key=None
        )
    )
)
```

### EvaluationResult

```python
# EvaluationResult contains the evaluation results
result = EvaluationResult(
    # Reference to original job
    job=job,
    
    # Dictionary mapping task names to TaskResult objects
    tasks={
        "main_task": TaskResult(
            metrics={
                "accuracy": MetricResult(
                    scores={"accuracy": Score(value=0.95)}
                )
            }
        )
    }
)
```

## Implementation Guide

### 1. Create Custom Launcher

Create a class that inherits from `EvaluationJobLauncher`:

```python
class CustomEvalLauncher(EvaluationJobLauncher):
    def __init__(self):
        # Initialize any required resources
        pass

    def launch_evaluation_job(self, job: EvaluationJob) -> EvaluationResult:
        result = EvaluationResult(job=job)
        
        for task_key, task_config in job.config.tasks.items():
            task_result = self._execute_task(task_config, job.target)
            result.tasks[task_key] = task_result
            
        return result
```

### 2. Implement Input Validation

Add validation logic to ensure job inputs meet requirements:

```python
def validate_job_input(self, job: EvaluationJob) -> ValidationResult:
    errors = []
    
    if not job.id:
        errors.append("Job ID is required")
    
    # Add custom validation rules
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors
    )
```

### 3. Transform Evaluation Parameters

Convert your evaluation project's parameters into the framework's data model:

```python
def create_evaluation_job(original_params: dict) -> EvaluationJob:
    # Convert original parameters to framework format
    eval_config = EvaluationConfig(
        type=EvaluationType.CUSTOM,
        tasks={
            "main_task": TaskConfig(
                type=TaskType.CUSTOM,
                dataset=Dataset(
                    dataset_format="your_format",
                    dataset_path=original_params["data_path"]
                ),
                metrics=[
                    MetricConfig(
                        type=MetricType.CUSTOM,
                        params={"name": metric_name}
                    ) for metric_name in original_params["metrics"]
                ],
                params=original_params["additional_params"]
            )
        }
    )

    eval_target = EvaluationTarget(
        type=TargetType.MODEL,
        model=Model(
            api_endpoint=APIEndpointData(
                url=original_params["model_endpoint"],
                model_id=original_params["model_id"]
            )
        )
    )

    return EvaluationJob(
        config=eval_config,
        target=eval_target,
        id=get_random_id("eval")
    )
```

### 4. Execute Evaluation Tasks

Implement the core evaluation logic in `_execute_task`:

```python
def _execute_task(self, task_config: TaskConfig, eval_target: EvaluationTarget) -> TaskResult:
    # 1. Set up the evaluation environment
    self._setup_environment(task_config)
    
    # 2. Prepare the dataset
    dataset = self._prepare_dataset(task_config.dataset)
    
    # 3. Initialize your evaluation model/system
    evaluator = self._initialize_evaluator(eval_target, task_config)
    
    # 4. Run the evaluation
    raw_results = evaluator.evaluate(dataset)
    
    # 5. Convert results to TaskResult format
    return self._convert_results(raw_results)
```

### 5. Format Results

Convert your evaluation results into the framework's format:

```python
def _convert_results(self, raw_results: dict) -> TaskResult:
    task_result = TaskResult()
    
    for metric_name, value in raw_results.items():
        metric_result = MetricResult(
            scores={metric_name: Score(value=value)}
        )
        task_result.metrics[metric_name] = metric_result
    
    return task_result
```

## Best Practices

1. **Parameter Mapping**
   - Create clear mappings between your original parameters and the framework's data model
   - Document any parameter transformations
   - Validate all required parameters are present

2. **Error Handling**
   - Implement comprehensive validation in `validate_job_input`
   - Provide clear error messages for invalid configurations
   - Handle evaluation failures gracefully

3. **Resource Management**
   - Clean up resources after evaluation
   - Handle file paths and environment variables properly
   - Consider using context managers for resource lifecycle

4. **Result Processing**
   - Ensure all metrics are properly converted to framework format
   - Preserve any relevant metadata
   - Handle missing or invalid results appropriately

## Example Usage

Here's how an AI agent might use your adapted evaluation:

```python
# Original evaluation parameters
original_params = {
    "model_endpoint": "https://api.example.com/v1",
    "model_id": "example-model-v1",
    "data_path": "evaluation_data.json",
    "metrics": ["accuracy", "f1_score"],
    "additional_params": {
        "batch_size": 32,
        "max_length": 512
    }
}

# Create evaluation job
job = create_evaluation_job(original_params)

# Initialize and run evaluation
launcher = CustomEvalLauncher()
validation = launcher.validate_job_input(job)

if validation.is_valid:
    result = launcher.launch_evaluation_job(job)
    print(f"Evaluation results: {result.model_dump_json()}")
else:
    print(f"Validation errors: {validation.errors}")
```

## Common Pitfalls

1. Don't hardcode evaluation parameters - use TaskConfig.params
2. Don't ignore validation - always implement comprehensive input validation
3. Don't skip error handling - wrap evaluation code in try-except blocks
4. Don't lose metadata - preserve important information in result conversion
