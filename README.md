# Fraud detection system (with Signal and Graph visualization and its applications)


## Introduction

A Python program to detect and trace financial fraud by analyzing data patterns. Visualizes findings via signal (wavelet/FFT) and graph-based models.

---

## What does it do?

This program is designed to detect and trace financial fraud by analyzing data patterns. It visualizes its findings either via signal (where wavelet and FFT is used, and is compared to the threshold), or through graph-based models that illustrate relationships using vertices and edges.

---

## How to Run

1. **Install dependencies:**
    ```
    pip install numpy matplotlib scipy pywavelets networkx
    ```
2. Have all of the data files ready (e.g., credit_card_transactions.txt, insurance_claims.txt), and change the intended file path, to where you would like it to be
   ```
   output_path = r"C:\Users\YourUser\ThePlaceWhereYouPutTheFolder\Kursins darbas\info.txt"
   file_path = r"C:\Users\YourUser\ThePlaceWhereYouPutTheFolder\Kursins darbas\insurance_claims.txt"
   file_path = r"C:\Users\YourUser\PlaceWhereYouPutTheFolder\Kursins darbas\credit_card_transactions.txt"
   ```
3. Run the program
   ```
   python Failas.py
   ```
