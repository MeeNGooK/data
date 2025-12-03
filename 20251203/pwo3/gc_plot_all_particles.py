#for particle set


import numpy as np
from netCDF4 import Dataset
import os
import math
from matplotlib import animation
from matplotlib.animation import PillowWriter
import matplotlib.pyplot as plt
datnum=239   # make sure dat file name is formatted as 'dat1.dat', 'dat2.dat', ...
cutter=2
mode=1

headerrow=10

nc_filename= 'wout_pwO_nfp2_A6.nc'
nc_folder='/home/rjrj524/Finished/vmec_gc_tracer/revised_251128/nc'
# 0: 3D plot, 
# 1: 2d plot
# 2: animation(with constant timestep)

def title_format(idx):
    return f'1e3, -{(1.0*idx):.2f}e4'

# Edit above and run

def datagetter_cut(file_path2,cut):
    data = np.loadtxt(file_path2, skiprows=headerrow)
    
    R2 = data[:cut:cutter, 1]
    Z2 = data[:cut:cutter, 2]
    Zeta = data[:cut:cutter, 3]  # Zeta = 2*phi
    # x2, y2, z2로 변환
    x2 = R2 * np.cos(Zeta / 2)
    y2 = R2 * np.sin(Zeta / 2)
    z2 = Z2
    return T2,x2,y2,z2, Zeta
def datagetter(file_path2):
    data = np.loadtxt(file_path2, skiprows=headerrow)
    T2=data[::cutter, 0]
    R2 = data[::cutter, 1]
    Z2 = data[::cutter, 2]
    Zeta = data[::cutter, 3]  # Zeta = 2*phi
    # x2, y2, z2로 변환
    x2 = R2 * np.cos(Zeta / 2)
    y2 = R2 * np.sin(Zeta / 2)
    z2 = Z2
    return T2, x2,y2,z2, Zeta
def datagetter_ful(file_path2):
    data = np.loadtxt(file_path2, skiprows=headerrow)
    time= data[::cutter,0]
    R2 = data[::cutter, 1]
    Z2 = data[::cutter, 2]
    Zeta = data[::cutter, 3]  # Zeta = 2*phi
    fl= data[::cutter,4]  #flux
    # x2, y2, z2로 변환
    x2 = R2 * np.cos(Zeta / 2)
    y2 = R2 * np.sin(Zeta / 2)
    z2 = Z2
    return time,x2,y2,z2, Zeta,fl
file_path = os.path.join(nc_folder, nc_filename)



f = Dataset(file_path, 'r')
#phi, theta 결정. 이걸로 곡면 구성함
ph=np.linspace(0, 2*np.pi, 60)
thet=np.linspace(0, 2*np.pi, 60)
phi, theta= np.meshgrid(ph, thet)
rmnc= f.variables['rmnc'][:].data
zmns= f.variables['zmns'][:].data
xm= f.variables['xm'][:].data
xn= f.variables['xn'][:].data
ns= f.variables['ns'][:].data
zmax=f.variables['zmax_surf'][:].data
sind2=ns-1
sind3=110
mnmax=f.variables['mnmax'][:].data
mnmax_nyq=f.variables['mnmax_nyq'][:].data

R3=np.zeros_like(phi*2)
Z3=np.zeros_like(phi*2)
for i in range(mnmax):
    R3 += rmnc[sind2, i] * np.cos(xm[i]*theta-xn[i]*phi)
    Z3 +=  zmns[sind2, i] * np.sin(xm[i]*theta-xn[i]*phi)

X3= R3 * np.cos(phi)    #flux surface(outer bound)
Y3= R3 * np.sin(phi)
fig = plt.figure()

R6=np.zeros_like(phi*2)
Z6=np.zeros_like(phi*2)
for i in range(mnmax):
    R6 += rmnc[sind3, i] * np.cos(xm[i]*theta-xn[i]*phi)
    Z6 +=  zmns[sind3, i] * np.sin(xm[i]*theta-xn[i]*phi)

