class Process:
    def __init__(self, pid, burst, arrival, priority):
        self.pid = pid
        self.burst = burst
        self.arrival = arrival
        self.priority = priority
        self.remaining = burst


# ---------------- ALGORITHMS ----------------
def fcfs(processes):
    processes = sorted(processes, key=lambda x: x.arrival)
    time = 0
    results = []

    for p in processes:
        start = max(time, p.arrival)
        finish = start + p.burst

        results.append({
            "pid": p.pid,
            "start": start,
            "finish": finish,
            "waiting": start - p.arrival,
            "turnaround": finish - p.arrival,
            "burst": p.burst
        })

        time = finish

    return results


def sjf(processes):
    processes = sorted(processes, key=lambda x: x.arrival)
    time = 0
    completed = []
    ready = []
    i = 0

    while len(completed) < len(processes):
        while i < len(processes) and processes[i].arrival <= time:
            ready.append(processes[i])
            i += 1

        if ready:
            ready.sort(key=lambda x: x.burst)
            p = ready.pop(0)

            start = time
            finish = start + p.burst

            completed.append({
                "pid": p.pid,
                "start": start,
                "finish": finish,
                "waiting": start - p.arrival,
                "turnaround": finish - p.arrival,
                "burst": p.burst
            })

            time = finish
        else:
            time += 1

    return completed


def priority_sched(processes):
    processes = sorted(processes, key=lambda x: x.arrival)
    time = 0
    completed = []
    ready = []
    i = 0

    while len(completed) < len(processes):
        while i < len(processes) and processes[i].arrival <= time:
            ready.append(processes[i])
            i += 1

        if ready:
            ready.sort(key=lambda x: x.priority)
            p = ready.pop(0)

            start = time
            finish = start + p.burst

            completed.append({
                "pid": p.pid,
                "start": start,
                "finish": finish,
                "waiting": start - p.arrival,
                "turnaround": finish - p.arrival,
                "burst": p.burst
            })

            time = finish
        else:
            time += 1

    return completed


def round_robin(processes, quantum=2):
    queue = []
    time = 0
    i = 0
    processes = sorted(processes, key=lambda x: x.arrival)
    results = {}

    while i < len(processes) or queue:
        while i < len(processes) and processes[i].arrival <= time:
            queue.append(processes[i])
            i += 1

        if queue:
            p = queue.pop(0)

            if p.pid not in results:
                results[p.pid] = {"start": time}

            run_time = min(quantum, p.remaining)
            p.remaining -= run_time
            time += run_time

            while i < len(processes) and processes[i].arrival <= time:
                queue.append(processes[i])
                i += 1

            if p.remaining > 0:
                queue.append(p)
            else:
                results[p.pid]["finish"] = time
                results[p.pid]["waiting"] = time - p.arrival - p.burst
                results[p.pid]["turnaround"] = time - p.arrival
                results[p.pid]["burst"] = p.burst
        else:
            time += 1

    return [{"pid": k, **v} for k, v in results.items()]


def srtf(processes):
    time = 0
    completed = 0
    n = len(processes)
    results = {}

    while completed < n:
        available = [p for p in processes if p.arrival <= time and p.remaining > 0]

        if available:
            p = min(available, key=lambda x: x.remaining)

            if p.pid not in results:
                results[p.pid] = {"start": time}

            p.remaining -= 1
            time += 1

            if p.remaining == 0:
                completed += 1
                results[p.pid]["finish"] = time
                results[p.pid]["waiting"] = time - p.arrival - p.burst
                results[p.pid]["turnaround"] = time - p.arrival
                results[p.pid]["burst"] = p.burst
        else:
            time += 1

    return [{"pid": k, **v} for k, v in results.items()]


def hrrn(processes):
    processes = sorted(processes, key=lambda x: x.arrival)
    time = 0
    completed = []
    ready = []
    i = 0

    while len(completed) < len(processes):
        while i < len(processes) and processes[i].arrival <= time:
            ready.append(processes[i])
            i += 1

        if ready:
            for p in ready:
                waiting = time - p.arrival
                p.response_ratio = (waiting + p.burst) / p.burst

            ready.sort(key=lambda x: x.response_ratio, reverse=True)
            p = ready.pop(0)

            start = time
            finish = start + p.burst

            completed.append({
                "pid": p.pid,
                "start": start,
                "finish": finish,
                "waiting": start - p.arrival,
                "turnaround": finish - p.arrival,
                "burst": p.burst
            })

            time = finish
        else:
            time += 1

    return completed


