# nfp 2임!

import numpy as np
from netCDF4 import Dataset
import os
import math
from matplotlib import animation
from matplotlib.animation import PillowWriter
import matplotlib.pyplot as plt
import csv

datnum=442   # make sure dat file name is formatted as 'dat1.dat', 'dat2.dat', ...
cutter=40
mode=9
csv_name='gc_grid.csv'
headerrow=10

nc_filename= 'wout_pwO_nfp2_A6.nc'
nc_folder=os.path.join(os.path.dirname(__file__), 'nc')
# 0: 3D plot, 
# 1: 2d plot  
# 2: animation(with constant timestep)
# 3: animation(with constant playing time) 
# 4: zeta - s plot 
# 5: time - zeta plot 
# 6: time - flux plot  
# 7:(mod2pi)zeta-s plot 
# 8:(mod)t-zeta plot
# 9: time - zeta and time-flux plot
def load_meta_from_csv(csv_path):
    """
    returns: dict like meta['dat5.dat'] = {'v_perp':..., 'v_para':..., 'dt':..., ...}
    """
    meta = {}
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            out = row["output"].strip()
            # 숫자형 변환(필요한 것만)
            for k in ["v_perp","v_para","dt","steps","compress","mass","x1","x2","x3"]:
                if k in row and row[k] != "":
                    row[k] = float(row[k])
            meta[out] = row
    return meta
def title_from_csv(meta_row, idx):
    vp = meta_row["v_perp"]
    va = meta_row["v_para"]
    dt = meta_row["dt"]
    return f"idx={idx} | v_perp={vp:.0f}, v_para={va:.0f} | dt={dt:.1e}"
def title_format(idx):
    csv_path = os.path.join(os.path.dirname(__file__), csv_name)
    meta = load_meta_from_csv(csv_path)
    dat_filename = f'dat{idx}.dat'
    if dat_filename in meta:
        return title_from_csv(meta[dat_filename], idx)
    else:
        return f'idx={idx} | No metadata found'
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
    return x2,y2,z2, Zeta
def datagetter(file_path2):
    data = np.loadtxt(file_path2, skiprows=headerrow)

    R2 = data[::cutter, 1]
    Z2 = data[::cutter, 2]
    Zeta = data[::cutter, 3]  # Zeta = 2*phi
    # x2, y2, z2로 변환
    x2 = R2 * np.cos(Zeta / 2)
    y2 = R2 * np.sin(Zeta / 2)
    z2 = Z2
    return x2,y2,z2, Zeta
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





# plt.plot(x2,y2)
# plt.plot(X3,Y3, 'r', lw=1, color='tab:orange')

if mode==0:

    for idx in range(1, datnum):
        ax = fig.add_subplot(2, 5, idx, projection='3d') #, projection='3d')

        # 파일 경로 및 데이터 로드
        file_path_tmp = os.path.join(os.path.dirname(__file__), f'dat{idx}.dat')
        xt, yt, zt, zetat = datagetter(file_path_tmp)

        # 각 데이터 플롯
        ax.plot(xt, yt, zt, color='tab:blue', linewidth=0.8)
        ax.plot(X3, Y3, Z3, alpha=0.3, color='tab:red')

        # 라벨 설정
        ax.set_title(title_format(idx), fontsize=9)
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
#        ax.set_zlim(-1.5, 1.5)
        # ax.set_xticks([])
        # ax.set_yticks([])
#        ax.set_zticks([])

        # 축 라벨은 첫 번째 subplot에만 표시 (깔끔하게)
        if idx == datnum:
            ax.set_xlabel('X (m)')
            ax.set_ylabel('Y (m)')
    fig.tight_layout()
    fig.savefig(os.path.join(os.path.dirname(__file__), 'gc_all_3d.png'), dpi=150)
    plt.close(fig)
#            ax.set_zlabel('Z (m)')


