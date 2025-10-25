# Quantum RNG Data Sources Documentation

This document provides detailed information about each quantum random number generation source used in the Unified Quantum RNG API.

---

## 1. ANU Quantum Random Number Generator (QRNG)

### Organization
**Australian National University (ANU) - School of Physics**

**Location:** Canberra, Australia  
**Website:** https://qrng.anu.edu.au/  
**Research Group:** Quantum Optics Group, Department of Quantum Science

### Description

The ANU QRNG is one of the world's most well-known and trusted sources of quantum-generated random numbers. It has been providing true quantum randomness to researchers, cryptographers, and the general public since 2007.

### How It Works

**Technology:** Vacuum State Quantum Fluctuations

The ANU QRNG measures quantum fluctuations of the electromagnetic field vacuum state using a technique called **homodyne detection**:

1. **Quantum Process:** The generator measures the quantum fluctuations of vacuum state in the electromagnetic field
2. **Physical Basis:** These fluctuations arise from Heisenberg's uncertainty principle - at the quantum level, even "empty space" has measurable random fluctuations
3. **Detection Method:** A laser beam is split and recombined, and the quantum interference pattern is measured
4. **Digitization:** The analog quantum measurements are converted to digital random bits
5. **Output Format:** Unsigned 16-bit integers (uint16), values range from 0 to 65,535

### Scientific Foundation

- Based on fundamental quantum mechanics principles
- Randomness is intrinsic and unpredictable - not pseudo-random
- Passes all standard statistical tests for randomness (NIST, Diehard, TestU01)
- Cannot be reproduced or predicted, even in principle

### Applications

- Cryptographic key generation
- Scientific simulations requiring true randomness
- Secure communications
- Research in quantum mechanics and information theory
- Fair lottery and gaming applications

### Academic Background

The ANU School of Physics has been a world leader in quantum optics research for over 30 years, with numerous breakthrough discoveries in quantum information science, quantum teleportation, and quantum computing.

---

## 2. LfD Laboratorium für Datenverarbeitung QRNG

### Organization
**Laboratorium für Datenverarbeitung (Laboratory for Data Processing)**

**Location:** Germany  
**Website:** https://lfdr.de/qrng_api/  
**Technology Provider:** ID Quantique (IDQ)

### Description

LfD provides quantum random numbers through a public API using certified quantum RNG hardware from ID Quantique, a Swiss company that is a global leader in quantum-safe cryptography and quantum random number generation.

### How It Works

**Technology:** Quantum Photonic Detection (IDQ Quantis)

The system uses ID Quantique's Quantis QRNG technology:

1. **Quantum Process:** Single photon detection at a beam splitter
2. **Physical Basis:** When a photon hits a beam splitter, quantum mechanics dictates that it has a 50/50 probability of going either direction - this is true quantum randomness from superposition
3. **Detection:** High-sensitivity photodetectors measure which path each photon takes
4. **Timing Method:** The random arrival time of photons is also used as an entropy source
5. **Output Format:** Raw random bytes in hexadecimal format

### Certification and Standards

**ID Quantique's Quantis QRNG:**
- Certified by multiple international security agencies
- Complies with NIST SP 800-90B entropy source validation
- Used in commercial quantum cryptography systems
- Deployed in government and financial institutions worldwide
- Common Criteria EAL4+ certified (security evaluation standard)

### Applications

- Military-grade cryptography
- Financial transaction security
- Secure key distribution
- Quantum key distribution (QKD) systems
- High-security random number generation for sensitive applications

### Technology Background

ID Quantique was founded in 2001 as a spin-off from the University of Geneva's Group of Applied Physics. They are the world's first commercial quantum cryptography company and hold numerous patents in quantum random number generation.

---

## 3. CURBy Local Quantum Data

### Organization
**Local Dataset with SHA-3 Cryptographic Extraction**

**Source:** Pre-generated quantum data  
**File Format:** CSV (random_packed_u32be.csv)  
**Processing:** Cryptographic extraction using SHA-3

### Description

