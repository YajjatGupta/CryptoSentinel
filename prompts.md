# Shubham Tandon's Prompts

1.Act as a senior software engineer and data scientist. I have a Flask backend script, app.py, for a project called CryptoSentinel. Explain the entire data processing and analysis pipeline in detail.
Your explanation should cover:
The overall architecture: How the frontend, backend, and external APIs interact.
The data flow: A step-by-step description from the moment a user selects a coin in the UI to the final chart and analysis being displayed.
Key functions: A detailed breakdown of the fetch_historical_data, run_anomaly_detection, and get_gemini_analysis functions, including the technologies used (e.g., CoinGecko API, IsolationForest, Google Gemini).
Use a structured format with headings and bullet points for easy documentation.

2.Act as a machine learning expert. I am working on the anomaly detection component of my project, CryptoSentinel. My current approach for setting the anomaly threshold is threshold = np.mean(train_loss) + np.std(train_loss).
Address the following points:
Explain the current threshold: Describe what this line of code does, its strengths, and its limitations for detecting financial anomalies.
Suggest a better approach: Provide and explain an alternative, more robust method for setting the threshold, such as using a precision-recall or ROC curve approach. Explain why this method is better for this specific application.
Troubleshoot the error: I tried to implement a validation curve approach, but I'm getting a NameError: name 'valid_labels' is not defined. Explain what this error means in the context of the code and how to correctly implement this approach using the existing data in the Graph.py script.

3.Act as a Python developer and data visualization expert. I'm using Matplotlib in my plot_generator.py script to visualize price anomalies.
Answer the following questions with specific code examples:
Anomaly Visualization: Is there a way to mark on the graph exactly where a detected anomaly is? Provide a code snippet using plt.scatter that I can add to my plot_anomalies function to achieve this. Specify where this snippet should be placed.
Plotting the Entire Window: If the model detects an anomaly within a user-specified date range (e.g., from 2025-03-01 to 2025-07-01), will the plot visualize only the anomalous portion or the entire window? Explain the current behavior based on the plot_anomalies function and confirm it with a specific line reference.
Direction of Manipulation: Is it possible to add visual cues, such as red lines or arrows, on the graph to show the direction of the manipulation (e.g., a "pump" or a "dump")? Provide a detailed explanation of how to infer this information from the provided data and a code snippet demonstrating how to add these visual markers.

4.Act as a financial data analyst specializing in quantitative trading. I have two different models for detecting market anomalies, and I have their outputs as graphs.
Analyze the two models based on the provided visual outputs:
Model 1: Isolation Forest (e.g., MSFT.png, ICICIBANK.NS.png)
Model 2: LSTM Autoencoder (e.g., META.png, RELIANCE.NS.png)
In your response, provide a structured comparison that addresses the following:
Types of Anomalies: Based on the graphs, describe the types of anomalies each model seems to be detecting. Does Model 1 focus on sharp, sudden changes, while Model 2 identifies sustained deviations from a reconstructed baseline?
Logical Standpoint: Evaluate the 'Actual Price' (blue line) vs. the 'Reconstruction' (red line) in both graphs. From a logical standpoint, does each model's reconstruction make sense in the context of anomaly detection? Which model's reconstruction seems to better represent "normal" behavior?
Overall Performance: Based on the visual evidence, which model do you believe does a better job of detecting anomalies and why? Support your answer with specific observations from the provided images.
Please use a table or a clear, side-by-side comparison to present your findings
# Vipin Yadav's Prompts
1.Project Re-branding and Core Objective
Objective: Re-brand the existing "Web3Guard" platform for a new hackathon, defining the project's core purpose.

2.Directive:
Rename the platform to "CryptoSentinel".
Analyze the provided project context and the main.ipynb notebook to understand the core functionality.
Generate a new, unique, and professional logo for the "CryptoSentinel" brand.
Propose a clear and compelling tagline that accurately describes the platform's value proposition.

3.Landing Page & Visual Enhancements
Objective: Improve the user interface and branding on the landing page (Index.tsx).
Directive: Update all instances of the old logo and name to the new "CryptoSentinel" logo and name. Change the hero section's tagline to: "Our advanced AI algorithms detect suspicious on-chain activity in real-time, keeping your digital assets safe from manipulation." Set up an image as the background for the landing page hero section.

