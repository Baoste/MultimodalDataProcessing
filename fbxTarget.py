import numpy as np
import math, random
import matplotlib.pyplot as plt
from matplotlib import animation


def animate(i):
    line.set_xdata(ppx[i])
    line.set_ydata(ppy[i])
    return line,

def init():
    return line,


def del_matrix(index, num, rotate_mat, len):
    del_mat = np.eye(3)
    for i in range(num+1):
        if i == index:
            c = rotate_mat[i][0][0]
            s = rotate_mat[i][1][0]
            tmp = np.array([[-s, -c, -len[i]*s], [c, -s, len[i]*c], [0, 0, 0]])
            del_mat = del_mat@tmp
        else:
            del_mat = del_mat@rotate_mat[i]
    return del_mat

if __name__ == "__main__":
    LOOP = 1000
    # 标准列向量
    v = np.mat([0, 0, 1]).T
    ppx = []
    ppy = []

    angle_t = np.array([0,0.8,0.5,0.6,0.4,0.5])
    # 总点数
    n = len(angle_t)
    # 目标数据的长度
    len_t = np.array([0, 7, 8, 9, 6, 6])
    # 暂时储存三角函数值
    cos_t = np.array([math.cos(x) for x in angle_t])
    sin_t = np.array([math.sin(x) for x in angle_t])
    # 每个点的旋转矩阵
    rotate_mat_t = [np.array([[cos_t[i], -sin_t[i], len_t[i]*cos_t[i]], [sin_t[i], cos_t[i], len_t[i]*sin_t[i]], [0, 0, 1]]) for i in range(n)]
    # 每个点的列向量
    point_t = []
    for i in range(n):
        mat = rotate_mat_t[0]
        for j in range(i):
            mat = mat@rotate_mat_t[j+1]
        point_t.append(mat@v)

    distance = 0
    # 待处理角度
    theta = np.array([0 for x in angle_t])
    # 待处理数据的长度
    t = 0
    len_b = np.array([t, 8, 8, 6, 7, 9])

    for loop_time in range(LOOP):
        # 暂时储存三角函数值
        cos_b = np.array([math.cos(x) for x in theta])
        sin_b = np.array([math.sin(x) for x in theta])
        # 每个点的旋转矩阵
        rotate_mat_b = [np.array([[cos_b[i], -sin_b[i], len_b[i]*cos_b[i]], [sin_b[i], cos_b[i], len_b[i]*sin_b[i]], [0, 0, 1]]) for i in range(n)]

        # 每个点的列向量
        point_b = []
        for i in range(n):
            mat = rotate_mat_b[0]
            for j in range(i):
                mat = mat@rotate_mat_b[j+1]
            point_b.append(mat@v)
        
        # 动画
        pxb = [float(x[0]) for x in point_b]
        pyb = [float(x[1]) for x in point_b]
        ppx.append(pxb)
        ppy.append(pyb)

        # 距离求和
        distance = 0
        for i in range(n):
            distance += np.linalg.norm(point_b[i]-point_t[i])
        print('distance: {0}'.format(distance))

        # theta偏导矩阵
        mat_p = [[None]*n for i in range(n)]
        for i in range(n):
            for j in range(i+1):
                mat_p[i][j] = del_matrix(j, i, rotate_mat_b, len_b)
        # t偏导矩阵
        mat_tp = [None for i in range(n)]
        for i in range(n):
            mat_tp[i] = np.array([[0, 0, cos_b[i]], [0, 0, sin_b[i]], [0, 0, 0]])
            for j in range(i):
                mat_tp[i] = mat_tp[i]@rotate_mat_b[j+1]

        # 偏导矩阵求x,y坐标对theta的偏导
        x_p = [[None]*n for i in range(n)]
        y_p = [[None]*n for i in range(n)]
        for i in range(n):
            for j in range(i+1):
                x_p[i][j] = mat_p[i][j][0]@v
                y_p[i][j] = mat_p[i][j][1]@v
        # 偏导矩阵求x,y坐标对t的偏导
        x_tp = [None for i in range(n)]
        y_tp = [None for i in range(n)]
        for i in range(n):
            x_tp[i] = mat_tp[i][0]@v
            y_tp[i] = mat_tp[i][1]@v

        # 求distance偏导
        del_theta = []
        for j in range(n):
            delta_D = 0
            for i in range(j, n):
                delta_D += -2*point_t[i][0]*x_p[i][j]+2*point_b[i][0]*x_p[i][j]
                delta_D += -2*point_t[i][1]*y_p[i][j]+2*point_b[i][1]*y_p[i][j]
            del_theta.append(delta_D[0, 0])
        del_theta = np.array(del_theta)
        print('del_theta: {0}'.format(del_theta))
        theta = theta - 0.0001*del_theta
        print('theta: {0}'.format(theta))
        del_t = 0
        for i in range(n):
            del_t += -2*point_t[i][0]*x_tp[i]+2*point_b[i][0]*x_tp[i]
            del_t += -2*point_t[i][1]*y_tp[i]+2*point_b[i][1]*y_tp[i]
        print('del_t: {0}'.format(del_t))
        t = t - 0.0001*del_t
        print('t: {0}'.format(t))
        len_b[0] = t


    px = [float(x[0]) for x in point_t]
    py = [float(x[1]) for x in point_t]
    fig, ax = plt.subplots()
    plt.gca().set_aspect(1)
    plt.xlim((-10, 50))
    plt.ylim((-10, 50))
    ax.plot(px, py)
    line, = ax.plot(px, py)
    ani = animation.FuncAnimation(fig=fig,
                              func=animate,
                              frames=LOOP,
                              init_func=init,
                              interval=50,
                              blit=True)
    plt.show()