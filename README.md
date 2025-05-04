# Fraud detection system (with Signal and Graph visualization and its applications)


## Introduction

A Python program to detect and trace financial fraud by analyzing data patterns. Visualizes findings via signal (wavelet/FFT) and graph-based models.

---

### What does it do?

This program is designed to detect and trace financial fraud by analyzing data patterns. It visualizes its findings either via signal (where wavelet and FFT is used, and is compared to the threshold), or through graph-based models that illustrate relationships using vertices and edges.

---

### How to Run

1. **Install dependencies:**
    ```
    pip install numpy matplotlib scipy pywavelets networkx
    ```
2. Place all data files in the same folder, open it in Visual Studio Code, and use the Explorer to navigate them.

3. Run the program

## Body analysis

### OOP 4 pillars

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
    
Transactions, amounts, and every other morsel of data are securely stuffed inside layers of encapsulation. Why? Because cyber-attacks are out there, lurking, like a badly tuned Audi A3 in "Krasnucha", ready to ruin your day. But in all seriousness, it's the main use of encapsulation - safety, so that only intended users would be able to get the data.

Encapsulation in this TransactionData class hides the internal data structures such as __transactions, __timestamps, and __amounts by making them private with double underscores. This prevents direct access or modification of these attributes from outside the class, ensuring data integrity. The class controls how raw input data is parsed and stored through the private method __parse_data, centralizing and protecting the parsing logic.

2/3.  **Abstraction/Inheritance**

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

class SignalProcessor(ABC): #second code here
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

        def get_name(self):
        return f"Threshold Detector (threshold={self.threshold})"  

    class GraphFraudDetector(FraudDetector): 

        def __init__(self, min_path_amount=5000):
        self.min_path_amount = min_path_amount

        def detect(self, processed_signal, raw_data):
        G = raw_data.build_transaction_graph()
        suspicious_paths = []
        nodes = list(G.nodes)
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):  
                if i != j and nx.has_path(G, nodes[i], nodes[j]):
                    try:
                        path = nx.dijkstra_path(G, nodes[i], nodes[j], weight='weight')
                        total = 0
                        for k in range(len(path)-1):
                            total += G[path[k]][path[k+1]]['weight']
                            
                        if total > self.min_path_amount:
                            suspicious_paths.append((path, total))
                    except nx.NetworkXNoPath:
                        continue
        return {
            'suspicious_paths': suspicious_paths
        }
        def get_name(self):
        return f"Graph Dijkstra Detector (min_path_amount={self.min_path_amount})
    ```

Polymorphism isn’t just code, it’s a shapeshifting virus in a trench coat, sliding through 32 shadow interfaces like a neural ghost jacked into corporate mainframes. Every time you invoke a method, a child's dream is overriden with existential dread.

The FraudDetector interface defines the abstract detect(self, processed_signal, raw_data) method. The ThresholdDetector and GraphFraudDetector classes implement distinct fraud detection algorithms. Polymorphism enables the FraudAnalysisSystem to use any FraudDetector implementation through its detect method

## Design pattern

   **Factory Method**
   
   ```python
    
    class DetectorFactory: 
        @staticmethod
        def create_detector(detector_type, **kwargs):
        if detector_type == "threshold":
            return ThresholdDetector(**kwargs)
        elif detector_type == "graph":
            return GraphFraudDetector(**kwargs)
        else:
            raise ValueError(f"Unsupported detector type: {detector_type}")

    class ProcessorFactory:
        @staticmethod
        def create_processor(processor_type, **kwargs):
            if processor_type == "fft":
                return FFTProcessor(**kwargs)
            elif processor_type == "wavelet":
                return WaveletProcessor(**kwargs)
            else:
                raise ValueError(f"Unsupported processor type: {processor_type}")
```

I chose the Factory Method over Singleton, Prototype, or Builder because I need an interface to create families of related objects without specifying concrete classes. The Singleton ensures a single instance, which isn’t needed, while Prototype focuses on cloning objects, which doesn't align with my need for diverse algorithm types. The Builder would add unnecessary complexity for this purpose.

I needed it for creating families of related objects, easy extensability, and abstraction. 

The detectorFactory is responsible for creating different types of FraudDetector objects (ThresholdDetector, GraphFraudDetector). The create_detector static method takes a detector_type string and optional keyword arguments to instantiate the appropriate concrete detector.

## Composition/aggregation

 1. **Aggregation**

 ```python
class FraudAnalysisSystem: 
    
    def __init__(self, data_loader, signal_processor, fraud_detector, visualizer): 
        self.data_loader = data_loader
        self.signal_processor = signal_processor
        self.fraud_detector = fraud_detector
        self.visualizer = visualizer
    
    def analyze(self, file_path):
        raw_data = self.data_loader.load(file_path)
        if raw_data is None:
            return None
        
        script_dir = Path(__file__).parent
        script_dir = Path.cwd()
        output_path = script_dir / "info.txt"
   
        if isinstance(self.fraud_detector, GraphFraudDetector):
            with open(output_path, "w") as f:
                f.write(f"Loaded {raw_data.get_transaction_count()} transactions of type {raw_data.get_data_type()}\n")
                f.write(f"Using graph-based detection with {self.fraud_detector.get_name()}\n")


            anomalies = self.fraud_detector.detect(None, raw_data)
            suspicious_paths_count = len(anomalies.get('suspicious_paths', []))
            with open(output_path, "w") as f:
             f.write(f"Loaded {raw_data.get_transaction_count()} transactions of type {raw_data.get_data_type()}\n")
             f.write(f"Detected {suspicious_paths_count} suspicious transaction paths")
        else:

            processed_signal = self.signal_processor.process(raw_data)
            with open(output_path, "w") as f:
                f.write(f"Processed signal using {self.signal_processor.get_name()}\n")
                anomalies = self.fraud_detector.detect(processed_signal, raw_data)
                anomaly_count = len(anomalies.get('indices', []))
                f.write(f"Detected {anomaly_count} potential fraud cases using {self.fraud_detector.get_name()}\n")
 
        self.visualizer.visualize(raw_data, 
                                 self.signal_processor.process(raw_data) if not isinstance(self.fraud_detector, GraphFraudDetector) else None,
                                 anomalies, 
                                 self.signal_processor, 
                                 self.fraud_detector)
        
        return anomalies
```

The FraudAnalysisSystem aggregates instances of DataLoader, SignalProcessor, FraudDetector, and FraudVisualizer. It relies on these independent objects to perform their specific tasks (loading data, processing signals, detecting fraud, and visualizing results).

2. **Composition**
   
```python

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
                timestamp = float(parts[0])
                amount = float(parts[1])
                merchant = parts[2]
                card_id = parts[3]
                
                self.__timestamps.append(timestamp)
                self.__amounts.append(amount)
                self.__transactions.append({
                    'timestamp': timestamp,
                    'amount': amount,
                    'merchant': merchant,
                    'card_id': card_id
                })
            elif self.__data_type == "insurance":

                claim_date = parts[0]
                claim_amount = float(parts[1])
                policy_id = parts[2]
                claim_type = parts[3]
                
                self.__timestamps.append(self._convert_date_to_timestamp(claim_date))
                self.__amounts.append(claim_amount)
                self.__transactions.append({
                    'claim_date': claim_date, 
                    'claim_amount': claim_amount,
                    'policy_id': policy_id,
                    'claim_type': claim_type
                })
```
The TransactionData class composes its internal data structures (__transactions, __timestamps, __amounts, __data_type). These lists and the data type are parts of the TransactionData object, which are quite important.

    


      

   
