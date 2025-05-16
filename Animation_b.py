import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Parameters
real_mu = 1.95  # service rate for Real Timing
b_mu = 3.0     # service rate for Optimized Timing
yellow = 4
dt = 1
steps = 600

# Real green times and cycle
real_green = {'N': 60, 'S': 60, 'E': 42, 'W': 42}
real_cycle = 110

# Optimized green durations
opt_green = {'N': 22.36, 'S': 21.12, 'E': 26.34, 'W': 24.18}
opt_schedule = []
for d in ['N', 'E', 'S', 'W']:
    opt_schedule.append((d, opt_green[d]))
    opt_schedule.append(('Y', yellow))
opt_cycle = sum(duration for _, duration in opt_schedule)

# Arrival rates
lambda_rates = {
    'N': 0.438,
    'E': 0.619,
    'S': 0.382,
    'W': 0.521
}
directions = ['N', 'E', 'S', 'W']

# Queues
real_queues = {d: [] for d in directions}
opt_queues = {d: [] for d in directions}

# Pause flag
paused = [False]

# Setup figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
bars1 = ax1.bar(directions, [0]*4, color='red')
bars2 = ax2.bar(directions, [0]*4, color='red')
ax1.set_title("Real Timing")
ax2.set_title("Optimized Timing")
for ax in [ax1, ax2]:
    ax.set_ylim(0, 100)
    ax.set_ylabel("Queue Length (cars)")

# Add text labels above bars
labels1 = [ax1.text(i, 0, '', ha='center', va='bottom', fontsize=9) for i in range(4)]
labels2 = [ax2.text(i, 0, '', ha='center', va='bottom', fontsize=9) for i in range(4)]

def get_opt_phase(t):
    time_in_cycle = t % opt_cycle
    time_sum = 0
    for phase, duration in opt_schedule:
        if time_sum <= time_in_cycle < time_sum + duration:
            return phase
        time_sum += duration
    return 'Y'

def get_real_phase(t):
    phase = t % real_cycle
    if phase < 60:
        return ['N', 'S']
    elif 60 + 4 <= phase < 60 + 4 + 42:
        return ['E', 'W']
    return []

def on_key(event):
    if event.key == 'a':
        paused[0] = not paused[0]

fig.canvas.mpl_connect('key_press_event', on_key)

def update(t):
    if paused[0]:
        return

    # Current phases
    real_phase = get_real_phase(t)
    opt_phase = get_opt_phase(t)

    # Arrivals
    for d in directions:
        if np.random.rand() < lambda_rates[d]:
            real_queues[d].append(t)
            opt_queues[d].append(t)

    # Departures (real timing with real_mu)
    for d in real_phase:
        served = int(min(real_mu * dt, len(real_queues[d])))
        real_queues[d] = real_queues[d][served:]

    # Departures (optimized timing with b_mu)
    if opt_phase in directions:
        served = int(min(b_mu * dt, len(opt_queues[opt_phase])))
        opt_queues[opt_phase] = opt_queues[opt_phase][served:]

    # Update bars and labels
    for i, d in enumerate(directions):
        # Real
        q_real = len(real_queues[d])
        bars1[i].set_height(q_real)
        bars1[i].set_color('green' if d in real_phase else 'red')
        labels1[i].set_position((i, q_real))
        labels1[i].set_text(str(q_real))

        # Optimized
        q_opt = len(opt_queues[d])
        bars2[i].set_height(q_opt)
        bars2[i].set_color('green' if d == opt_phase else 'red')
        labels2[i].set_position((i, q_opt))
        labels2[i].set_text(str(q_opt))

    fig.suptitle(f'Time = {t}s | Real Phase: {real_phase} | Optimized Phase: {opt_phase}')

ani = FuncAnimation(fig, update, frames=range(0, steps), interval=100)
plt.tight_layout()
plt.show()
