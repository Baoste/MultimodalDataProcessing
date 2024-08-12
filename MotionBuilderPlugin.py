from pyfbsdk import *
from pyfbsdk_additions import *

import math
import numpy as np

AXIS0 = 0
AXIS1 = 1
AXIS2 = 2

def get_top_from_root(top, root):
    '''
    从top改为root坐标
    '''
    node = FBFindModelByLabelName(top)
    v = np.asmatrix([0, 0, 1]).T
    mat = np.eye(3)
    while node.LongName != root:
        node_parent = node.Parent
        cos = math.cos(node_parent.Rotation[AXIS2]/180*math.pi)
        sin = math.sin(node_parent.Rotation[AXIS2]/180*math.pi)
        l = math.sqrt(node.Translation[AXIS0]**2 + node.Translation[AXIS1]**2)
        mat = np.array([[cos, -sin, l*cos], [sin, cos, l*sin], [0, 0, 1]])@mat
        node = node_parent
    return mat


def get_position_from_hips(top, node_name):
    '''
    获取单个节点相对于top的信息
    角度从自己读取
    长度从子节点读取
    '''
    node = FBFindModelByLabelName(top)
    v = np.asmatrix([0, 0, 1]).T
    mat = np.eye(3)
    node_child = node.Children[0]
    while True:
        cos = math.cos(node.Rotation[AXIS2]/180*math.pi)
        sin = math.sin(node.Rotation[AXIS2]/180*math.pi)
        l = math.sqrt(node_child.Translation[AXIS0]**2 + node_child.Translation[AXIS1]**2)
        mat = mat@np.array([[cos, -sin, l*cos], [sin, cos, l*sin], [0, 0, 1]])
        if node.LongName == node_name:
            break
        node = node.Children[0]
        node_child = node.Children[0]
    return mat@v


def get_all_positions_from_hips(top, node_name_list, const_mat):
    '''
    以根骨为原点，获取list里的节点相对于根骨的世界坐标
    '''
    positions = []
    for node_name in node_name_list:
        positions.append(const_mat@get_position_from_hips(top, node_name))
    return positions


def get_path_to_node(node_name_list, top, target_name):
    '''
    寻找到指定节点的唯一路径，返回途径的节点列表
    '''
    node = FBFindModelByLabelName(target_name)
    while node.LongName != top:
        node_name_list.append(node.LongName)
        node = node.Parent
    node_name_list.append(node.LongName)
    node_name_list.reverse()


def caculate_distance(points0, points1):
    '''
    计算两组点的距离和
    '''
    distance = 0
    assert len(points0) == len(points0)
    for i in range(len(points0)):
        distance += np.linalg.norm(points0[i]-points1[i])
    print('distance: {0}'.format(distance))


def get_rotation(node_name_list):
    '''
    获得list里每个节点的旋转角度，返回弧度制
    '''
    theta = []
    for node_name in node_name_list:
        node = FBFindModelByLabelName(node_name)
        theta.append(node.Rotation[AXIS2]/180*math.pi)
    return theta


def set_rotation(node_name_list, theta):
    '''
    设置list里每个节点的旋转角度，使用弧度制
    '''
    for node_name, t in zip(node_name_list, theta):
        node = FBFindModelByLabelName(node_name)
        if AXIS2 == 2:
            rot = FBVector3d(node.Rotation[0], node.Rotation[1], t/math.pi*180)
        elif AXIS2 == 1:
            rot = FBVector3d(node.Rotation[0], t/math.pi*180, node.Rotation[2])
        elif AXIS2 == 0:
            rot = FBVector3d(t/math.pi*180, node.Rotation[1], node.Rotation[2])
        node.Rotation = rot


def get_length(node_name_list):
    '''
    获得list里每个节点的长度
    '''
    length = []
    for node_name in node_name_list:
        node = FBFindModelByLabelName(node_name)
        node_child = node.Children[0]
        l = math.sqrt(node_child.Translation[AXIS0]**2+node_child.Translation[AXIS1]**2)
        length.append(l)
    return length


def del_matrix(num, index, theta, length, const_mat):
    '''
    对第num个点的第index个变量求偏导
    '''
    del_mat = np.eye(3)
    for i in range(num+1):
        c = math.cos(theta[i])
        s = math.sin(theta[i])
        if i == index:
            tmp = np.array([[-s, -c, -length[i]*s], [c, -s, length[i]*c], [0, 0, 0]])
            del_mat = del_mat@tmp
        else:
            tmp = np.array([[c, -s, length[i]*c], [s, c, length[i]*s], [0, 0, 1]])
            del_mat = del_mat@tmp
    return const_mat@del_mat


