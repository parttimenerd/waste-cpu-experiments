Waste-CPU Experiments
=====================

A collection of C programs demonstrating different CPU-wasting implementations for performance comparison and compiler optimization analysis.

## Overview

This project compares various CPU-intensive strategies to understand their performance characteristics under different compiler optimizations. Each implementation uses the same interface but different internal approaches to consume CPU cycles efficiently. The Python management script provides comprehensive performance analysis including statistical measurement and system call tracing.

## Files

- `basic.c` - Simple CPU-wasting loop using clock() function
- `for-loop.c` - CPU-intensive loop with nested arithmetic operations
- `volatile-loop.c` - CPU-wasting loop with volatile operations
- `noinline.c` - CPU-wasting loop with noinline function attribute
- `noopt.c` - CPU-intensive loop with optimization barriers
- `alarm.c` - Signal-based timing using alarm() and setjmp/longjmp
- `main.h` - Shared header with main function and timing utilities
- `waste_cpu.py` - Comprehensive Python utility for compilation and performance analysis

## Quick Start

```bash
# Build and test basic implementation
python3 waste_cpu.py compile basic
./basic 3

# Compare performance with statistical analysis
python3 waste_cpu.py perf basic -r 5      # Run 5 times for statistics
python3 waste_cpu.py perf for-loop -r 5

# Measure system calls (requires root)
sudo python3 waste_cpu.py perf basic --syscalls

# View help for all options
python3 waste_cpu.py --help
```

## Usage

### Python Script Commands

The `waste_cpu.py` script provides four main commands:

#### compile
Compile C source files with configurable optimization levels:
```bash
python3 waste_cpu.py compile basic -O2    # Compile with -O2
python3 waste_cpu.py compile for-loop -O0 # Compile with no optimization
```

#### code
Display source code with optional main function:
```bash
python3 waste_cpu.py code basic           # Show includes and wait() function
python3 waste_cpu.py code basic --add-main # Include main() function
```

#### perf
Run performance analysis with comprehensive metrics:
```bash
# Basic performance measurement
python3 waste_cpu.py perf basic -d 5      # 5-second test

# Statistical analysis with multiple runs
python3 waste_cpu.py perf basic -r 10     # Run 10 times, show mean/std dev

# System call tracing (requires root)
sudo python3 waste_cpu.py perf basic --syscalls

# Combined options
python3 waste_cpu.py perf for-loop -O1 -d 3 -r 5
```

#### perf-all
Run performance tests on all C files in the directory:
```bash
# Test all implementations with default settings
python3 waste_cpu.py perf-all

# Test all with custom duration and multiple runs
python3 waste_cpu.py perf-all -d 3 -r 5

# System call analysis on all implementations
sudo python3 waste_cpu.py perf-all --syscalls -d 2
```

#### Options

- `-O, --optimize`: Optimization level (0-3, default: 3)
- `-d, --duration`: Duration in seconds for perf tests (default: 10)
- `-r, --runs`: Number of test runs for statistical analysis (default: 1)
- `--syscalls`: Measure system calls instead of performance counters (requires root)
- `--add-main`: Include main function in code display

## Performance Measurement Features

### Statistical Analysis
When using multiple runs (`-r` option), the script provides:
- **Mean values** for all metrics
- **Standard deviation** as percentages
- **Min/Max values** across all runs
- **Right-aligned formatting** for easy comparison

### Performance Metrics (Default Mode)
- **Cycles** - CPU cycles consumed
- **Instructions** - Instructions executed  
- **Insn/Cycle** - Instructions per cycle (IPC)
- **Cache Refs/Misses** - Memory access patterns and cache miss percentage
- **Branches** - Total branch instructions executed
- **Branch Misses** - Branch prediction failures and miss percentage
- **Timing** - Elapsed, user, and system time
- **Time Accuracy %** - How close actual runtime was to requested duration
- **Sys Time %** - System time as percentage of total CPU time
- **Sys Time %** - System time as percentage of total CPU time

### System Call Tracing (`--syscalls` mode)
- **Total Syscalls** - Overall system call count
- **Individual Syscalls** - Breakdown by syscall type, ordered by frequency
- **Zero filtering** - Only shows syscalls that actually occurred
- **Timing metrics** - Same timing information as performance mode

## Examples

### Basic Performance Testing
```bash
# Single run performance measurement
python3 waste_cpu.py perf basic -d 5

# Statistical analysis across multiple runs  
python3 waste_cpu.py perf basic -d 3 -r 10

# Compare all implementations at once
python3 waste_cpu.py perf-all -d 3 -r 5

# Compare specific implementations individually
python3 waste_cpu.py perf basic -r 5
python3 waste_cpu.py perf for-loop -r 5
python3 waste_cpu.py perf alarm -r 5
```

### Optimization Level Comparison
```bash
# Compare optimization levels statistically
python3 waste_cpu.py perf basic -O0 -r 5    # No optimization
python3 waste_cpu.py perf basic -O1 -r 5    # Basic optimization  
python3 waste_cpu.py perf basic -O2 -r 5    # Standard optimization
python3 waste_cpu.py perf basic -O3 -r 5    # Aggressive optimization
```

### System Call Analysis
```bash
# Basic syscall tracing (requires root)
sudo python3 waste_cpu.py perf basic --syscalls -d 2

# Statistical syscall analysis on single implementation
sudo python3 waste_cpu.py perf volatile-loop --syscalls -d 3 -r 5

# Compare syscall patterns across all implementations
sudo python3 waste_cpu.py perf-all --syscalls -d 2
```

### Code Inspection
```bash
# View source code
python3 waste_cpu.py code basic           # Function only
python3 waste_cpu.py code basic --add-main # Include main()

# Compare implementations
python3 waste_cpu.py code basic
python3 waste_cpu.py code for-loop
python3 waste_cpu.py code volatile-loop
python3 waste_cpu.py code alarm
```

## Requirements

- **Python 3.6+** with standard library modules (subprocess, argparse, statistics, re)
- **GCC compiler** for C compilation
- **Linux perf utility** for performance measurement and syscall tracing
- **Root privileges** for syscall tracing (sudo access)

## Installation

```bash
# Install perf utility (Ubuntu/Debian)
sudo apt-get install linux-tools-common linux-tools-generic

# Install perf utility (Red Hat/CentOS/Fedora)  
sudo yum install perf
# or
sudo dnf install perf

# Clone/download the project
git clone https://github.com/parttimenerd/waste-cpu
cd waste-cpu
```

## License

MIT License - Copyright (c) 2025 SAP SE or an SAP affiliate company, Johannes Bechberger and waste-cpu contributors 
