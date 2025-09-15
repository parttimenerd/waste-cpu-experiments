#!/usr/bin/env python3
"""
waste-cpu Experiments Manager

A utility script to compile, view, and benchmark CPU-wasting implementations.
"""
import os
import sys
import argparse
import subprocess


class WasteCpuManager:
    def __init__(self):
        self.cc = "gcc"
        self.cflags = ["-Wall", "-Wextra"]
        self.perf_duration = 10
        self.opt_level = 3  # Default to -O3
        self.working_dir = os.getcwd()

    def compile(self, filename, extra_args=None):
        """Compile a .c file into an executable."""
        if not filename.endswith(".c"):
            filename = f"{filename}.c"
            
        basename = os.path.splitext(filename)[0]
        opt_flag = f"-O{self.opt_level}"
        
        cmd = [self.cc, opt_flag] + self.cflags + ["-o", basename, filename]
        if extra_args:
            cmd.extend(extra_args)
            
        print(f"Compiling {filename} with {opt_flag}...")
        result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            print(f"Successfully compiled {basename}")
            return True
        else:
            print(f"Error compiling {basename}:")
            print(result.stderr)
            return False
    
    def show_code(self, filename, include_main=False):
        """Display the full source code for a file and main.h."""
        if not filename.endswith(".c"):
            filename = f"{filename}.c"
            
        if not os.path.exists(filename):
            print(f"Error: File {filename} not found")
            return False
        
        try:
            # Read main.h and extract includes
            with open("main.h", "r") as f:
                main_content = f.read()
            
            main_lines = main_content.split('\n')
            includes = []
            for line in main_lines:
                if line.strip().startswith('#include'):
                    includes.append(line)
            
            # Always show includes from main.h
            for include in includes:
                print(include)
            print()
            
            # Show the .c file content (skip #include "main.h")
            with open(filename, "r") as f:
                content = f.read()
                lines = content.split('\n')
                for line in lines:
                    if not line.strip().startswith('#include "main.h"'):
                        print(line)
            
            # Optionally show main function
            if include_main:
                print()
                main_lines = main_content.split('\n')
                in_main = False
                for line in main_lines:
                    if 'int main(' in line:
                        in_main = True
                    if in_main:
                        print(line)
            
            return True
            
        except FileNotFoundError as e:
            print(f"Error: Could not find file {e.filename}")
            return False
    

    
    def perf(self, filename, duration=None, runs=1, syscalls=False, quiet_runs=False):
        """Run performance analysis using perf stat."""
        if not filename.endswith(".c"):
            basename = filename
            filename = f"{filename}.c"
        else:
            basename = os.path.splitext(filename)[0]
            
        # Always rebuild the program before perf testing
        if not self.compile(filename):
            return False
                
        # Use provided duration or default
        duration = duration or self.perf_duration
        
        mode_desc = "syscalls" if syscalls else "performance counters"
        print(f"Running {basename} {runs} time{'s' if runs > 1 else ''} for {duration} seconds each (measuring {mode_desc})...")
        
        # Check if syscalls mode requires root privileges
        if syscalls and os.getuid() != 0:
            print("Warning: Syscalls measurement may require root privileges. If it fails, try running with sudo.")
        
        results = []
        if quiet_runs:
            print("Runs: ", end="", flush=True)
            
        for run in range(runs):
            if runs > 1:
                if quiet_runs:
                    print(".", end="", flush=True)
                else:
                    print(f"  Run {run + 1}/{runs}...", end=" ", flush=True)
            
            cmd = ["perf", "stat"]
            
            if syscalls:
                # Count both total syscalls and individual syscalls
                cmd.extend(["-e", "raw_syscalls:sys_enter,syscalls:sys_enter_*"])
            else:
                cmd.append("--")
                
            cmd.extend([f"./{basename}", str(duration)])
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                if not quiet_runs:
                    print("done")
                
                # Parse the stderr output (perf writes to stderr)
                parsed = self._parse_perf_output(result.stderr, syscalls, duration)
                if parsed:
                    results.append(parsed)
                else:
                    print("Warning: Failed to parse perf output for this run")
                    
            except subprocess.CalledProcessError as e:
                print(f"\nError running perf: {e}")
                if runs == 1:
                    return False
            except FileNotFoundError:
                print("Error: 'perf' command not found. Please install the perf utility.")
                return False
        
        if quiet_runs:
            print()  # Add newline after dots
        
        if results:
            self._display_perf_results(results, basename, duration, runs, syscalls)
            return True
        else:
            print("No successful perf runs completed")
            return False
    
    def perf_all(self, duration=None, runs=1, syscalls=False):
        """Run performance analysis on all C files in the current directory."""
        import glob
        
        # Find all .c files in the current directory
        c_files = glob.glob("*.c")
        if not c_files:
            print("No .c files found in the current directory")
            return False
        
        # Filter out main.h if it exists as a .c file
        c_files = [f for f in c_files if not f.startswith("main")]
        c_files.sort()
        
        if not c_files:
            print("No implementation .c files found (excluding main.c)")
            return False
        
        print(f"Running performance tests on {len(c_files)} files: {', '.join(c_files)}")
        print()
        
        success_count = 0
        for filename in c_files:
            print(f"{'='*60}")
            print(f"Testing {filename}")
            print(f"{'='*60}")
            
            if self.perf(filename, duration, runs, syscalls, quiet_runs=True):
                success_count += 1
            else:
                print(f"Failed to run perf test for {filename}")
        
        print(f"\nCompleted perf tests: {success_count}/{len(c_files)} successful")
        return success_count > 0
    
    def _parse_perf_output(self, output, syscalls=False, expected_duration=None):
        """Parse perf stat output and extract metrics."""
        import re
        
        metrics = {}
        lines = output.split('\n')
        
        for line in lines:
            if syscalls:
                # Parse raw syscalls line like: "123      raw_syscalls:sys_enter"
                raw_syscall_match = re.match(r'\s*([\d,]+)\s+raw_syscalls:sys_enter', line)
                if raw_syscall_match:
                    value_str = raw_syscall_match.group(1).replace(',', '')
                    try:
                        metrics["total_syscalls"] = int(value_str)
                    except ValueError:
                        continue
                
                # Also parse individual syscall lines like: "123      syscalls:sys_enter_clock_gettime"
                # (in case both are available)
                syscall_match = re.match(r'\s*([\d,]+)\s+syscalls:sys_enter_(\w+)', line)
                if syscall_match:
                    value_str = syscall_match.group(1).replace(',', '')
                    syscall_name = syscall_match.group(2)
                    try:
                        count = int(value_str)
                        if count > 0:  # Only store non-zero syscalls
                            metrics[f"syscall_{syscall_name}"] = count
                    except ValueError:
                        continue
            else:
                # Parse counter lines like: "19,791,669,777      cycles"
                counter_match = re.match(r'\s*([\d,]+)\s+(\w+[-\w]*)', line)
                if counter_match:
                    value_str = counter_match.group(1).replace(',', '')
                    metric = counter_match.group(2)
                    try:
                        metrics[metric] = int(value_str)
                    except ValueError:
                        continue
                
                # Parse instructions per cycle: "instructions # 0.65 insn per cycle"
                ipc_match = re.search(r'instructions\s+#\s+([\d.]+)\s+insn per cycle', line)
                if ipc_match:
                    metrics['insn_per_cycle'] = float(ipc_match.group(1))
                
                # Parse cache miss percentage: "cache-misses # 2.93% of all cache refs"
                cache_miss_pct_match = re.search(r'cache-misses\s+#\s+([\d.]+)%\s+of all cache refs', line)
                if cache_miss_pct_match:
                    metrics['cache_miss_pct'] = float(cache_miss_pct_match.group(1))
                
                # Parse branch miss percentage: "branch-misses # 15.22% of all branches"
                branch_miss_pct_match = re.search(r'branch-misses\s+#\s+([\d.]+)%\s+of all branches', line)
                if branch_miss_pct_match:
                    metrics['branch_miss_pct'] = float(branch_miss_pct_match.group(1))
            
            # Parse time lines (common for both modes)
            time_match = re.search(r'(\d+\.\d+)\s+seconds\s+time\s+elapsed', line)
            if time_match:
                metrics['time_elapsed'] = float(time_match.group(1))
            
            user_match = re.search(r'(\d+\.\d+)\s+seconds\s+user', line)
            if user_match:
                metrics['user_time'] = float(user_match.group(1))
                
            sys_match = re.search(r'(\d+\.\d+)\s+seconds\s+sys', line)
            if sys_match:
                metrics['sys_time'] = float(sys_match.group(1))
        
        # Calculate system time percentage for non-syscall mode
        if not syscalls and 'user_time' in metrics and 'sys_time' in metrics:
            total_cpu_time = metrics['user_time'] + metrics['sys_time']
            if total_cpu_time > 0:
                metrics['sys_time_pct'] = (metrics['sys_time'] / total_cpu_time) * 100
        
        # Calculate time accuracy by comparing elapsed time with expected duration
        if expected_duration is not None and 'time_elapsed' in metrics:
            actual_time = metrics['time_elapsed']
            accuracy_error = abs(actual_time - expected_duration) / expected_duration * 100
            metrics['time_accuracy_pct'] = 100.0 - accuracy_error
        
        return metrics if metrics else None
    
    def _display_perf_results(self, results, basename, duration, runs, syscalls=False):
        """Display perf results in a formatted table."""
        import statistics
        
        if not results:
            return
            
        mode_desc = "Syscalls" if syscalls else "Performance"
        print(f"\n {mode_desc} Results for {basename} ({runs} run{'s' if runs > 1 else ''}):")
        print("=" * 80)
        
        if syscalls:
            # For syscalls, dynamically find all syscall metrics and filter out zeros
            all_syscalls = {}
            for result in results:
                for key, value in result.items():
                    if key.startswith('syscall_') and value > 0:
                        if key not in all_syscalls:
                            all_syscalls[key] = []
                        all_syscalls[key].append(value)
            
            metrics_info = []
            # Add total syscalls count first if available
            if any('total_syscalls' in result for result in results):
                metrics_info.append(('total_syscalls', 'Total Syscalls'))
            
            # Sort syscalls by average count (highest first)
            syscall_averages = []
            for syscall, values in all_syscalls.items():
                avg_count = sum(values) / len(values)
                syscall_averages.append((syscall, avg_count))
            
            # Sort by average count in descending order
            syscall_averages.sort(key=lambda x: x[1], reverse=True)
            
            # Add individual syscalls ordered by count
            for syscall, _ in syscall_averages:
                display_name = syscall.replace('syscall_', '').replace('_', ' ').title()
                metrics_info.append((syscall, display_name))
            
            # Add timing metrics
            metrics_info.extend([
                ('time_elapsed', 'Time Elapsed (s)'),
                ('time_accuracy_pct', 'Time Accuracy %'),
                ('user_time', 'User Time (s)'),
                ('sys_time', 'Sys Time (s)')
            ])
        else:
            # Define metrics to display for performance counters
            metrics_info = [
                ('cycles', 'Cycles'),
                ('instructions', 'Instructions'),
                ('insn_per_cycle', 'Insn/Cycle'),
                ('cache-references', 'Cache Refs'),
                ('cache-misses', 'Cache Misses'),
                ('cache_miss_pct', 'Cache Miss %'),
                ('branches', 'Branches'),
                ('branch-instructions', 'Branch Instr'),
                ('branch-misses', 'Branch Misses'),
                ('branch_miss_pct', 'Branch Miss %'),
                ('time_elapsed', 'Time Elapsed (s)'),
                ('time_accuracy_pct', 'Time Accuracy %'),
                ('user_time', 'User Time (s)'),
                ('sys_time', 'Sys Time (s)'),
                ('sys_time_pct', 'Sys Time %')
            ]
        
        # Print header
        if runs > 1:
            print(f"{'Metric':<16} {'Mean':>15} {'Std Dev (%)':>15} {'Min':>15} {'Max':>15}")
            print("-" * 80)
        else:
            print(f"{'Metric':<16} {'Value':>15}")
            print("-" * 35)
        
        # Calculate and display statistics for each metric
        for metric_key, metric_name in metrics_info:
            values = [r[metric_key] for r in results if metric_key in r]
            if not values:
                continue
                
            if runs > 1 and len(values) > 1:
                mean_val = statistics.mean(values)
                std_dev = statistics.stdev(values) if len(values) > 1 else 0
                std_dev_pct = (std_dev / mean_val * 100) if mean_val != 0 else 0
                min_val = min(values)
                max_val = max(values)
                
                if metric_key.endswith('_time') or metric_key == 'time_elapsed':
                    print(f"{metric_name:<16} {mean_val:>15.6f} {std_dev_pct:>14.2f}% {min_val:>15.6f} {max_val:>15.6f}")
                elif metric_key.endswith('_pct') or metric_key == 'insn_per_cycle':
                    print(f"{metric_name:<16} {mean_val:>15.3f} {std_dev_pct:>14.2f}% {min_val:>15.3f} {max_val:>15.3f}")
                else:
                    print(f"{metric_name:<16} {mean_val:>15,.0f} {std_dev_pct:>14.2f}% {min_val:>15,} {max_val:>15,}")
            else:
                val = values[0]
                if metric_key.endswith('_time') or metric_key == 'time_elapsed':
                    print(f"{metric_name:<16} {val:>15.6f}")
                elif metric_key.endswith('_pct') or metric_key == 'insn_per_cycle':
                    print(f"{metric_name:<16} {val:>15.3f}")
                else:
                    print(f"{metric_name:<16} {val:>15,}")
        
        print()