CURBy provides pre-computed quantum random numbers that have been processed through cryptographic randomness extractors to ensure uniform distribution and remove any potential bias from the original quantum source.

### How It Works

**Technology:** Quantum Source + Cryptographic Extractor

1. **Original Source:** Quantum measurements (details in source documentation)
2. **Packing Algorithm:** Binary packing with mapping: 1→0, 2→1
3. **Bit Order:** MSB first (Most Significant Bit first)
4. **Extractor:** SHA-3 (SHA3-256) block processing
5. **Storage:** Pre-computed values stored in CSV format
6. **Selection:** ANU QRNG seeds determine which row to use
7. **Output Formats:** 
   - uint32 (32-bit unsigned integers)
   - uint8 (8-bit unsigned bytes)

### SHA-3 Cryptographic Extractor

**Purpose:** Randomness extraction ensures that even if the original quantum source has slight imperfections or correlations, the output is cryptographically uniform and unbiased.

**SHA-3 Properties:**
- Winner of NIST's Cryptographic Hash Algorithm Competition (2012)
- Based on Keccak algorithm
- Provides strong avalanche effect (small input change → completely different output)
- Resistant to all known cryptanalytic attacks
- Serves as a perfect randomness extractor

### Advantages

1. **Speed:** Pre-computed values provide instant access
2. **Reliability:** No network dependency for generation
3. **Quality:** Cryptographic extraction ensures maximum entropy
4. **Verification:** Output can be tested and verified before deployment
5. **Reproducibility:** Specific rows can be referenced for auditing

### Use Cases

- High-performance applications requiring minimal latency
- Offline cryptographic operations
- Systems requiring guaranteed availability
- Reproducible research requiring documented random sources
- Batch processing of cryptographic operations

---

## 4. Global Consciousness Project (GCP) Egg Data

### Organization
**Global Consciousness Project / Institute of Noetic Sciences**