def loop(LOOP, name, top, root):
    '''
    迭代
    '''
    # 标准列向量
    v = np.asmatrix([0, 0, 1]).T

    # 初始化
    target_name = 'target:' + name
    target_top = 'target:' + top
    const_mat = get_top_from_root(target_top, 'target:' + root)
    t_node_name_list = []
    get_path_to_node(t_node_name_list, target_top, target_name)
    target_positions = get_all_positions_from_hips(target_top, t_node_name_list, const_mat)
    
    source_name = 'source:' + name
    source_top = 'source:' + top
    const_mat = get_top_from_root(source_top, 'source:' + root)
    node_name_list = []
    get_path_to_node(node_name_list, source_top, source_name)
    length = get_length(node_name_list)
    length = [scale*l for l in length]
    theta = get_rotation(t_node_name_list)
    set_rotation(node_name_list, theta)
    theta = np.array(theta)
    source_positions = get_all_positions_from_hips(source_top, node_name_list, const_mat)
    source_positions = [scale*p for p in source_positions]

    n = len(node_name_list)
    # 迭代
    for loop_time in range(LOOP):
        # 距离求和
        # caculate_distance(source_positions, target_positions)
        # theta偏导矩阵
        mat_p = [[None]*n for i in range(n)]
        for i in range(n):
            for j in range(i+1):
                mat_p[i][j] = del_matrix(i, j, theta, length, const_mat)
        # 偏导矩阵求x,y坐标对theta的偏导
        x_p = [[None]*n for i in range(n)]
        y_p = [[None]*n for i in range(n)]
        for i in range(n):
            for j in range(i+1):
                x_p[i][j] = mat_p[i][j][0]@v
                y_p[i][j] = mat_p[i][j][1]@v  
        # 求distance偏导
        del_theta = []
        for j in range(n):
            delta_D = 0
            for i in range(j, n):
                delta_D += -2*target_positions[i][0]*x_p[i][j]+2*source_positions[i][0]*x_p[i][j]
                delta_D += -2*target_positions[i][1]*y_p[i][j]+2*source_positions[i][1]*y_p[i][j]
            del_theta.append(delta_D[0, 0])
        del_theta = np.array(del_theta)
        # print('del_theta: {0}'.format(del_theta))
        theta = theta - 0.0001*del_theta
        # print('theta: {0}'.format(theta))
        set_rotation(node_name_list, theta)
        source_positions = get_all_positions_from_hips(source_top, node_name_list, const_mat)
        source_positions = [scale*p for p in source_positions]
        length = get_length(node_name_list)
        length = [scale*l for l in length]


def choose_scale():
    '''
    确定缩放大小
    '''
    top_point = FBVector3d()
    obj = FBFindModelByLabelName('target:Skeleton0_HeadEnd')
    obj.GetVector(top_point, FBModelTransformationType.kModelTranslation)
    bottom_point = FBVector3d()
    obj = FBFindModelByLabelName('target:Skeleton0RightToeBase')
    obj.GetVector(bottom_point, FBModelTransformationType.kModelTranslation)
    target_delta_len = (top_point - bottom_point)[1]

    top_point = FBVector3d()
    obj = FBFindModelByLabelName('source:Skeleton0_HeadEnd')
    obj.GetVector(top_point, FBModelTransformationType.kModelTranslation)
    bottom_point = FBVector3d()
    obj = FBFindModelByLabelName('source:Skeleton0RightToeBase')
    obj.GetVector(bottom_point, FBModelTransformationType.kModelTranslation)
    source_delta_len = (top_point - bottom_point)[1]

    scale = target_delta_len / source_delta_len
    return math.pow(scale, 1/11)


if __name__ in ('__main__', 'builtins'):
    # 移动
    root = FBFindModelByLabelName('source:Skeleton0Hips')
    t_root = FBFindModelByLabelName('target:Skeleton0Hips')
    root.Translation = FBVector3d(t_root.Translation)
    # 缩放
    scale = choose_scale()
    scale_vec = FBVector3d(scale, scale, scale)
    root.Scaling = scale_vec
    print(scale)
    # XY
    print("deal with XY-flat")
    loop(1000, 'Skeleton0LeftForeArm', 'Skeleton0LeftShoulder', 'Skeleton0Spine3')
    loop(1000, 'Skeleton0RightForeArm', 'Skeleton0RightShoulder', 'Skeleton0Spine3')
    loop(1000, 'Skeleton0LeftLeg', 'Skeleton0LeftUpLeg', 'Skeleton0LeftUpLeg')
    loop(1000, 'Skeleton0RightLeg', 'Skeleton0RightUpLeg', 'Skeleton0RightUpLeg')
    # YZ
    print("deal with YZ-flat")
    AXIS0 = 1
    AXIS1 = 2
    AXIS2 = 0
    loop(1000, 'Skeleton0LeftForeArm', 'Skeleton0LeftShoulder', 'Skeleton0Spine3')
    loop(1000, 'Skeleton0RightForeArm', 'Skeleton0RightShoulder', 'Skeleton0Spine3')
    loop(1000, 'Skeleton0LeftLeg', 'Skeleton0LeftUpLeg', 'Skeleton0LeftUpLeg')
    loop(1000, 'Skeleton0RightLeg', 'Skeleton0RightUpLeg', 'Skeleton0RightUpLeg')
    # ZX
    print("deal with ZX-flat")
    AXIS0 = 2
    AXIS1 = 0
    AXIS2 = 1
    loop(1000, 'Skeleton0LeftForeArm', 'Skeleton0LeftShoulder', 'Skeleton0Spine3')
    loop(1000, 'Skeleton0RightForeArm', 'Skeleton0RightShoulder', 'Skeleton0Spine3')
    loop(1000, 'Skeleton0LeftLeg', 'Skeleton0LeftUpLeg', 'Skeleton0LeftUpLeg')
    loop(1000, 'Skeleton0RightLeg', 'Skeleton0RightUpLeg', 'Skeleton0RightUpLeg')

    print("DONE")