X6= R6 * np.cos(phi)
Y6= R6 * np.sin(phi)  # second flux surface(initial)

#추가: B의 세기(Additional: Magnitude of B)

s_b=range(128)
ph_b=np.linspace(0, 2*np.pi, 60)
thet_b=np.linspace(0, 2*np.pi, 60)

if mode==0:

    dat_folder = os.path.dirname(__file__)
    datasets = []
    for i in range(1, datnum + 1):
        fname = f"dat{i}.dat"
        p1 = os.path.join(dat_folder, fname)
        p2 = os.path.join(os.path.dirname(__file__), fname)
        file_path2 = p1 if os.path.exists(p1) else (p2 if os.path.exists(p2) else None)
        if file_path2 is None:
            print(f"Skipping {fname}: not found")
            continue
        try:
           _, x, y, z, zeta = datagetter(file_path2)
        except Exception as e:
            print(f"Error reading {fname}: {e}")
            continue
        
        datasets.append((x, y, z, zeta, fname))

    if not datasets:
        raise FileNotFoundError("No dat files found to plot.")

    # global color scale from all files
    all_zeta = np.hstack([d[3] for d in datasets])
    vmin, vmax = all_zeta.min(), all_zeta.max()

    fig2 = plt.figure(figsize=(10, 8))
    ax2 = fig2.add_subplot(111, projection='3d')

    for x, y, z, zeta, fname in datasets:
        sc = ax2.scatter(x, y, z, c=zeta, cmap='viridis', s=6, vmin=vmin, vmax=vmax, alpha=0.8, label=fname)

    cbar = fig2.colorbar(sc, ax=ax2, pad=0.1)
    cbar.set_label('Zeta')

    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_zlabel('Z')
    ax2.legend(loc='upper right', fontsize='small', markerscale=2)
    ax2.set_title('3D scatter of dat files (colored by Zeta)')

    out_dir = dat_folder
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'dat_all_particles.png')
    fig2.tight_layout()
    fig2.savefig(out_path, dpi=300)
    plt.close(fig2)
    print(f"Saved plot to {out_path}")