**Founded:** 1998 (originated from Princeton's PEAR lab)  
**Website:** https://global-mind.org/  
**Director:** Dr. Roger Nelson (Director Emeritus, Princeton PEAR Lab)

### Description

The Global Consciousness Project is a long-running international scientific collaboration studying whether collective human consciousness can be detected in physical systems. The project maintains a worldwide network of quantum Random Event Generators (REGs), affectionately called "Eggs," continuously generating random data.

### How It Works

**Technology:** Distributed Network of Quantum Random Event Generators

#### Hardware - The "Eggs"
Each Egg is a quantum random number generator:
- Based on electronic quantum tunneling or quantum optical processes
- Generates continuous stream of random bits (typically 200 bits/second)
- Time-stamped to microsecond precision
- Automatically uploads data to central servers

#### Network
- **Coverage:** ~50-70 active Eggs distributed globally
- **Locations:** Universities, research centers, private hosts across 6 continents
- **Continuous Operation:** 24/7 data collection since 1998
- **Data Volume:** Over 20 years of continuous quantum random data

#### Data Outputs

**1. persec (Per-Second Data)**
- Raw bit count per second from each Egg
- Expected value: 100 (with 200 trials, expecting 50% ones)
- Actual measurements: typically 80-120 range
- Format: Array of integer counts per Egg, indexed by Unix timestamp

**2. persecz (Per-Second Z-Score)**
- Standard deviations from expected randomness
- Formula: (observed - expected) / standard_error
- Measures how far each second's data deviates from pure randomness
- Values: typically -3 to +3 (68% within ±1, 95% within ±2)
- Positive = more ones than expected; Negative = fewer ones than expected

**3. perseczcs (Per-Second Z-Score Cumulative Sum)**
- Running sum of Z-scores over time
- Shows long-term trends and persistence of deviations
- Random walk pattern expected for pure randomness
- Significant slopes may indicate persistent non-random periods

**4. Stouffer Z (Combined Statistic)**
- Combines data from all active Eggs into single measure
- Meta-analysis technique: combines p-values across independent tests
- Shows whether network as a whole is deviating from randomness
- Global measure of potential "coherence" across all generators

**5. CSZ²-1 (Cumulative Stouffer Z Squared Minus One)**
- Chi-squared variant of cumulative Stouffer statistic
- Squares eliminate direction (both high and low deviations contribute equally)
- Cumulative version shows long-term trends
- Minus one normalizes to expected value of zero

### Research Hypothesis

The GCP investigates whether:
1. Major world events (disasters, celebrations, global attention) correlate with deviations from randomness
2. Human consciousness has a detectable effect on physical quantum systems
3. Global consciousness can produce measurable coherence in distributed quantum generators

### Notable Findings

**Events with Reported Anomalies:**
- September 11, 2001 attacks: Significant network-wide deviation
- Princess Diana's funeral: Correlation with global attention
- New Year's Eve celebrations: Recurring patterns
- Major earthquakes and tsunamis
- Olympic opening ceremonies
- Papal events and religious gatherings

**Important Notes:**
- Results remain controversial and debated
- Statistical significance varies by analysis method
- Not accepted by mainstream physics (yet studied seriously)
- Provides unique dataset regardless of interpretation

### Scientific Background

**Origins:**
- Princeton Engineering Anomalies Research (PEAR) Lab (1979-2007)
- Founded by Robert G. Jahn (Dean Emeritus of Princeton Engineering)
- Decades of research on consciousness-related anomalies

**Current Status:**
- Continues under Institute of Noetic Sciences
- International academic collaboration
- Peer-reviewed publications in consciousness studies journals
- Open data access for independent researchers

### Data Applications

**Beyond GCP's Primary Research:**
1. **True Randomness Source:** High-quality quantum random data
2. **Network Science:** Studying distributed quantum systems
3. **Time-Series Analysis:** Long-duration quantum measurements
4. **Entropy Source:** Geographically diverse randomness
5. **Temporal Analysis:** Time-stamped quantum data for correlation studies
6. **Global Synchronization:** Studying correlations in distributed quantum systems

### Accessing the Data

- Real-time data available at https://global-mind.org/realtime/
- Historical data archives available for research
- API format: CSV download with multiple statistical measures
- Update frequency: Minute-by-minute (60-second windows)
- Data includes: timestamp, per-Egg measurements, network statistics

---

## 5. I Ching Hexagram Derivation

### Tradition
**I Ching (易經) - The Book of Changes**

**Origin:** Ancient China (Zhou Dynasty, ~1000 BCE)  
**Age:** Over 3,000 years old  
**Cultural Status:** One of the oldest Chinese classical texts

### Description

The I Ching is an ancient divination system based on 64 hexagrams, each composed of six lines that are either broken (yin ☷) or unbroken (yang ☰). It has been used for divination, philosophy, and decision-making for millennia and influenced Taoist and Confucian philosophy.

### Traditional Method

**Yarrow Stalk Method (Traditional):**
1. Begin with 50 yarrow stalks (one set aside, 49 used)
2. Perform elaborate ritual of dividing and counting stalks
3. Repeat process 3 times per line
4. Repeat for all 6 lines (18 divisions total)
5. Results in values: 6, 7, 8, or 9 for each line
6. Build hexagram from bottom to top

**Traditional Probabilities:**
- 6 (old yin, changing): 1/16 = 6.25%
- 7 (young yang, stable): 5/16 = 31.25%
- 8 (young yin, stable): 7/16 = 43.75%
- 9 (old yang, changing): 3/16 = 18.75%

### Quantum Implementation

**How This System Uses Quantum Randomness:**

1. **Entropy Source:** Uses bytes from LfD QRNG (quantum photonic randomness)
2. **Algorithm:** Simulates traditional yarrow stalk probabilities exactly
3. **Process:** 
   - Map quantum random bytes to probability distribution
   - Generate 6 line values (6, 7, 8, or 9)
   - Construct original hexagram
   - Apply changes (6→yang, 9→yin) to create resulting hexagram
4. **Output:**
   - Original hexagram (1-64)
   - Resulting hexagram (1-64, after changes)
   - Line values and changing lines
   - Binary representation
   - Traditional names and interpretations

### The 64 Hexagrams

Each hexagram has:
- **Number:** 1-64 (King Wen sequence)
- **Chinese Name:** Traditional name in Chinese characters
- **Translation:** English meaning
- **Judgment:** Confucian interpretation
- **Image:** Symbolic representation
- **Line Texts:** Interpretation for each of 6 lines

**Example Hexagrams:**
- Hexagram 1: 乾 Qián (The Creative, pure yang ☰☰)
- Hexagram 2: 坤 Kūn (The Receptive, pure yin ☷☷)
- Hexagram 63: 既濟 Jì Jì (After Completion)
- Hexagram 64: 未濟 Wèi Jì (Before Completion)

### Philosophical Significance

**Core Concepts:**
- **Change:** The only constant is change itself
- **Yin-Yang:** Complementary opposites in dynamic balance
- **Transformation:** "Changing lines" represent transition points
- **Wisdom:** Not prediction, but understanding of patterns and principles

**Applications:**
- Personal decision-making and reflection
- Understanding situation dynamics
- Strategic planning
- Meditation and contemplation
- Connecting quantum randomness to ancient wisdom traditions

### Why Combine Quantum RNG with I Ching?

1. **True Randomness:** Quantum mechanics provides genuine unpredictability
2. **Cultural Bridge:** Links cutting-edge physics with ancient philosophy
3. **Interpretive Framework:** Gives meaning to quantum randomness
4. **Philosophical Experiment:** Explores relationship between quantum mechanics and consciousness
5. **Practical Use:** Provides decision-making tool backed by quantum entropy

### Mathematical Perfection

The quantum implementation:
- Exactly replicates traditional yarrow stalk probability distribution
- Maintains 3:1:5:7 ratio (normalized to sixteenths)
- Preserves balance between yin and yang
- Honors traditional hexagram ordering and relationships

---

## Summary Comparison

| Source | Type | Technique | Output | Speed | Use Case |
|--------|------|-----------|--------|-------|----------|
| **ANU** | Live API | Vacuum fluctuations | uint16 | ~100ms | Real-time quantum randomness |
| **LfD** | Live API | Photon detection | bytes (hex) | ~100ms | Cryptographic applications |
| **CURBy** | Local file | SHA-3 extraction | uint32/uint8 | <1ms | High-speed, offline |
| **GCP Eggs** | Live API | Distributed QRNGs | Statistics | ~5s | Global consciousness research |
| **I Ching** | Derivation | LfD bytes | Hexagrams | derived | Divination, philosophy |

---

## Quality Assurance

All sources provide:
- **True Randomness:** Based on quantum mechanical processes
- **Statistical Validity:** Pass standard randomness tests
- **Unpredictability:** Cannot be reproduced or predicted
- **Entropy:** Full entropy for cryptographic use (ANU, LfD, CURBy)
- **Auditability:** Sources are documented and verifiable

---

## References and Further Reading

### ANU QRNG
- ANU QRNG Website: https://qrng.anu.edu.au/
- Research Paper: "A fast physical random number generator" (2008)
- GitHub: Sample implementations and tools

### LfD / ID Quantique
- LfD API: https://lfdr.de/qrng_api/
- ID Quantique: https://www.idquantique.com/
- Quantis QRNG Documentation

### Global Consciousness Project
- Main Site: https://global-mind.org/
- Real-time Data: https://global-mind.org/realtime/
- Publications: http://noosphere.princeton.edu/papers/

### I Ching
- "I Ching: Book of Changes" - Various translations (Wilhelm, Huang, Legge)
- "The Tao of Physics" - Fritjof Capra (connections to quantum mechanics)
- Online I Ching resources for hexagram interpretations

### Quantum Randomness
- NIST Randomness Beacon: https://www.nist.gov/programs-projects/nist-randomness-beacon
- Quantum Random Number Generation (Scientific reviews)
- Bell's Theorem and quantum indeterminacy

---

## Version Information

- **Document Version:** 1.0
- **Last Updated:** October 24, 2025
- **API Version:** 1.0
- **Authors:** RNG Unified Development Team

