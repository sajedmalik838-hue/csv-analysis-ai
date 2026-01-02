# 🤖 AI Chatbot Dashboard

A modern Streamlit-based chatbot dashboard that allows you to upload CSV files and interact with your data using Google's Gemini AI.

## ✨ Features

- **📤 CSV File Upload**: Easy drag-and-drop CSV file upload
- **🤖 AI-Powered Chat**: Ask questions about your data using Gemini AI
- **📊 Interactive Data Preview**: View and explore your data with Streamlit's dataframe widget
- **📈 Automatic Statistics**: Get instant insights with statistical summaries
- **💬 Conversation History**: Chat history persists throughout your session
- **🎨 Modern Dark Theme**: Beautiful, eye-friendly interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   cd Antigravit
   pip install -r requirements.txt
   ```

3. **Configure your Gemini API Key**
   
   Add your Gemini API key to the `.env` file in the project root:
   ```bash
   GEMINI_API_KEY = "your-actual-api-key-here"
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```
   *Note: If port 8501 is in use, use: `streamlit run app.py --server.port 8502`*

The app will automatically open in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### Uploading a CSV File

1. Click the **"Browse files"** button in the sidebar
2. Select a CSV file from your computer
3. The file will be automatically processed and statistics will appear in the sidebar

### Chatting with Your Data

Once a CSV is uploaded, you can ask questions like:

- "What columns are in this dataset?"
- "Show me statistics for the Salary column"
- "What patterns do you see in this data?"
- "Are there any missing values?"
- "What's the average age of employees in the Engineering department?"
- "Can you summarize this dataset?"

### Viewing Your Data

Switch to the **"Data Preview"** tab to:
- View the complete dataset in an interactive table
- See statistical summaries for numeric columns
- Explore column data types and metadata

## 🗂️ Project Structure

```
Antigravit/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── sample_data.csv                 # Sample CSV for testing
├── .streamlit/
│   ├── config.toml                # Streamlit configuration & theme
│   └── secrets.toml.example       # Template for API key
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🎨 Customization

### Changing the Theme

Edit `.streamlit/config.toml` to customize colors:

```toml
[theme]
primaryColor = "#8B5CF6"           # Purple accent
backgroundColor = "#0F172A"         # Dark blue background
secondaryBackgroundColor = "#1E293B"
textColor = "#F1F5F9"
```

### Adjusting File Size Limits

By default, Streamlit limits file uploads to 200MB. To change this, add to `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 500  # In MB
```

## 🧪 Testing

A sample CSV file (`sample_data.csv`) is included for testing. It contains employee data with:
- Customer IDs
- Names
- Ages
- Departments
- Salaries
- Join dates
- Performance scores

## 🛠️ Troubleshooting

### "Error initializing Gemini API"
- Make sure `.streamlit/secrets.toml` exists (not just the .example file)
- Verify your API key is correctly copied into the secrets file
- Ensure there are no extra spaces or quotes around the API key

### "Module not found" errors
- Run `pip install -r requirements.txt` again
- Make sure you're using Python 3.8 or higher: `python --version`

### CSV upload fails
- Ensure your file is a valid CSV format
- Check that the file isn't corrupted
- Try the included `sample_data.csv` first to verify the app works

### Port already in use
If port 8501 is busy, specify a different port:
```bash
streamlit run app.py --server.port 8502
```

## 🔒 Security Notes

- **Never commit `.streamlit/secrets.toml`** to version control (it's already in `.gitignore`)
- Keep your Gemini API key private
- The app runs locally on your machine - no data is sent anywhere except to the Gemini API for chat responses

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Ensure your API key is valid and active

## 📝 License

This project is open source and available for personal and commercial use.

---

**Built with ❤️ using Streamlit and Google Gemini AI**
