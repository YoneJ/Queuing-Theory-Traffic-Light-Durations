import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Real and optimized green durations
real_green_NS = 60
real_green_EW = 42
real_cycle_time = real_green_NS + real_green_EW + 8  # 4s yellow per direction

opt_green_NS = 49.24
opt_green_EW = 52.76
opt_cycle_time = opt_green_NS + opt_green_EW + 8

mu = 1.95
lambda_rate_NS = (0.438 + 0.382) / 2
lambda_rate_EW = (0.619 + 0.521) / 2
dt = 1.0
time_steps = 600

# Queues
queue_real_NS = []
queue_real_EW = []
queue_opt_NS = []
queue_opt_EW = []

# State for pausing
paused = [False]  # use a mutable container so we can change it from inside the function

# Setup figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
bars1 = ax1.bar(['N/S', 'E/W'], [0, 0], color=['green', 'red'])
bars2 = ax2.bar(['N/S', 'E/W'], [0, 0], color=['green', 'red'])

# Set limits and titles
for ax in [ax1, ax2]:
    ax.set_ylim(0, 100)
    ax.set_ylabel('Queue Length (cars)')

ax1.set_title('Real Timing')
ax2.set_title('Optimized Timing')

# Initialize labels for queue lengths
labels1 = [ax1.text(i, 0, '', ha='center', va='bottom', fontsize=9) for i in range(2)]
labels2 = [ax2.text(i, 0, '', ha='center', va='bottom', fontsize=9) for i in range(2)]

# Pause/resume toggle on key press
def on_key(event):
    if event.key == 'a':
        paused[0] = not paused[0]

fig.canvas.mpl_connect('key_press_event', on_key)

def update(t):
    if paused[0]:
        return

    global queue_real_NS, queue_real_EW, queue_opt_NS, queue_opt_EW

    # Determine signal phases
    phase_real = t % real_cycle_time
    is_real_NS_green = phase_real < real_green_NS
    is_real_EW_green = real_green_NS + 4 <= phase_real < real_green_NS + 4 + real_green_EW

    phase_opt = t % opt_cycle_time
    is_opt_NS_green = phase_opt < opt_green_NS
    is_opt_EW_green = opt_green_NS + 4 <= phase_opt < opt_green_NS + 4 + opt_green_EW

    # Arrivals
    if np.random.rand() < lambda_rate_NS * dt:
        queue_real_NS.append(t)
        queue_opt_NS.append(t)
    if np.random.rand() < lambda_rate_EW * dt:
        queue_real_EW.append(t)
        queue_opt_EW.append(t)

    # Departures
    if is_real_NS_green:
        queue_real_NS = queue_real_NS[int(min(mu * dt, len(queue_real_NS))):]
    if is_real_EW_green:
        queue_real_EW = queue_real_EW[int(min(mu * dt, len(queue_real_EW))):]
    if is_opt_NS_green:
        queue_opt_NS = queue_opt_NS[int(min(mu * dt, len(queue_opt_NS))):]
    if is_opt_EW_green:
        queue_opt_EW = queue_opt_EW[int(min(mu * dt, len(queue_opt_EW))):]

    # Queue lengths
    q_r_ns = len(queue_real_NS)
    q_r_ew = len(queue_real_EW)
    q_o_ns = len(queue_opt_NS)
    q_o_ew = len(queue_opt_EW)

    # Update bars and colors
    bars1[0].set_height(q_r_ns)
    bars1[0].set_color('green' if is_real_NS_green else 'red')
    bars1[1].set_height(q_r_ew)
    bars1[1].set_color('green' if is_real_EW_green else 'red')

    bars2[0].set_height(q_o_ns)
    bars2[0].set_color('green' if is_opt_NS_green else 'red')
    bars2[1].set_height(q_o_ew)
    bars2[1].set_color('green' if is_opt_EW_green else 'red')

    # Update labels
    labels1[0].set_position((0, q_r_ns))
    labels1[0].set_text(str(q_r_ns))
    labels1[1].set_position((1, q_r_ew))
    labels1[1].set_text(str(q_r_ew))

    labels2[0].set_position((0, q_o_ns))
    labels2[0].set_text(str(q_o_ns))
    labels2[1].set_position((1, q_o_ew))
    labels2[1].set_text(str(q_o_ew))

    fig.suptitle(f'Time = {t}s')

ani = FuncAnimation(fig, update, frames=range(0, time_steps), interval=100)
plt.tight_layout()
plt.show()
