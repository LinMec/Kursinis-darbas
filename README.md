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
2. Place all data files in the same folder, open it in Visual Studio Code, and use the Explorer to navigate them.

3. Run the program

## OOP 4 pillars

1. **Encapsulation**

    ```
    class TransactionData:
        def __init__(self, raw_data, data_type):
            self.__transactions = []
            self.__timestamps = []
            self.__amounts = []
            self.__data_type = data_type  
            self.__parse_data(raw_data)
        
        def __parse_data(self, raw_data):
            for line in raw_data:
                if not line.strip():  
                    continue
                parts = line.strip().split(',')
                if self.__data_type == "credit_card":
                    timestamp = float(parts)
                    amount = float(parts)
                    merchant = parts
                    card_id = parts
                    self.__timestamps.append(timestamp)  #The self_.. is an encapsulation
                    self.__amounts.append(amount)
                    self.__transactions.append({  
                        'timestamp': timestamp,
                        'amount': amount,
                        'merchant': merchant,
                        'card_id': card_id
                    })
                elif self.__data_type == "insurance":
                    # Add insurance data parsing here
                    pass
    ```
    Transactions, amounts, and every other morsel of data, whether it’s linked to actual people or just poor old time/data being crunched by FFTs or wavelets, are securely stuffed inside layers of encapsulation. Why? Because cyber-attacks are out there, lurking, like a badly tuned Vauxhall Astra in "Krasnucha", ready to ruin your day. The given encapsulation attribute is __.