elif mode==1:
    dat_folder = os.path.dirname(__file__)
    file_infos = []
    max_rows = 0

    # collect data arrays for each dat file
    for i in range(1, datnum + 1):
        fname = f"dat{i}.dat"
        p1 = os.path.join(dat_folder, fname)
        p2 = os.path.join(os.path.dirname(__file__), fname)
        file_path2 = p1 if os.path.exists(p1) else (p2 if os.path.exists(p2) else None)
        if file_path2 is None:
            print(f"Skipping {fname}: not found")
            continue
        try:
            data = np.loadtxt(file_path2, skiprows=headerrow)
        except Exception as e:
            print(f"Error reading {fname}: {e}")
            continue
            # <-- 여기가 핵심 수정점: data가 1차원(행이 1개)일 때 2차원으로 강제 -->
        if data.ndim == 1:
            # 한 행짜리 파일일 경우 (1, N) 모양으로 바꿔줌
            data = data.reshape(1, -1)
        # 또는: data = np.atleast_2d(data)
        nrows = data.shape[0]
        if nrows == 0:
            continue
        file_infos.append((fname, data))
        if nrows > max_rows:
            max_rows = nrows

    if not file_infos:
        raise FileNotFoundError("No dat files found for animation.")

    nframes = (max_rows + cutter - 1) // cutter  # number of frames (0-based indexing)

    # create side-by-side figure: left = 3D, right = XY plane (2D)
    fig_anim = plt.figure(figsize=(14, 6))
    ax3d = fig_anim.add_subplot(121, projection='3d')
    ax_xy = fig_anim.add_subplot(122)
    cmap = plt.get_cmap('tab10')
    sizes = 40

    # prepare legend handles (one per file) so legend is consistent across frames
    handles_all = []
    labels_all = []
    for i, (fname, _) in enumerate(file_infos):
        col = 'blue'
        handles_all.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=col, markersize=1))
        labels_all.append(fname)

    def update(frame):
        ax3d.cla()
        ax_xy.cla()

        # fix axes limits for every frame
        ax3d.set_xlim(-1.5, 1.5)
        ax3d.set_ylim(-1.5, 1.5)
        ax3d.set_zlim(-0.8, 0.8)
        ax_xy.set_xlim(-1.5, 1.5)
        ax_xy.set_ylim(-1.5, 1.5)
        ax_xy.set_aspect('equal', 'box')
        ax3d.scatter(X3, Y3, Z3, color='lightgray', alpha=0.5, s=3)
        ax_xy.scatter(X3, Y3, color='lightgray', alpha=0.5, s=3)
        xs_all, ys_all, zs_all, cs_all = [], [], [], []
        for idx, (fname, data) in enumerate(file_infos):
            row_idx = frame * cutter
            if row_idx >= data.shape[0]:
                continue
            row = data[row_idx]
            T2=row[0]
            R2 = row[1]
            Z2 = row[2]
            Zeta = row[3]
            x = R2 * np.cos(Zeta / 2)
            y = R2 * np.sin(Zeta / 2)
            z = Z2
            xs_all.append(x)
            ys_all.append(y)
            zs_all.append(z)
            cs_all.append(idx)  # color index per file

        if xs_all:
            sc3 = ax3d.scatter(xs_all, ys_all, zs_all, color='blue', s=10)
            sc2 = ax_xy.scatter(xs_all, ys_all, color='blue', s=10)

            # legend (consistent for all files)

        ax3d.set_xlabel('X')
        # remove per-frame legend if created earlier

        # show initial and current living particle count as figure title
        current_N = len(xs_all)
        fig_anim.suptitle(f'H+  init N={datnum}, current N={current_N}')
        ax3d.set_ylabel('Y')
        ax3d.set_zlabel('Z')
        ax3d.view_init(elev=30, azim=45)

        ax_xy.set_xlabel('X')
        ax_xy.set_ylabel('Y')
        ax_xy.set_title(f'XY projection Frame {frame}')
        ax3d.set_title(f't={5.0e-7*cutter*frame:.5f} s/{nframes*cutter*5.0e-7:.5f} s')

    # ensure initial fixed limits before animation starts
    ax3d.set_xlim(-2, 2)
    ax3d.set_ylim(-2, 2)
    ax3d.set_zlim(-0.8, 0.8)
    ax_xy.set_xlim(-2, 2)

    # Double GIF playback fps by wrapping PillowWriter so later calls (e.g. PillowWriter(fps=5)) use doubled fps
    _OriginalPillowWriter = PillowWriter
    def PillowWriter(fps=5, **kwargs):
        return _OriginalPillowWriter(fps=(fps * 4), **kwargs)
    ax_xy.set_ylim(-2, 2)
    ax_xy.set_aspect('equal', 'box')

    ani = animation.FuncAnimation(fig_anim, update, frames=nframes, interval=200)

    out_path = os.path.join(dat_folder, 'dat_all_particles.gif')
    writer = PillowWriter(fps=5)
    ani.save(out_path, writer=writer)
    plt.close(fig_anim)
    print(f"Saved animation to {out_path}")


