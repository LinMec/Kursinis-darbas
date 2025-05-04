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

    ```python
    class TransactionData
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
                timestamp = float(parts[0])
                amount = float(parts[1])
                merchant = parts[2]
                card_id = parts[3]
                
                self.__timestamps.append(timestamp)
                self.__amounts.append(amount) #The __ is the attribute for encapsulation
                self.__transactions.append({
                    'timestamp': timestamp,
                    'amount': amount,
                    'merchant': merchant,
                    'card_id': card_id
                })
            elif self.__data_type == "insurance":
    ```
    
    Transactions, amounts, and every other morsel of data are securely stuffed inside layers of encapsulation. Why? Because cyber-attacks are out there, lurking, like a badly tuned Audi A3 in "Krasnucha", ready to ruin your day. But in all seriousness, it's the main use of encapsulation - safety, so that only intended users would be able to get the data. Encapsulation in this TransactionData class hides the internal data structures such as __transactions, __timestamps, and __amounts by making them private with double underscores. This prevents direct access or modification of these attributes from outside the class, ensuring data integrity. The class controls how raw input data is parsed and stored through the private method __parse_data, centralizing and protecting the parsing logic.

2-3.  **Abstraction/Inheritance**

      ```python
      class FraudDetector(ABC): 
    
        @abstractmethod
        def detect(self, processed_signal, raw_data):
        pass
        class ThresholdDetector(FraudDetector): 
        def __init__(self, threshold=2):
        self.threshold = threshold

        def detect(self, processed_signal, raw_data):
        _, amounts = raw_data.get_time_series()
        amounts = np.array(amounts)
        mean = np.mean(amounts)
        std = np.std(amounts)
        z_scores = np.abs((amounts - mean) / std)
        anomaly_indices = np.where(z_scores > self.threshold)[0]
        confidence_scores = z_scores[anomaly_indices] / self.threshold

        return {
            'indices': anomaly_indices,
            'scores': confidence_scores,
            'z_scores': z_scores
        }
      ```
      ```python
      class SignalProcessor(ABC): 
    
        @abstractmethod
        def process(self, data):
        pass
    
        @abstractmethod
        def get_name(self):
        pass

      class FFTProcessor(SignalProcessor): 
    
        def __init__(self, sample_rate=1000):
        self.sample_rate = sample_rate
        
        def process(self, data):
        timestamps, amounts = data.get_time_series()
        normalized_amounts = (amounts - np.mean(amounts)) / np.std(amounts)
        spectrum = fft(normalized_amounts)
        return np.abs(spectrum)
    
        def get_name(self):
        return "Fast Fourier Transform"
      ```
I put both codes in there to show how inheritance and abstraction work together like an abusive relationship. Abstraction lays down all the rules without doing any real work, and inheritance just nods along and takes everything, whether it asked for it or not. I used this a lot because it is simply comfortable to use. In all seriousness, inheritance and abstraction are often used together to create well-organized and manageable code.

In the code, abstraction is shown by the abstract base classes FraudDetector and SignalProcessor, which define abstract methods like detect and process that must be implemented by subclasses. Inheritance is demonstrated as ThresholdDetector inherits from FraudDetector, as for FFTProcessor inherits from SignalProcessor, providing specific implementations of these abstract methods.

4.  **Polymorphism**
     ```python
      

   
