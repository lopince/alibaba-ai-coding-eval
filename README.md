# Alibaba AI Coding Evaluation

This repository contains evaluation tasks and benchmarks for Alibaba's AI coding product assessment.

## Evaluation Action Items

### 1. Alicloud Product Overview

Comprehensive review and documentation of Alibaba Cloud's AI-related products and services.

- Product catalog and capabilities
- Target use cases and industries
- Integration patterns and APIs
- Competitive positioning

### 2. Qoder Product Overview

In-depth analysis of the Qoder AI coding assistant product.

- Core features and functionality
- User experience and interface design
- Supported languages and frameworks
- Deployment options and pricing

### 3. Qoder Evaluation

Standalone assessment of Qoder's capabilities.

- Code generation quality
- Context understanding
- Multi-turn conversation handling
- Edge case handling

### 4. Qwen 3.x Series Evaluation

Evaluation of the Qwen 3.x large language model series.

- Model variants and specifications
- Benchmark performance
- Coding-specific capabilities
- Comparison with previous versions

### 5. Coding Harness Evaluation (Model + Coding CLI)

Systematic evaluation of different model and CLI combinations for coding tasks.

#### 5.1 Qwen 3.x + Qoder

Evaluate Qwen 3.x models integrated with the Qoder coding assistant.

- End-to-end coding workflow performance
- Prompt engineering effectiveness
- Output quality and accuracy

#### 5.2 3rd-party Models + Qoder

Evaluate third-party models (e.g., GPT, Claude, Gemini) integrated with Qoder.

- Cross-model compatibility
- Performance comparison with Qwen 3.x
- Feature parity analysis

#### 5.3 Qwen 3.x + OpenCode

Evaluate Qwen 3.x models with the OpenCode CLI tool.

- Command-line interaction quality
- Code generation and editing capabilities
- Integration smoothness

#### 5.4 Qwen 3.x + CC (CodeCompanion)

Evaluate Qwen 3.x models with CodeCompanion CLI.

- Workflow efficiency
- Feature utilization
- User experience comparison

## Repository Structure

```
.
├── 01-alicloud-overview/      # Alicloud product overview materials
├── 02-qoder-overview/         # Qoder product overview materials
├── 03-qoder-eval/             # Qoder standalone evaluation
├── 04-qwen3-eval/             # Qwen 3.x series evaluation
├── 05-coding-harness-eval/    # Coding harness evaluations
│   ├── 5.1-qwen3-qoder/
│   ├── 5.2-3rd-models-qoder/
│   ├── 5.3-qwen3-opencode/
│   └── 5.4-qwen3-cc/
├── datasets/                  # Shared test datasets
├── templates/                 # Evaluation templates and rubrics
└── results/                   # Consolidated evaluation results
```

## Getting Started

1. Clone this repository
2. Navigate to the relevant evaluation directory
3. Follow the README in each subdirectory for specific setup instructions

## License

MIT
