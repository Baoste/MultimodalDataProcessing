from pyfbsdk import *
from pyfbsdk_additions import *

import math
import numpy as np

def get_position_from_origin(namespace, node_name):
    '''
    retrurn Vector3d of position from origin
    '''
    v = np.asmatrix([0, 0, 0, 1]).T
    mat = np.eye(4)
    #print(namespace + ':' + node_name)
    node = FBFindModelByLabelName(namespace + ':' + node_name)
    node_parent = node.Parent
    while node_parent:
        x_r = node_parent.Rotation[0] / 180 * math.pi
        y_r = node_parent.Rotation[1] / 180 * math.pi
        z_r = node_parent.Rotation[2] / 180 * math.pi
        mat_x = np.array([[1, 0, 0, 0], 
                        [0, math.cos(x_r), -math.sin(x_r), 0], 
                        [0, math.sin(x_r), math.cos(x_r), 0],
                        [0, 0, 0, 1]])
        mat_y = np.array([[math.cos(y_r), 0, math.sin(y_r), 0], 
                        [0, 1, 0, 0], 
                        [-math.sin(y_r), 0, math.cos(y_r),0],
                        [0, 0, 0, 1]])
        mat_z = np.array([[math.cos(z_r), -math.sin(z_r), 0, 0], 
                        [math.sin(z_r), math.cos(z_r), 0, 0],
                        [0, 0, 1, 0], 
                        [0, 0, 0, 1]])
        mat_t = np.array([[1, 0, 0, node.Translation[0]], 
                        [0, 1, 0, node.Translation[1]],
                        [0, 0, 1, node.Translation[2]], 
                        [0, 0, 0, 1]])
        mat = np.dot(mat_t, mat)
        mat = np.dot(mat_x, mat)
        mat = np.dot(mat_y, mat)
        mat = np.dot(mat_z, mat)
        node = node_parent
        node_parent = node.Parent
    #print(np.dot(mat, v))
    return np.dot(mat, v)
    

def get_mat_from_origin_to_top(namespace, top_name):
    '''
    retrurn mat from origin to top
    '''
    mat = np.eye(4)
    
    node = FBFindModelByLabelName(namespace + ':' + top_name)
    node_parent = node.Parent
    while node_parent:
        x_r = node_parent.Rotation[0] / 180 * math.pi
        y_r = node_parent.Rotation[1] / 180 * math.pi
        z_r = node_parent.Rotation[2] / 180 * math.pi
        mat_x = np.array([[1, 0, 0, 0], 
                        [0, math.cos(x_r), -math.sin(x_r), 0], 
                        [0, math.sin(x_r), math.cos(x_r), 0],
                        [0, 0, 0, 1]])
        mat_y = np.array([[math.cos(y_r), 0, math.sin(y_r), 0], 
                        [0, 1, 0, 0], 
                        [-math.sin(y_r), 0, math.cos(y_r),0],
                        [0, 0, 0, 1]])
        mat_z = np.array([[math.cos(z_r), -math.sin(z_r), 0, 0], 
                        [math.sin(z_r), math.cos(z_r), 0, 0],
                        [0, 0, 1, 0], 
                        [0, 0, 0, 1]])
        mat_t = np.array([[1, 0, 0, node.Translation[0]], 
                        [0, 1, 0, node.Translation[1]],
                        [0, 0, 1, node.Translation[2]], 
                        [0, 0, 0, 1]])
        mat = np.dot(mat_t, mat)
        mat = np.dot(mat_x, mat)
        mat = np.dot(mat_y, mat)
        mat = np.dot(mat_z, mat)
        node = node_parent
        node_parent = node.Parent

    return mat
    

def get_positions_of_path(node_name_list):
    positions = []
    for node in node_name_list:
        namespace = node.split(':')[0]
        node_name = node.split(':')[1]
        positions.append(get_position_from_origin(namespace, node_name))
    return positions


def get_path(node_name_list, namespace, end, top):
    '''
    get path
    [top->end]
    '''
    node = FBFindModelByLabelName(namespace + ':' + end)
    while node.LongName != namespace + ':' + top:
        node_name_list.append(node.LongName)
        node = node.Parent
    node_name_list.reverse()


def caculate_distance(points0, points1):
    '''
    caculate distance
    '''
    distance = 0
    assert len(points0) == len(points0)
    for i in range(len(points0)):
        distance += np.linalg.norm(points0[i]-points1[i])
    print('distance: {0}'.format(distance))


def get_translation(node_name_list):
    '''
    get translation
    from top(included) to end(not included)
    '''
    trans = []
    for node_name in node_name_list:
        node = FBFindModelByLabelName(node_name)
        trans.append([node.Translation[i] for i in range(3)])
    return trans


def get_rotation(node_name_list):
    '''
    get angle
    from top(included) to end(not included)
    '''
    theta = []
    for node_name in node_name_list:
        node = FBFindModelByLabelName(node_name)
        theta.append([node.Parent.Rotation[i]/180*math.pi for i in range(3)])
    return theta


def set_rotation(node_name_list, theta):
    '''
    set angle
    from top(included) to end(not included)
    '''
    node_parent_list = [FBFindModelByLabelName(i).Parent for i in node_name_list]
    for node, t in zip(node_parent_list, theta):
        rot = FBVector3d(t[0]/math.pi*180, t[1]/math.pi*180, t[2]/math.pi*180)
        node.Rotation = rot


