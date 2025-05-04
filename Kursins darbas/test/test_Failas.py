import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import networkx as nx
from Failas import DetectorFactory, ProcessorFactory, ThresholdDetector, GraphFraudDetector, TransactionData, FFTProcessor, np, WaveletProcessor
class TestTransactionData(unittest.TestCase):
    def setUp(self):
        self.credit_data = [
            "1622505600,100.0,Amazon,1234",
            "1622509200,250.0,Apple,1234",
            "1622512800,50.0,Amazon,5678"
        ]
        self.insurance_data = [
            "2021-06-01,500.0,POL123,Theft",
            "2021-06-02,2500.0,POL456,Fire"
        ]

    def test_credit_card_parsing(self):
        td = TransactionData(self.credit_data, "credit_card")
        self.assertEqual(td.get_transaction_count(), 3)
        ts, am = td.get_time_series()
        self.assertEqual(len(ts), 3)
        self.assertEqual(len(am), 3)
        self.assertEqual(td.get_transactions()[0]['merchant'], "Amazon")

    def test_insurance_parsing(self):
        td = TransactionData(self.insurance_data, "insurance")
        self.assertEqual(td.get_transaction_count(), 2)
        ts, am = td.get_time_series()
        self.assertEqual(len(ts), 2)
        self.assertEqual(td.get_transactions()[1]['claim_type'], "Fire")

    def test_data_type(self):
        td = TransactionData(self.credit_data, "credit_card")
        self.assertEqual(td.get_data_type(), "credit_card")

    def test_graph_building(self):
        td = TransactionData(self.credit_data, "credit_card")
        G = td.build_transaction_graph()
        self.assertTrue(G.has_edge('1234', 'Amazon'))
        self.assertTrue(G.has_edge('1234', 'Apple'))
        self.assertTrue(G.has_edge('5678', 'Amazon'))

class TestProcessors(unittest.TestCase):
    def setUp(self):
        credit_data = [
            "1622505600,100.0,Amazon,1234",
            "1622509200,250.0,Apple,1234",
            "1622512800,50.0,Amazon,5678"
        ]
        self.td = TransactionData(credit_data, "credit_card")

    def test_fft_processor(self):
        proc = FFTProcessor()
        spectrum = proc.process(self.td)
        self.assertIsInstance(spectrum, np.ndarray)
        self.assertEqual(len(spectrum), 3)

    def test_wavelet_processor(self):
        proc = WaveletProcessor(level=1)
        filtered = proc.process(self.td)
        self.assertIsInstance(filtered, np.ndarray)
        self.assertEqual(len(filtered), 3)

class TestDetectors(unittest.TestCase):
    def setUp(self):
        credit_data = [
            "1622505600,100.0,Amazon,1234",
            "1622509200,250.0,Apple,1234",
            "1622512800,5000.0,Amazon,5678"
        ]
        self.td = TransactionData(credit_data, "credit_card")
        self.proc = FFTProcessor()
        self.signal = self.proc.process(self.td)

    def test_threshold_detector(self):
        detector = ThresholdDetector(threshold=1)
        result = detector.detect(self.signal, self.td)
        self.assertIn('indices', result)
        self.assertTrue(len(result['indices']) > 0)

    def test_graph_detector(self):
        detector = GraphFraudDetector(min_path_amount=100)
        result = detector.detect(None, self.td)
        self.assertIn('suspicious_paths', result)

class TestFactory(unittest.TestCase):
    def test_detector_factory(self):
        d1 = DetectorFactory.create_detector('threshold', threshold=2)
        self.assertIsInstance(d1, ThresholdDetector)
        d2 = DetectorFactory.create_detector('graph', min_path_amount=100)
        self.assertIsInstance(d2, GraphFraudDetector)
        with self.assertRaises(ValueError):
            DetectorFactory.create_detector('unknown')

    def test_processor_factory(self):
        p1 = ProcessorFactory.create_processor('fft')
        self.assertIsInstance(p1, FFTProcessor)
        p2 = ProcessorFactory.create_processor('wavelet')
        self.assertIsInstance(p2, WaveletProcessor)
        with self.assertRaises(ValueError):
            ProcessorFactory.create_processor('unknown')

if __name__ == "__main__":
    unittest.main()