elif mode==1:

    for idx in range(1, datnum):
        print(f'Plotting idx={idx}')
        ax = fig.add_subplot(2, 5, idx) #, projection='3d')

        # 파일 경로 및 데이터 로드
        file_path_tmp = os.path.join(os.path.dirname(__file__), f'dat{idx}.dat')
        xt, yt, zt, zetat = datagetter(file_path_tmp)

        # 각 데이터 플롯
        ax.plot(xt, yt, color='tab:blue', linewidth=0.8)
        ax.plot(X3, Y3, alpha=0.3, color='tab:red')

        # 라벨 설정
        ax.set_title(f'{(4.5+0.5*idx):.2f}e4, 5.0e5', fontsize=9)
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
 #       ax.set_zlim(-0.4, 0.4)
        # ax.set_xticks([])
        # ax.set_yticks([])
#        ax.set_zticks([])

        # 축 라벨은 첫 번째 subplot에만 표시 (깔끔하게)
        if idx == datnum:
            ax.set_xlabel('X (m)')
            ax.set_ylabel('Y (m)')
#            ax.set_zlabel('Z (m)')

    fig.tight_layout()
    fig.savefig(os.path.join(os.path.dirname(__file__), 'gc_all_2d.png'), dpi=150)
    plt.close(fig)

elif mode==2:
    for idx in range(1, datnum):
        print(f'Creating animation for idx={idx}')

        # 파일 경로 및 데이터 로드
        file_path_tmp = os.path.join(os.path.dirname(__file__), f'dat{idx}.dat')
        time,xt, yt, zt, zetat,_ = datagetter_ful(file_path_tmp)


        xt = np.asarray(xt)
        yt = np.asarray(yt)
        zt = np.asarray(zt)

        # prepare figure for this idx
        fig_anim = plt.figure(figsize=(10,5))
        ax3d = fig_anim.add_subplot(121, projection='3d')
        ax2d = fig_anim.add_subplot(122)

        ax3d.set_title(title_format(idx), fontsize=9)

        # optional static surface/shape in background
        ax3d.plot(X3, Y3, Z3, alpha=0.3, color='tab:red', linewidth=0.6)
        ax2d.plot(X3, Y3, alpha=0.3, color='tab:red', linewidth=0.6)

        ax3d.plot(X6, Y6, Z6, alpha=0.3, color='tab:green', linewidth=0.6)
        ax2d.plot(X6, Y6, alpha=0.3, color='tab:green', linewidth=0.6)     # INITIAL FLUX BOUNDARY

        # dynamic lines
        line3d, = ax3d.plot([], [], [], color='tab:blue', lw=1)
        line2d, = ax2d.plot([], [], color='tab:blue', lw=1)

        ax3d.set_xlim(-1.5, 1.5)
        ax3d.set_ylim(-1.5, 1.5)
        #ax3d.set_zlim(zmin - 0.1 * abs(zmin if zmin != 0 else 1), zmax + 0.1 * abs(zmax if zmax != 0 else 1))
        ax3d.set_zlim(-zmax,zmax)
        ax2d.set_xlim(-1.5, 1.5)
        ax2d.set_ylim(-1.5, 1.5)
        ax2d.set_aspect('equal', 'box')

        n_points = len(xt)
        step =1000
        frames = max(1, math.ceil(n_points / step))

        def init():
            line3d.set_data([], [])
            line3d.set_3d_properties([])
            line2d.set_data([], [])
            return (line3d, line2d)

        def update(frame):
            end = min((frame + 1) * step, n_points)
            # 3D line
            ax2d.set_title(f'Time: {time[end-1]:.2e}')
            line3d.set_data(xt[:end], yt[:end])
            line3d.set_3d_properties(zt[:end])
            # 2D projection
            line2d.set_data(xt[:end], yt[:end])
            return (line3d, line2d)
        # ax3d.view_init(elev=30, azim=-120) # default=30,-60
        anim = animation.FuncAnimation(fig_anim, update, init_func=init,
                           frames=frames, interval=20, blit=False)

        out_path = os.path.join(os.path.dirname(__file__), f'{idx}_t.gif')
        writer = PillowWriter(fps=10)
        anim.save(out_path, writer=writer)
        plt.close(fig_anim)