4.Dashboard Layout Refinement
Objective: Simplify the dashboard to focus on the core anomaly detection feature.
Directive: 
Modify the Dashboard.tsx component.
Remove the following sections from the dashboard layout:
"Market Overview" tabs
"Fraud Alerts" widget
"Market Sentiment" widget
Keep only the interactive graph and the AI analysis section.

5.Graphing Technology Migration to Plotly Ojective: Replace the current static Matplotlib plots with dynamic, interactive graphs using Plotly.
Directive:Change the plotting library from Matplotlib to Plotly for the frontend graphs.
The new plots must be interactive, allowing users to zoom and pan.
The graphs must display the cryptocurrency price data, the reconstructed data from the anomaly detection model, and visually mark the anomalous data points.

6.Backend Data API Modification
Objective: Adapt the backend to serve raw data instead of pre-generated images, supporting the Plotly migration.
Directive: Modify the app.py and plot_generator.py files.
Change the /api/analyze-crypto endpoint to return a JSON object instead of an image path.
The JSON object should contain:
The time-series data for the selected cryptocurrency.
The reconstructed data from the anomaly detection model.
A list of timestamps for the detected anomalies.

7.Frontend Graphing Implementation
Objective: Implement the new interactive Plotly graph component to consume the updated backend data.
Directive:
Create a new React component for rendering the Plotly graph.
This component should fetch the JSON data from the new /api/analyze-crypto endpoint.
Use Plotly to visualize the fetched time-series data, the reconstructed data, and the highlighted anomalies in a single, interactive graph.

8.UI Styling and Text Formatting
Objective: Resolve visual and formatting issues in both light and dark modes.
Directive:
In the dashboard, ensure the x and y-axis labels and values on the Plotly graph are clearly visible in both light and dark themes. Change their color as necessary.
Fix the text overflow issue in the Gemini AI analysis card to ensure the text wraps correctly.
Apply proper text formatting, including bolding and spacing, to make the AI analysis report more professional and readable.

9.Final Backend Code Objective: Provide the final, complete, and fully functional app.py file.
Directive:
Provide the full, corrected source code for app.py.
The code must be production-ready and include the changes for the data API, the Gemini API integration, and any other necessary fixes.

10.Project Execution Instructions
Objective: Provide a clear guide for running the entire project.
Directive:
Give step-by-step instructions on how to install all necessary dependencies for both the Python backend and the React frontend.
Provide the commands to run both the Flask server and the Vite development server.
Explain how a user can verify that the project is running correctly and that all the changes have been applied.

11. Final Code Update Summary Objective: Summarize all the changes made to the project. Directive:
List all the files that were modified or created.
Provide a brief, high-level overview of the purpose of each change (e.g., "Modified app.py to return JSON data instead of an image for interactive graphs.").
This should serve as a final confirmation that all the project requirements have been met.

# Vihag Chaturvedi's Prompts

1.Act as a financial data scientist. Compare the anomaly detection approach of my project, CryptoSentinel, with a Transformer-based model for stock price prediction.
For my project, assume the use of an LSTM autoencoder and Isolation Forest models. For the alternative, analyze the approach described in Matthew Frank's article, 'Stock Price Prediction Using Transformers'.
In your response, provide a comprehensive analysis in a clear, side-by-side comparison table. The table should include the following columns: 'Primary Goal', 'Core Mechanism', 'Benefits of the Approach', and 'Shortcomings of the Approach'.
Conclude with a brief paragraph summarizing which approach is better suited for a trading platform focused on real-time fraud alerts and why.

2.Act as a machine learning engineer. I am comparing the anomaly detection approach of my project, CryptoSentinel, with the Transformer-based model for stock price prediction described in the provided Medium article.
Explain how the Transformer model, designed for prediction, could be adapted to perform anomaly detection.
Compare the benefits and shortcomings of this adapted Transformer approach versus the unsupervised Isolation Forest and autoencoder methods currently used in my project.
Which approach would be more effective for detecting pump-and-dump schemes and why?
Please use a structured format with clear headings and bullet points for my documentation also show me the training loss curves and the scaling law demonstration 

3.Act as a Python developer. Explain how to modify the Graph.py script to generate a single graph that visualizes all anomalies within the user-specified date range. The graph should display the entire time series, with anomaly points marked clearly. Explain why the original code created multiple graphs and how the new code resolves the X-axis scaling issue. Provide the specific code snippet to replace the existing plotting loop.

