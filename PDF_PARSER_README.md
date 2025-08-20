# PDF Parser for College Cutoff Data

This project now includes a comprehensive PDF parsing system that can extract college admission cutoff data from PDF documents and store it in a SQLite database.

## Features

- **PDF Text Extraction**: Automatically extracts text content from PDF files
- **Intelligent Data Parsing**: Recognizes college names, branch codes, and cutoff data
- **Database Storage**: Stores parsed data in a structured SQLite database
- **REST API**: Flask endpoints for PDF upload and data retrieval
- **React Frontend**: User-friendly interface for PDF upload and management
- **Data Validation**: Ensures data integrity and handles parsing errors gracefully

## Installation

### Prerequisites

- Python 3.8+
- Node.js and npm (for React frontend)
- Conda (recommended for Python package management)

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   conda install -c conda-forge pypdf2 pandas openpyxl
   # or
   pip install PyPDF2 pandas openpyxl
   ```

2. **Install additional Python packages:**
   ```bash
   pip install flask flask-cors python-dotenv
   ```

3. **Verify installation:**
   ```bash
   python test_pdf_parser.py
   ```

### Frontend Setup

1. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

2. **Start the React development server:**
   ```bash
   npm start
   ```

## Usage

### 1. Starting the Backend

```bash
python EDI_project.py
```

The Flask server will start on `http://localhost:5001`

### 2. PDF Upload and Parsing

#### Via React Frontend
1. Open the React app in your browser
2. Navigate to the PDF Upload component
3. Select a PDF file (max 16MB)
4. Click "Parse PDF" to extract and store data

#### Via API Endpoints

**Upload PDF:**
```bash
curl -X POST -F "file=@your_file.pdf" http://localhost:5001/upload-pdf
```

**Get all colleges:**
```bash
curl http://localhost:5001/colleges
```

**Get specific college details:**
```bash
curl http://localhost:5001/college/01002
```

**Get database statistics:**
```bash
curl http://localhost:5001/database-stats
```

### 3. Database Structure

The system creates three main tables:

#### `colleges` table
- `id`: Primary key
- `college_code`: Unique college identifier (e.g., "01002")
- `college_name`: Full college name
- `created_at`, `updated_at`: Timestamps

#### `branches` table
- `id`: Primary key
- `college_id`: Foreign key to colleges table
- `branch_code`: Unique branch identifier (e.g., "0100219110")
- `branch_name`: Branch name (e.g., "Civil Engineering")
- `status`: College status (e.g., "Government Autonomous")

#### `cutoff_data` table
- `id`: Primary key
- `branch_id`: Foreign key to branches table
- `stage`: Admission stage (e.g., "I", "VII")
- `category`: Admission category (e.g., "GOPENS", "GSCS", "EWS")
- `rank`: Cutoff rank
- `percentage`: Cutoff percentage/percentile

## PDF Format Requirements

The parser is designed to work with PDFs that have the following structure:

```
01002 - Government College of Engineering, Amravati

0100219110 - Civil Engineering
Status: Government Autonomous
State Level
Stage I
GOPENS: 33717 (88.6037289)
GSCS: 61041 (78.5613347)
GNT3S: 67451 (76.1358545)
...

0100224210 - Computer Science and Engineering
Status: Government Autonomous
State Level
Stage I
GSCS: 11323 (96.2437396)
...
```

### Key Elements:
- **College Header**: Format: `[5-digit code] - [College Name]`
- **Branch Section**: Format: `[10-digit code] - [Branch Name]`
- **Status Line**: Format: `Status: [Status Description]`
- **Stage Information**: Format: `Stage [Roman Numeral]` or `Stage [Roman Numeral]-[Description]`
- **Cutoff Data**: Format: `[CATEGORY]: [RANK] ([PERCENTAGE])`

## Testing

### Run the Test Suite

```bash
python test_pdf_parser.py
```

This will:
1. Test the PDF parser with sample data
2. Test database functionality
3. Generate a test output file (`test_output.json`)

### Expected Output

```
🚀 Starting PDF Parser Tests...

==================================================
TEST 1: PDF Parser Functionality
==================================================
✅ Parsing successful!
College: Government College of Engineering, Amravati
College Code: 01002
Total Branches: 4

📚 Branches found:
  - Civil Engineering (0100219110)
    Status: Government Autonomous
    Cutoff data entries: 9
  - Computer Science and Engineering (0100224210)
    Status: Government Autonomous
    Cutoff data entries: 7
  ...

==================================================
TEST 2: Database Functionality
==================================================
✅ Sample data stored successfully!
✅ Data retrieved successfully!

🎉 All tests completed!
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload-pdf` | POST | Upload and parse PDF file |
| `/colleges` | GET | Get list of all colleges |
| `/college/<code>` | GET | Get specific college details |
| `/database-stats` | GET | Get database statistics |
| `/chat` | POST | Existing chatbot functionality |

## Error Handling

The system includes comprehensive error handling:

- **File Validation**: Ensures only PDF files are uploaded
- **Parsing Errors**: Gracefully handles malformed PDFs
- **Database Errors**: Provides clear error messages for storage issues
- **API Errors**: Returns appropriate HTTP status codes and error messages

## File Management

- **Upload Directory**: `uploads/` (created automatically)
- **File Size Limit**: 16MB maximum
- **Cleanup**: Uploaded files are automatically removed after processing
- **Database**: All data is stored persistently in SQLite

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'PyPDF2'**
   ```bash
   conda install -c conda-forge pypdf2
   ```

2. **Database connection errors**
   - Ensure you have write permissions in the project directory
   - Check if the database file is locked by another process

3. **PDF parsing fails**
   - Verify the PDF contains text (not just images)
   - Check if the PDF format matches the expected structure
   - Ensure the PDF is not password-protected

4. **Frontend connection errors**
   - Verify the Flask backend is running on port 5001
   - Check CORS configuration
   - Ensure the React app is configured to connect to the correct backend URL

### Debug Mode

Enable debug logging by modifying the logging level in `pdf_parser.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

- **Large PDFs**: The parser can handle PDFs up to 16MB
- **Database Indexes**: Automatic indexing for optimal query performance
- **Memory Usage**: Files are processed in chunks to minimize memory usage
- **Cleanup**: Automatic file cleanup prevents disk space issues

## Future Enhancements

- **Batch Processing**: Support for multiple PDF uploads
- **Data Export**: Export parsed data to various formats (CSV, Excel)
- **Advanced Parsing**: Machine learning-based parsing for varied PDF formats
- **User Management**: Multi-user support with authentication
- **API Rate Limiting**: Protect against abuse
- **Data Validation**: Enhanced validation rules and data quality checks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of the EDI SEM 5 coursework and follows the same licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test output
3. Check the Flask server logs
4. Verify database connectivity
