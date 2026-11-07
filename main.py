import numpy as np
import time

# ==============================================================================
# QuLattice-Decoy: High-Throughput Verification Testbench (10,000 Bits)
# Author: SOUNTHIRA MANICKAM K
# Track 1: Advanced Cryptography (Mathematics for Systems Security)
# ==============================================================================

N = 128          # Lattice dimension
Q = 2053         # Prime modulus
SIGMA = 3.0      # Discrete Gaussian noise standard deviation

def setup_keys():
    """Generates 4-layer partitioned key shares and master public key."""
    hw1 = np.random.randint(-1, 2, size=N)
    sw1 = np.random.randint(-1, 2, size=N)
    sw2 = np.random.randint(-1, 2, size=N)
    hw2 = np.random.randint(-1, 2, size=N)
    
    s_master = (hw1 + sw1 + sw2 + hw2) % Q
    A = np.random.randint(0, Q, size=(N, N))
    e = np.round(np.random.normal(0, SIGMA, size=N)).astype(int)
    B = (np.dot(A, s_master) + e) % Q
    
    return A, B, (hw1, sw1, sw2, hw2)

def run_testbench(total_bits=10000):
    A, B, shares = setup_keys()
    hw1, sw1, sw2, hw2 = shares
    s_recon = (hw1 + sw1 + sw2 + hw2) % Q
    
    input_stream = np.random.randint(0, 2, size=total_bits)
    decrypted_stream = []
    
    print(f"[*] Starting QuLattice-Decoy 10,000-Bit Verification Pipeline...")
    start_time = time.time()
    
    for idx, bit in enumerate(input_stream):
        # 1. LWE Encryption
        r = np.random.randint(-1, 2, size=N)
        e1 = np.round(np.random.normal(0, SIGMA, size=N)).astype(int)
        e2 = int(np.round(np.random.normal(0, SIGMA)))
        
        u = (np.dot(A.T, r) + e1) % Q
        v = (np.dot(B, r) + e2 + (Q // 2) * bit) % Q
        
        # 2. 10-Channel Decoy Multi-Path Routing
        true_channel = np.random.randint(0, 10)
        channel_bits = []
        
        for ch in range(10):
            if ch == true_channel:
                m_raw = (v - np.dot(u, s_recon)) % Q
                d0 = min(m_raw, Q - m_raw)
                d1 = abs(m_raw - (Q // 2))
                channel_bits.append(0 if d0 < d1 else 1)
            else:
                dummy_s = np.random.randint(-1, 2, size=N)
                _ = (v - np.dot(u, dummy_s)) % Q
                channel_bits.append(0)
                
        decrypted_stream.append(channel_bits[true_channel])
        
    elapsed = time.time() - start_time
    errors = np.sum(input_stream != np.array(decrypted_stream))
    ber = (errors / total_bits) * 100
    
    print("\n" + "=" * 55)
    print("TESTBENCH AUDIT RESULTS (10,000 Bits)")
    print("=" * 55)
    print(f"Total Bits Processed    : {total_bits:,}")
    print(f"Total Execution Time    : {elapsed:.2f} seconds")
    print(f"Average Bit Latency     : {(elapsed/total_bits)*1000:.4f} ms/bit")
    print(f"Bit Errors Detected     : {errors}")
    print(f"Bit Error Rate (BER)    : {ber:.4f}%")
    print(f"Decryption Accuracy     : {100.0 - ber:.4f}%")
    print("=" * 55)

if __name__ == "__main__":
    run_testbench(10000)