elif mode==3:
    for idx in range(1, datnum):
        print(f'Creating animation for idx={idx}')

        # 파일 경로 및 데이터 로드
        file_path_tmp = os.path.join(os.path.dirname(__file__), f'dat{idx}.dat')
        time,xt, yt, zt, zetat,_ = datagetter_ful(file_path_tmp)


        xt = np.asarray(xt)
        yt = np.asarray(yt)
        zt = np.asarray(zt)

        # prepare figure for this idx
        fig_anim = plt.figure(figsize=(10,5))
        ax3d = fig_anim.add_subplot(121, projection='3d')
        ax2d = fig_anim.add_subplot(122)

        ax3d.set_title(title_format(idx), fontsize=9)

        # optional static surface/shape in background
        ax3d.plot(X3, Y3, Z3, alpha=0.3, color='tab:red', linewidth=0.6)
        ax2d.plot(X3, Y3, alpha=0.3, color='tab:red', linewidth=0.6)

        ax3d.plot(X6, Y6, Z6, alpha=0.3, color='tab:green', linewidth=0.6)
        ax2d.plot(X6, Y6, alpha=0.3, color='tab:green', linewidth=0.6)     # INITIAL FLUX BOUNDARY

        # dynamic lines
        line3d, = ax3d.plot([], [], [], color='tab:blue', lw=1)
        line2d, = ax2d.plot([], [], color='tab:blue', lw=1)

        ax3d.set_xlim(-1.5, 1.5)
        ax3d.set_ylim(-1.5, 1.5)
        #ax3d.set_zlim(zmin - 0.1 * abs(zmin if zmin != 0 else 1), zmax + 0.1 * abs(zmax if zmax != 0 else 1))
        ax3d.set_zlim(-zmax,zmax)
        ax2d.set_xlim(-1.5, 1.5)
        ax2d.set_ylim(-1.5, 1.5)
        ax2d.set_aspect('equal', 'box')

        n_points = len(xt)
        step = max(1, n_points // 100)  # Adjust step to have around 100 frames
        frames = max(1, math.ceil(n_points / step))

        def init():
            line3d.set_data([], [])
            line3d.set_3d_properties([])
            line2d.set_data([], [])
            return (line3d, line2d)

        def update(frame):
            end = min((frame + 1) * step, n_points)
            # 3D line
            ax2d.set_title(f'Time: {time[end-1]:.2e}')
            line3d.set_data(xt[:end], yt[:end])
            line3d.set_3d_properties(zt[:end])
            # 2D projection
            line2d.set_data(xt[:end], yt[:end])
            return (line3d, line2d)
        # ax3d.view_init(elev=30, azim=-120)

        anim = animation.FuncAnimation(fig_anim, update, init_func=init,
                           frames=frames, interval=20, blit=False)

        out_path = os.path.join(os.path.dirname(__file__), f'{idx}.gif')
        writer = PillowWriter(fps=10)
        anim.save(out_path, writer=writer)
        plt.close(fig_anim)

elif mode==4:
    #zeta - s plot
    for idx in range(1, datnum):
        # 파일 경로 및 데이터 로드
        file_path_tmp = os.path.join(os.path.dirname(__file__), f'dat{idx}.dat')
        time2, xt, yt, zt, zetat, fl2 = datagetter_ful(file_path_tmp)

        # 각 idx 별로 별도 figure 생성하여 저장
        fig_i = plt.figure(figsize=(5,4))
        ax_i = fig_i.add_subplot(1, 1, 1)
        ax_i.plot(zetat, fl2, color='tab:blue', linewidth=0.8)

        ax_i.set_title(title_format(idx), fontsize=9)
        ax_i.set_xlabel('Zeta (rad)')
        ax_i.set_ylabel('Flux')

        out_path = os.path.join(os.path.dirname(__file__), f'zeta_flux_{idx}.png')
        fig_i.tight_layout()
        fig_i.savefig(out_path, dpi=150)
        plt.close(fig_i)
elif mode==5:
    for idx in range(1, datnum):
        # 파일 경로 및 데이터 로드
        file_path_tmp = os.path.join(os.path.dirname(__file__), f'dat{idx}.dat')
        time2, xt, yt, zt, zetat, fl2 = datagetter_ful(file_path_tmp)

        # 각 idx 별로 별도 figure 생성하여 저장
        fig_i = plt.figure(figsize=(5,4))
        ax_i = fig_i.add_subplot(1, 1, 1)
        ax_i.plot(time2,zetat,color='tab:blue', linewidth=0.8)

        ax_i.set_title(title_format(idx), fontsize=9)
        ax_i.set_xlabel('Time')
        ax_i.set_ylabel('Zeta (rad)')
        out_path = os.path.join(os.path.dirname(__file__), f'zeta_{idx}.png')
        fig_i.tight_layout()
        fig_i.savefig(out_path, dpi=150)
        plt.close(fig_i)
elif mode==6:
    for idx in range(1, datnum):
        # 파일 경로 및 데이터 로드
        file_path_tmp = os.path.join(os.path.dirname(__file__), f'dat{idx}.dat')
        time2, xt, yt, zt, zetat, fl2 = datagetter_ful(file_path_tmp)

        # 각 idx 별로 별도 figure 생성하여 저장
        fig_i = plt.figure(figsize=(5,4))
        ax_i = fig_i.add_subplot(1, 1, 1)
        ax_i.plot(time2,fl2,color='tab:blue', linewidth=0.8)

        ax_i.set_title(title_format(idx), fontsize=9)
        ax_i.set_xlabel('Time')
        ax_i.set_ylabel('Flux')
        out_path = os.path.join(os.path.dirname(__file__), f'flux_{idx}.png')
        fig_i.tight_layout()
        fig_i.savefig(out_path, dpi=150)
        plt.close(fig_i)
elif mode==7:
    for idx in range(1, datnum):
        file_path_tmp = os.path.join(os.path.dirname(__file__), f'dat{idx}.dat')
        time2, xt, yt, zt, zetat, fl2 = datagetter_ful(file_path_tmp)
        zetat=np.mod(zetat, 4*np.pi)
            # 각 idx 별로 별도 figure 생성하여 저장
        fig_i = plt.figure(figsize=(5,4))
        ax_i = fig_i.add_subplot(1, 1, 1)
        ax_i.plot(zetat, fl2, color='tab:blue', linewidth=0.8)

        ax_i.set_title(title_format(idx), fontsize=9)
        ax_i.set_xlabel('Zeta (rad)')
        ax_i.set_ylabel('Flux')

        out_path = os.path.join(os.path.dirname(__file__), f'zetamod_flux_{idx}.png')
        fig_i.tight_layout()
        fig_i.savefig(out_path, dpi=150)
        plt.close(fig_i)    
elif mode==8:
    for idx in range(1, datnum):
        # 파일 경로 및 데이터 로드
        file_path_tmp = os.path.join(os.path.dirname(__file__), f'dat{idx}.dat')
        time2, xt, yt, zt, zetat, fl2 = datagetter_ful(file_path_tmp)
        zetat=np.mod(zetat, 4*np.pi)
        # 각 idx 별로 별도 figure 생성하여 저장
        fig_i = plt.figure(figsize=(5,4))
        ax_i = fig_i.add_subplot(1, 1, 1)
        ax_i.plot(time2,zetat,color='tab:blue', linewidth=0.8)

        ax_i.set_title(title_format(idx), fontsize=9)
        ax_i.set_xlabel('Time')
        ax_i.set_ylabel('Zeta (rad)')
        out_path = os.path.join(os.path.dirname(__file__), f'zetamod_time_{idx}.png')
        fig_i.tight_layout()
        fig_i.savefig(out_path, dpi=150)
        plt.close(fig_i)
elif mode==9:
    for idx in range(1, datnum):
        # 파일 경로 및 데이터 로드
        file_path_tmp = os.path.join(os.path.dirname(__file__), f'dat{idx}.dat')
        time2, xt, yt, zt, zetat, fl2 = datagetter_ful(file_path_tmp)

        # 각 idx 별로 별도 figure 생성하여 저장
        fig_i, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 8))

        ax1.plot(time2, zetat, color='tab:blue', linewidth=0.8)
        ax1.set_title('Zeta vs Time', fontsize=9)
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Zeta (rad)')

        ax2.plot(time2, fl2, color='tab:orange', linewidth=0.8)
        ax2.set_title(title_format(idx), fontsize=9)
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Flux')

        fig_i.suptitle(title_format(idx), fontsize=10)

        out_path = os.path.join(os.path.dirname(__file__), f'time_zeta_flux_{idx}.png')
        fig_i.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig_i.savefig(out_path, dpi=150)
        plt.close(fig_i)

else:
    print("Invalid mode selected.")