elif mode==2:
    dat_folder = os.path.dirname(__file__)
    file_infos = []
    max_rows = 0

    # collect data arrays for each dat file
    for i in range(1, datnum + 1):
        fname = f"dat{i}.dat"
        p1 = os.path.join(dat_folder, fname)
        p2 = os.path.join(os.path.dirname(__file__), fname)
        file_path2 = p1 if os.path.exists(p1) else (p2 if os.path.exists(p2) else None)
        if file_path2 is None:
            print(f"Skipping {fname}: not found")
            continue
        try:
            data = np.loadtxt(file_path2, skiprows=headerrow)
        except Exception as e:
            print(f"Error reading {fname}: {e}")
            continue
            # <-- 여기가 핵심 수정점: data가 1차원(행이 1개)일 때 2차원으로 강제 -->
        if data.ndim == 1:
            # 한 행짜리 파일일 경우 (1, N) 모양으로 바꿔줌
            data = data.reshape(1, -1)
        # 또는: data = np.atleast_2d(data)
        nrows = data.shape[0]
        if nrows == 0:
            continue
        file_infos.append((fname, data))
        if nrows > max_rows:
            max_rows = nrows

    if not file_infos:
        raise FileNotFoundError("No dat files found for animation.")

    nframes = (max_rows + cutter - 1) // cutter  # number of frames (0-based indexing)

    # create side-by-side figure: left = 3D, right = XY plane (2D)
    fig_anim = plt.figure(figsize=(10, 10))
    ax3d = fig_anim.add_subplot(111, projection='3d')
    cmap = plt.get_cmap('tab10')
    sizes = 40

    # prepare legend handles (one per file) so legend is consistent across frames
    handles_all = []
    labels_all = []
    for i, (fname, _) in enumerate(file_infos):
        col = 'blue'
        handles_all.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=col, markersize=1))
        labels_all.append(fname)

    def update(frame):
        ax3d.cla()

        # fix axes limits for every frame
        ax3d.set_xlim(-1.5, 1.5)
        ax3d.set_ylim(-1.5, 1.5)
        ax3d.set_zlim(-0.8, 0.8)

        ax3d.scatter(X3, Y3, Z3, color='lightgray', alpha=0.5, s=1)
        xs_all, ys_all, zs_all, cs_all = [], [], [], []
        for idx, (fname, data) in enumerate(file_infos):
            row_idx = frame * cutter
            if row_idx >= data.shape[0]:
                continue
            row = data[row_idx]
            T2=row[0]
            R2 = row[1]
            Z2 = row[2]
            Zeta = row[3]
            x = R2 * np.cos(Zeta / 2)
            y = R2 * np.sin(Zeta / 2)
            z = Z2
            xs_all.append(x)
            ys_all.append(y)
            zs_all.append(z)
            cs_all.append(idx)  # color index per file

        if xs_all:
            sc3 = ax3d.scatter(xs_all, ys_all, zs_all, color='blue', s=1)

            # legend (consistent for all files)

        ax3d.set_xlabel('X')
        # remove per-frame legend if created earlier

        # show initial and current living particle count as figure title
        current_N = len(xs_all)
        fig_anim.suptitle(f'H+  init N={datnum}, current N={current_N}')
        ax3d.set_ylabel('Y')
        ax3d.set_zlabel('Z')
        ax3d.view_init(elev=30, azim=45)

        ax3d.set_title(f't={5.0e-7*cutter*frame:.5f} s/{nframes*cutter*5.0e-7:.5f} s')

    # ensure initial fixed limits before animation starts
    ax3d.set_xlim(-2, 2)
    ax3d.set_ylim(-2, 2)
    ax3d.set_zlim(-0.8, 0.8)

    # Double GIF playback fps by wrapping PillowWriter so later calls (e.g. PillowWriter(fps=5)) use doubled fps
    _OriginalPillowWriter = PillowWriter
    def PillowWriter(fps=5, **kwargs):
        return _OriginalPillowWriter(fps=(fps * 2), **kwargs)


    ani = animation.FuncAnimation(fig_anim, update, frames=nframes, interval=200)

    out_path = os.path.join(dat_folder, 'dat_all_particles_3.gif')
    writer = PillowWriter(fps=5)
    ani.save(out_path, writer=writer)
    plt.close(fig_anim)
    print(f"Saved animation to {out_path}")