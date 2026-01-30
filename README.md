# Vehicle Damage Analyzer

A modular, extensible application for analyzing vehicle damage using AI vision models. Supports multiple operation modes including interactive CLI, batch processing, and web interface.

## Features

- **AI-Powered Analysis**: Uses Ollama's Llama 3.2 Vision model for accurate damage detection
- **Multiple Operation Modes**: Switch between Interactive CLI, Batch Processing, and Web UI at runtime
- **Cost Estimation**: Automated repair cost calculation based on damage analysis
- **Report Generation**: Export detailed analysis reports in CSV format
- **Modular Architecture**: Clean, well-documented code structure for easy maintenance and extension
- **Secure**: No hardcoded credentials; supports environment variables for configuration

## Installation

### Prerequisites

- Python 3.9 or higher
- Ollama installed and running (required for AI analysis)
- Llama 3.2 Vision model pulled in Ollama

### Setup Ollama

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull llama3.2-vision
ollama pull llama3.2
```

### Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

```
ai_vehicle_damage_analyzer/
├── src/                    # Source code modules
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── cost_estimator.py  # Cost calculation logic
│   ├── file_handler.py    # File I/O operations
│   ├── image_analyzer.py  # Image analysis logic
│   ├── main.py            # CLI interface
│   ├── ollama_client.py   # Ollama API client
│   ├── report_generator.py # Report generation
│   └── web_ui.py          # Streamlit web UI
├── input_data/            # Input images directory
├── output_data/           # Output reports directory
├── .gitignore            # Git ignore rules
├── agents                # Task management file
├── IMPLEMENTATION_SUMMARY.md # Implementation summary
├── LICENSE               # License file
├── README.md             # This file
├── requirements.txt       # Python dependencies
└── TASK_LIST.md         # Implementation progress tracker
```

## Usage

### Configuration

Create a `.env` file in the project root (optional):

```bash
# Ollama configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL_VISION=llama3.2-vision
OLLAMA_MODEL_TEXT=llama3.2

# Logging configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Application configuration
DEFAULT_MODE=interactive
INPUT_DIR=input_data
OUTPUT_DIR=output_data
```

### Operation Modes

#### 1. Interactive CLI Mode

Provides an interactive command-line interface for single image analysis:

```bash
python -m src.main --mode interactive
```

Interactive mode prompts for:
- Image file path or upload
- Analysis options
- Report generation preferences

#### 2. Batch Processing Mode

Process multiple images from a directory:

```bash
python -m src.main --mode batch --input input_data/ --output output_data/
```

Batch mode supports:
- Processing all images in a directory
- Parallel processing for faster results
- Individual and combined reports
- Progress tracking

#### 3. Web UI Mode

Launch a Streamlit-based web interface:

```bash
streamlit run src/web_ui.py
```

Web UI features:
- Drag-and-drop image upload
- Real-time analysis display
- Interactive cost breakdown
- Downloadable reports
- Responsive design

### CLI Options

```bash
python -m src.main [OPTIONS]

Options:
  --mode MODE          Operation mode: interactive, batch, api [default: interactive]
  --input PATH         Input directory or file path [for batch mode]
  --output PATH        Output directory path [default: output_data/]
  --model MODEL        Ollama model to use [default: llama3.2-vision]
  --verbose            Enable verbose logging
  --help               Show this help message
```

## Input/Output

### Input Data

Place your vehicle images in the `input_data/` directory. Supported formats:
- JPEG (.jpg, .jpeg)
- PNG (.png)

### Output Data

Analysis results are saved in the `output_data/` directory:
- CSV reports with damage analysis and cost estimates
- Timestamped filenames for easy tracking
- Individual and batch summary reports

## Cost Estimation

The application uses a predefined cost database for different damage types:

| Damage Type | Minor | Moderate | Severe |
|-------------|-------|----------|--------|
| Scratches | $100 | $300 | $500 |
| Dented & Crumpled | $200 | $600 | $1000 |
| Broken Headlights | $150 | $400 | $800 |
| Shattered Windshield | $300 | $800 | $1200 |
| Damaged Bumper | $250 | $700 | $1100 |

Costs can be customized by modifying the `cost_estimator.py` module.

## API Usage

You can use the modules programmatically in your own code:

```python
from src.ollama_client import OllamaClient
from src.image_analyzer import ImageAnalyzer
from src.cost_estimator import CostEstimator

# Initialize components
client = OllamaClient()
analyzer = ImageAnalyzer(client)
estimator = CostEstimator()

# Analyze image
analysis = analyzer.analyze_image("path/to/image.jpg")

# Estimate costs
costs = estimator.estimate_costs(analysis)
print(costs)
```

## Error Handling

The application includes comprehensive error handling:
- Graceful degradation on API failures
- Detailed error messages and logging
- Automatic retry logic for transient failures
- Validation of input files and formats

## Logging

Logs are written to `logs/app.log` (if configured) and console. Log levels:
- DEBUG: Detailed debugging information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

## Security

- No hardcoded credentials or API keys
- Environment variables for sensitive configuration
- Input validation and sanitization
- Secure file handling

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama if needed
ollama serve
```

### Model Not Found

```bash
# Pull the required models
ollama pull llama3.2-vision
ollama pull llama3.2
```

### Import Errors

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt --upgrade
```

## Contributing

Contributions are welcome! Please follow these guidelines:
- Follow existing code style (PEP 8)
- Add docstrings to all functions and classes
- Write tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please refer to the project repository.

## Changelog

### Version 1.0.0
- Initial release
- Interactive CLI mode
- Batch processing mode
- Streamlit web UI
- Modular architecture
- Comprehensive documentation