def del_matrix(const_mat, theta, trans, num, index, k):
    '''
    caculate del of num's point's index
    '''
    del_mat = np.eye(4)
    for i in range(num+1):
        mat = np.eye(4)
        x_r = theta[i][0]
        y_r = theta[i][1]
        z_r = theta[i][2]
        t = trans[i]

        mat_x = np.array([[1, 0, 0, 0], 
                        [0, math.cos(x_r), -math.sin(x_r), 0], 
                        [0, math.sin(x_r), math.cos(x_r), 0],
                        [0, 0, 0, 1]])
        mat_y = np.array([[math.cos(y_r), 0, math.sin(y_r), 0], 
                        [0, 1, 0, 0], 
                        [-math.sin(y_r), 0, math.cos(y_r),0],
                        [0, 0, 0, 1]])
        mat_z = np.array([[math.cos(z_r), -math.sin(z_r), 0, 0], 
                        [math.sin(z_r), math.cos(z_r), 0, 0],
                        [0, 0, 1, 0], 
                        [0, 0, 0, 1]])
        mat_t = np.array([[1, 0, 0, t[0]], 
                        [0, 1, 0, t[1]],
                        [0, 0, 1, t[2]], 
                        [0, 0, 0, 1]])
        if i == index:
            if k == 0:
                mat_x = np.array([[0, 0, 0, 0], 
                                [0, -math.sin(x_r), -math.cos(x_r), 0], 
                                [0, math.cos(x_r), -math.sin(x_r), 0],
                                [0, 0, 0, 0]])
            elif k == 1:
                mat_y = np.array([[-math.sin(y_r), 0, math.cos(y_r), 0], 
                                [0, 0, 0, 0], 
                                [-math.cos(y_r), 0, -math.sin(y_r),0],
                                [0, 0, 0, 0]])
            elif k == 2:
                mat_z = np.array([[-math.sin(z_r), -math.cos(z_r), 0, 0], 
                                [math.cos(z_r), -math.sin(z_r), 0, 0],
                                [0, 0, 0, 0], 
                                [0, 0, 0, 0]])

        mat = np.dot(mat_t, mat)
        mat = np.dot(mat_x, mat)
        mat = np.dot(mat_y, mat)
        mat = np.dot(mat_z, mat)
        del_mat = np.dot(del_mat, mat)
    #print(np.dot(const_mat, del_mat))
    return np.dot(const_mat, del_mat)


def loop(LOOP, namespace, name, top):
    '''
    loop
    '''
    # normal vector
    v = np.asmatrix([0, 0, 0, 1]).T

    # init
    target_node_name_list = []
    get_path(target_node_name_list, 'YiFan', name, top)
    target_positions = get_positions_of_path(target_node_name_list)
    
    const_mat = get_mat_from_origin_to_top(namespace, top)

    node_name_list = []
    get_path(node_name_list, namespace, name, top)
    #theta = get_rotation(target_node_name_list)
    theta = get_rotation(node_name_list)
    trans = get_translation(node_name_list)
    set_rotation(node_name_list, theta)
    source_positions = get_positions_of_path(node_name_list)

    n = len(node_name_list)
    # loop
    for loop_time in range(LOOP):
        #print('-----------------')
        #caculate_distance(source_positions, target_positions)
        # del theta
        mat_p = np.array([[[None]*3]*n]*n)
        
        for i in range(n):
            for j in range(i+1):
                for k in range(3):
                    mat_p[i][j][k] = del_matrix(const_mat, theta, trans, i, j, k)

        # del x y z
        x_p = np.array([[[None]*3]*n]*n)
        y_p = np.array([[[None]*3]*n]*n)
        z_p = np.array([[[None]*3]*n]*n)
        for i in range(n):
            for j in range(i+1):
                for k in range(3):
                    x_p[i][j][k] = np.dot(mat_p[i][j][k][0], v)
                    y_p[i][j][k] = np.dot(mat_p[i][j][k][1], v)
                    z_p[i][j][k] = np.dot(mat_p[i][j][k][2], v)            

        # del distance
        del_theta = []
        for j in range(n):
            delta_D = np.zeros(3)
            for i in range(j, n):
                for k in range(3):
                    delta_D[k] += -2*target_positions[i][0]*x_p[i][j][k]+2*source_positions[i][0]*x_p[i][j][k]
                    delta_D[k] += -2*target_positions[i][1]*y_p[i][j][k]+2*source_positions[i][1]*y_p[i][j][k]
                    delta_D[k] += -2*target_positions[i][2]*z_p[i][j][k]+2*source_positions[i][2]*z_p[i][j][k]
            
            del_theta.append(delta_D)
        del_theta = np.array(del_theta)
        #print('del_theta: {0}'.format(del_theta))
        theta = theta - 0.0001*del_theta
        #print('theta: {0}'.format(theta))
        set_rotation(node_name_list, theta)
        source_positions = get_positions_of_path(node_name_list)


if __name__ in ('__main__', '__builtin__'):
    namespace = 'source'

    #print('===============')
    loop(50, namespace, 'Skeleton0RightHand', 'Skeleton0RightShoulder')
    loop(50, namespace, 'Skeleton0LeftHand', 'Skeleton0LeftShoulder')
    loop(50, namespace, 'Skeleton0RightToeBase', 'Skeleton0RightLeg')
    loop(50, namespace, 'Skeleton0LeftToeBase', 'Skeleton0LeftLeg')