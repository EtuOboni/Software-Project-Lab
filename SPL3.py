import tkinter as tk
from tkinter import Toplevel, messagebox
import joblib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load the trained model and encoders
regressor = joblib.load("regressor_model.pkl")
classifier = joblib.load("classifier_model.pkl")

encoder_api_url = joblib.load("encoder_api_url.pkl")
encoder_method = joblib.load("encoder_method.pkl")
encoder_best_tool = joblib.load("encoder_best_tool.pkl")

def predict_api(api_category, api_method):
    try:
        # Encode the input data
        api_encoded = encoder_api_url.transform([api_category])[0]
        method_encoded = encoder_method.transform([api_method])[0]

        # Prepare input for prediction
        input_data = np.array([[api_encoded, method_encoded]])

        # Predict regression metrics
        predicted_metrics = regressor.predict(input_data)

        # Predict the best tool
        predicted_tool_encoded = classifier.predict(input_data)
        predicted_tool = encoder_best_tool.inverse_transform(predicted_tool_encoded)[0]

        # Return the results
        return {
            "Predicted Response Time (ms)": float(predicted_metrics[0][0]),
            "Predicted Error Rate (%)": float(predicted_metrics[0][1]),
            "Predicted Throughput (Req/sec)": float(predicted_metrics[0][2]),
            "Recommended Tool": predicted_tool
        }
    except Exception as e:
        messagebox.showerror("Error", f"Failed to make prediction: {e}")
        return None

def show_predictions():
    api_category = api_category_entry.get().strip()
    api_method = api_method_entry.get().strip().upper()

    if not api_category or not api_method:
        messagebox.showerror("Error", "Please enter both API category and method.")
        return

    # Make predictions using the trained model
    prediction = predict_api(api_category, api_method)

    if prediction:
        # Open a new window for displaying results
        results_window = Toplevel(root)
        results_window.title("Prediction Results")
        results_window.geometry("700x550")
        results_window.configure(bg="#ffffff")

        tk.Label(results_window, text="Prediction Results", font=("Arial", 16, "bold"), bg="#ffffff").pack(pady=10)

        tk.Label(results_window, text=f"Response Time: {prediction['Predicted Response Time (ms)']:.2f} ms", 
                 font=("Arial", 12), bg="#ffffff").pack(pady=2)
        tk.Label(results_window, text=f"Error Rate: {prediction['Predicted Error Rate (%)']:.2f} %", 
                 font=("Arial", 12), bg="#ffffff").pack(pady=2)
        tk.Label(results_window, text=f"Throughput: {prediction['Predicted Throughput (Req/sec)']:.2f} Req/sec", 
                 font=("Arial", 12), bg="#ffffff").pack(pady=2)
        
        # Determine the recommendation reason
        recommended_tool = prediction["Recommended Tool"]
        reason = ""
        if recommended_tool == "K6":
            reason = (
                
                
                "K6 is best for high-throughput, low-error APIs, making it ideal for performance and stress testing."
            )
        elif recommended_tool == "JMeter":
            reason = (
               
                "JMeter is better suited for APIs with slow response times or high error rates, "
                "ideal for complex and functional load testing."
            )

        tk.Label(results_window, text=f"Recommended Tool: {prediction['Recommended Tool']}", 
                 font=("Arial", 14, "bold"), fg="white", bg="#4CAF50", padx=10, pady=5).pack(pady=10)
        
        # Display the recommendation reason
        tk.Label(results_window, text="Recommendation Reason:", font=("Arial", 12, "bold"), bg="#ffffff").pack(pady=5)
        tk.Label(results_window, text=reason, font=("Arial", 11), bg="#ffffff", justify="left", wraplength=600).pack(pady=5)

        # Graph Setup
        fig, ax1 = plt.subplots(figsize=(8, 4), dpi=100)
        
        # Plot Response Time and Throughput on the primary y-axis
        labels = ["Response Time (ms)", "Throughput (Req/sec)"]
        values = [
            prediction["Predicted Response Time (ms)"],
            prediction["Predicted Throughput (Req/sec)"]
        ]
        ax1.bar(labels, values, color=["blue", "green"], alpha=0.6, label="Response Time & Throughput")
        ax1.set_ylabel("Response Time (ms) & Throughput (Req/sec)", color="black")
        ax1.tick_params(axis='y', labelcolor="black")

        # Create a secondary y-axis for Error Rate
        ax2 = ax1.twinx()
        error_rate = prediction["Predicted Error Rate (%)"]
        ax2.plot(labels, [error_rate, error_rate], color="red", marker="o", linestyle="dashed", label="Error Rate (%)")
        ax2.set_ylabel("Error Rate (%)", color="red")
        ax2.tick_params(axis='y', labelcolor="red")

        # Add legends
        fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)

        # Set title
        ax1.set_title("API Performance Metrics (Response Time, Throughput, and Error Rate)")

        # Display the graph
        canvas = FigureCanvasTkAgg(fig, master=results_window)
        canvas.get_tk_widget().pack(pady=15)
        canvas.draw()

# Main UI Setup
root = tk.Tk()
root.title("API Load Tester & Tool Recommender")
root.geometry("500x350")
root.configure(bg="#f0f0f0")

# Centering Frame
frame = tk.Frame(root, bg="#f0f0f0")
frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(frame, text="Predictive Load Testing & API Tool Recommender", 
         bg="#f0f0f0", font=("Arial", 14, "bold"), wraplength=400, justify="center").pack(pady=10)

tk.Label(frame, text="Enter API Category:", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
api_category_entry = tk.Entry(frame, font=("Arial", 12), width=30)
api_category_entry.pack(pady=5)

tk.Label(frame, text="Enter API Method (GET, POST, PUT, DELETE):", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
api_method_entry = tk.Entry(frame, font=("Arial", 12), width=30)
api_method_entry.pack(pady=5)

predict_btn = tk.Button(frame, text="Show Result", command=show_predictions, 
                        font=("Arial", 12), bg="#4CAF50", fg="white", width=20)
predict_btn.pack(pady=10)

root.mainloop()