# ---------------- METRICS ----------------
def calculate_metrics(results):
    n = len(results)
    avg_wait = sum(r["waiting"] for r in results) / n
    avg_turn = sum(r["turnaround"] for r in results) / n

    total_burst = sum(r["burst"] for r in results)
    total_time = max(r["finish"] for r in results)

    cpu_util = (total_burst / total_time) * 100
    throughput = n / total_time

    return avg_wait, avg_turn, cpu_util, throughput


# ---------------- DATASETS ----------------
def generate_medium_dataset():
    return [Process(f"P{i+1}", (i % 10) + 1, i % 5, (i % 5) + 1) for i in range(20)]


def generate_large_dataset():
    return [Process(f"P{i+1}", (i % 20) + 1, i % 10, (i % 10) + 1) for i in range(100)]


# ---------------- UI ----------------
def get_user_processes():
    processes = []
    n = int(input("Enter number of processes: "))

    for i in range(n):
        pid = f"P{i+1}"
        burst = int(input(f"{pid} Burst Time: "))
        arrival = int(input(f"{pid} Arrival Time: "))
        priority = int(input(f"{pid} Priority: "))
        processes.append(Process(pid, burst, arrival, priority))

    return processes


def menu():
    print("\nSelect Option:")
    print("1. FCFS")
    print("2. SJF")
    print("3. Priority")
    print("4. Round Robin")
    print("5. SRTF")
    print("6. HRRN")
    print("7. Run All Algorithms")
    print("8. Use Medium Dataset")
    print("9. Use Large Dataset")

    return input("Enter choice: ")


# ---------------- RUNNER ----------------
def run_all(processes):
    algorithms = {
        "FCFS": fcfs,
        "SJF": sjf,
        "Priority": priority_sched,
        "Round Robin": lambda p: round_robin(p, 2),
        "SRTF": srtf,
        "HRRN": hrrn
    }

    print("\n" + "="*70)
    print(f"{'Algorithm':<15} {'AvgWait':<10} {'AvgTurn':<10} {'CPU %':<10} {'Throughput':<10}")
    print("="*70)

    for name, func in algorithms.items():
        proc_copy = [Process(p.pid, p.burst, p.arrival, p.priority) for p in processes]
        results = func(proc_copy)
        avg_w, avg_t, cpu, thr = calculate_metrics(results)

        print(f"{name:<15} {avg_w:<10.2f} {avg_t:<10.2f} {cpu:<10.2f} {thr:<10.2f}")

    print("="*70)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    choice = menu()

    if choice == "8":
        processes = generate_medium_dataset()
    elif choice == "9":
        processes = generate_large_dataset()
    else:
        processes = get_user_processes()

    if choice == "1":
        results = fcfs(processes)
    elif choice == "2":
        results = sjf(processes)
    elif choice == "3":
        results = priority_sched(processes)
    elif choice == "4":
        results = round_robin(processes, 2)
    elif choice == "5":
        results = srtf(processes)
    elif choice == "6":
        results = hrrn(processes)
    else:
        run_all(processes)
        exit()

    avg_w, avg_t, cpu, thr = calculate_metrics(results)

    print("\nResults:")
    print(f"{'PID':<5} {'Start':<8} {'Finish':<8} {'Wait':<8} {'Turn':<8}")
    print("-"*45)

    for r in results:
        print(f"{r['pid']:<5} {r['start']:<8} {r['finish']:<8} {r['waiting']:<8} {r['turnaround']:<8}")

    print(f"\nAvg Waiting: {avg_w:.2f}")
    print(f"Avg Turnaround: {avg_t:.2f}")
    print(f"CPU Util: {cpu:.2f}%")
    print(f"Throughput: {thr:.2f}")