def main():
    """Parse arguments and dispatch commands."""
    parser = argparse.ArgumentParser(description="Manage waste-cpu experiments")
    parser.add_argument("command", choices=["compile", "code", "perf", "perf-all"],
                        help="Command to execute")
    parser.add_argument("filename", nargs='?', help="C file to work with (with or without .c extension, not needed for perf-all)")
    parser.add_argument("-O", "--optimize", type=int, default=3,
                        help="Optimization level (0-3, default: 3)")
    parser.add_argument("-d", "--duration", type=int,
                        help="Duration in seconds for perf tests (default: 10)")
    parser.add_argument("-r", "--runs", type=int, default=1,
                        help="Number of times to run perf tests (default: 1)")
    parser.add_argument("--syscalls", action="store_true",
                        help="Count system calls instead of performance counters (requires root)")
    parser.add_argument("--add-main", action="store_true",
                        help="Include main function in code/godbolt output (default: only includes and wait function)")
    
    args = parser.parse_args()
    
    manager = WasteCpuManager()
    manager.opt_level = args.optimize
    if args.duration:
        manager.perf_duration = args.duration
    
    if args.command == "perf-all":
        manager.perf_all(args.duration, args.runs, args.syscalls)
    elif args.command in ["compile", "code", "perf"]:
        if not args.filename:
            print(f"Error: filename is required for {args.command} command")
            return
        
        if args.command == "compile":
            manager.compile(args.filename)
        elif args.command == "code":
            manager.show_code(args.filename, include_main=args.add_main)
        elif args.command == "perf":
            manager.perf(args.filename, args.duration, args.runs, args.syscalls, quiet_runs=True)


if __name__ == "__main__":
    main()
