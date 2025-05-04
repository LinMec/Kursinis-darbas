import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from scipy import signal
from scipy.fft import fft
import pywt
from datetime import datetime
import os
import networkx as nx  

class DataLoader(ABC):
    @abstractmethod
    def load(self, file_path):
        pass

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
    
    def _convert_date_to_timestamp(self, date_str):

        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.timestamp()
        
    def get_time_series(self):
        return self.__timestamps, self.__amounts
    
    def get_transactions(self):
        return self.__transactions.copy()
    
    def get_transaction_count(self):
        return len(self.__transactions)
        
    def get_data_type(self):
        return self.__data_type
    
    def build_transaction_graph(self):
        G = nx.DiGraph()
        if self.__data_type == "credit_card":
            for txn in self.__transactions:
                G.add_edge(txn['card_id'], txn['merchant'], 
                          weight=txn['amount'], 
                          timestamp=txn['timestamp'])
        elif self.__data_type == "insurance":
            for claim in self.__transactions:
                G.add_edge(claim['policy_id'], claim['claim_type'], 
                          weight=claim['claim_amount'], 
                          timestamp=self._convert_date_to_timestamp(claim['claim_date']))
        return G

class TextFileLoader(DataLoader): 
    
    def __init__(self, data_type):
        self.data_type = data_type  
    
    def load(self, file_path):
        try:
            with open(file_path, 'r') as file:
                raw_data = file.readlines()
            return TransactionData(raw_data, self.data_type)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return None


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

class WaveletProcessor(SignalProcessor): 
    def __init__(self, wavelet_type='db4', level=5):
        self.wavelet_type = wavelet_type
        self.level = level
    
    def process(self, data):
        timestamps, amounts = data.get_time_series()
        normalized_amounts = (amounts - np.mean(amounts)) / np.std(amounts)
        coeffs = pywt.wavedec(normalized_amounts, self.wavelet_type, level=self.level)
        filtered_coeffs = [coeffs[0]] + [None] * self.level
        filtered_signal = pywt.waverec(filtered_coeffs, self.wavelet_type)
        filtered_signal = filtered_signal[:len(normalized_amounts)]
        
        return filtered_signal
    
    def get_name(self):
        return f"Wavelet Transform ({self.wavelet_type})"


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
        return f"Graph Dijkstra Detector (min_path_amount={self.min_path_amount})"



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



class FraudVisualizer:

    def visualize(self, raw_data, processed_signal, anomalies, processor, detector): 
        data_type = raw_data.get_data_type()
        

        if isinstance(detector, GraphFraudDetector):
            self.visualize_graph_anomalies(raw_data, anomalies)
        else:
            timestamps, amounts = raw_data.get_time_series()
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15), constrained_layout=True)
        
            ax1.plot(amounts, 'b-')
            title_prefix = "Credit Card Transactions" if data_type == "credit_card" else "Insurance Claims"
            ax1.set_title(f'{title_prefix} (Original Data)')
            ax1.set_xlabel('Transaction Index')
            ax1.set_ylabel('Amount')
            
            ax2.plot(processed_signal, 'g-')
            ax2.set_title(f'Processed Signal using {processor.get_name()}')
            ax2.set_xlabel('Signal Index')
            ax2.set_ylabel('Magnitude')
            
            ax3.plot(amounts, 'b-')
            if 'indices' in anomalies and len(anomalies['indices']) > 0:
                anomaly_indices = anomalies['indices']
                anomaly_amounts = [amounts[i] for i in anomaly_indices if i < len(amounts)]
                
                ax3.scatter(anomaly_indices, anomaly_amounts, color='red', marker='o', 
                            s=100, label='Potential Fraud')
                if 'scores' in anomalies:
                    scores = anomalies['scores']
                    for i, (idx, y, s) in enumerate(zip(anomaly_indices, anomaly_amounts, scores)):
                        ax3.annotate(f"{s:.2f}", (idx, y), xytext=(10, 10), 
                                    textcoords='offset points')
            
            ax3.set_title(f'Detected Fraud Anomalies using {detector.get_name()}')
            ax3.set_xlabel('Transaction Index')
            ax3.set_ylabel('Amount')
            ax3.legend()
            plt.show()
    
    def visualize_graph_anomalies(self, raw_data, anomalies):
        G = raw_data.build_transaction_graph()
        suspicious_paths = anomalies.get('suspicious_paths', [])
        if not suspicious_paths:
            print("No suspicious paths found to visualize.")
            return
        plt.figure(figsize=(12, 10), constrained_layout=True)
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                node_size=700, font_size=8, arrows=True)
        edge_labels = {(u, v): f"{d['weight']:.1f}" 
                      for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
        for path, total in suspicious_paths:
            edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
            nx.draw_networkx_edges(G, pos, edgelist=edges, 
                                  edge_color='red', width=2)
        plt.title("Transaction Graph with Suspicious Paths")
        plt.show()
        print("\nSuspicious Paths Details:")
        for i, (path, total) in enumerate(suspicious_paths):
            print(f"{i+1}. Path: {' → '.join([str(node) for node in path])}")
            print(f"   Total amount: {total:.2f}")
            print()
            



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
        
        #Sitoje vietoje yra rasomi failai 
        output_path = r"C:\Users\mecko\OneDrive\Desktop\Kursins darbas\info.txt"
   
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



def main():
    print("Select data type to analyze:")
    print("1. Credit Card Transactions")
    print("2. Insurance Claims")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        data_type = "credit_card"
        file_path = r"C:\Users\mecko\OneDrive\Desktop\Kursins darbas\credit_card_transactions.txt"
        
    elif choice == "2":
        file_path = r"C:\Users\mecko\OneDrive\Desktop\Kursins darbas\insurance_claims.txt"
        data_type = "insurance"

    else:
        print("Invalid choice. Defaulting to Credit Card Transactions.")

    print("\nSelect detection method:")
    print("1. Signal Processing (FFT + Threshold)")
    print("2. Graph Theory (Dijkstra's Algorithm)")
    
    method_choice = input("Enter choice (1 or 2): ")
    

    loader = TextFileLoader(data_type)
    if method_choice == "2":
        processor = ProcessorFactory.create_processor("fft") 
        detector = DetectorFactory.create_detector("graph", min_path_amount=5000)
    else:
     
        processor = ProcessorFactory.create_processor("fft")
        detector = DetectorFactory.create_detector("threshold", threshold=1.5)
    visualizer = FraudVisualizer()
    fraud_system = FraudAnalysisSystem(loader, processor, detector, visualizer)
    fraud_system.analyze(file_path)
if __name__ == "__main__":
    main()