4.Act as a financial data analyst. Looking at the provided RELIANCE.NS.png chart, I notice a clear divergence between the actual price (blue line) and the reconstructed price (red line) during the period from approximately January 8, 2025, to January 15, 2025. Despite this noticeable difference, no anomalies were marked.
Explain the potential reasons why the anomaly detection model might have missed this event. Consider factors such as the model's training data, the definition of the anomaly threshold, and the overall volatility of the market during that specific window. How might these factors lead to a significant price deviation being classified as 'normal'?

5.Act as a senior machine learning engineer with expertise in both TensorFlow and PyTorch. I need you to convert my existing Python script, Graph.py, which uses TensorFlow for an anomaly detection autoencoder, into a new script using PyTorch.
Here is the content of my Graph.py file:
In your response, provide the following:
Complete PyTorch Script: Generate a new, fully functional Python script that achieves the same anomaly detection purpose as the original. The new script should be self-contained and runnable, including the model definition, data loading, preprocessing, training loop, and plotting logic.
Conversion Notes: In a separate section, detail the key changes and differences between the TensorFlow and PyTorch implementations. Focus on concepts such as:
How the autoencoder model architecture is defined in PyTorch (torch.nn.Module, torch.nn.Sequential).
The difference between TensorFlow's .fit() method and PyTorch's explicit training loop.
How data preprocessing and plotting from the original script are handled in the new PyTorch version.
Explanation of the PyTorch Code: Add comments within the new PyTorch script to explain the purpose of each major section, such as the model class, training loop, and inference stage.
The goal is to produce a PyTorch script that is a direct, well-documented replacement for the original TensorFlow code, without losing any functionality.

6.Act as a blockchain security analyst. I have an anomaly detection model for cryptocurrency prices that generates 30-day windows where an anomaly was detected. My goal is to identify which wallets may have been involved in the manipulative activity during these periods.
Using the Graph.py script and its output, identify all 30-day date windows where the autoencoder model detected an anomaly.
For each of these specific date windows, perform the following steps:
Retrieve a list of the top 5 cryptocurrency wallets with the highest trading volume for the asset in question.
Provide the wallet addresses and their corresponding trading volumes during that exact time frame.
Present the final output as a clear, bulleted list. Each bullet point should specify the date window, followed by a sub-list of the top 5 wallets and their trading volumes. The final response must focus on wallets and not include the original price graphs

# Yajat Gupta's Prompts
1.Objective: Analyze the provided codebase to diagnose and fix a critical bug preventing the graph from rendering. Propose general enhancements for the website's user experience and functionality.

2.Directive: Provide the corrected code for each file identified in the previous analysis.

3.Refinement: Implement a subscription-based smart contract. Provide the complete Solidity code, ensuring it includes best practices for security and access control.

4.Integration: Create a new React component to handle the frontend's interaction with the smart contract. The component should manage state, connect to a Web3 wallet, and facilitate on-chain subscription transactions.

5.Troubleshooting (Frontend): Debug the provided React component. Resolve all TypeScript errors, including module resolution issues for ethers and invalid syntax, to ensure the code is production-ready.

6.Troubleshooting (Frontend II): Debug the Pricing.tsx component. Address the JSX syntax errors, including unclosed tags and invalid variable references, to restore the page's functionality.

7.Verification: Provide a comprehensive checklist for validating the fixes and new features. The checklist should cover both backend and frontend functionality, including steps to test the graph rendering, the smart contract integration, and the theme toggle.

8.Troubleshooting (Backend): The backend script is failing due to a ModuleNotFoundError for yfinance and tensorflow. Provide a solution to install the missing Python libraries.

9.Troubleshooting (Backend II): The script is throwing a ValueError related to NumPy's squeeze function. Analyze the traceback to pinpoint the cause and provide a corrected Python code snippet that resolves the error.

10.Configuration: The terminal shows a PATH warning regarding tensorboard.exe. Explain the nature of this warning and provide a step-by-step guide on how to add the directory to the system's PATH variable for a permanent solution.

11.Feature & UI Enhancement
User Feedback: The "Pro" plan's subscribe button is incorrectly displaying a price of 0 ETH. Identify the root cause of this display issue in the frontend logic and provide a corrected version of the SubscribeButton.tsx component