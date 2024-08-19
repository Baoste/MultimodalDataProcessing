import FbxCommon, fbx

def get_animation_data(node, scene):
    # 获取动画堆栈（通常只有一个）
    anim_stack_count = scene.GetSrcObjectCount(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId))
    for i in range(anim_stack_count):
        anim_stack = scene.GetSrcObject(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId), i)
        scene.SetCurrentAnimationStack(anim_stack)
        print(f"Animation stack: {anim_stack.GetName()}")

        # 获取动画层
        anim_layer_count = anim_stack.GetMemberCount()
        for j in range(anim_layer_count):
            anim_layer = anim_stack.GetMember(j)
            print(f"  Animation layer: {anim_layer.GetName()}")

            # 获取动画曲线节点
            anim_curve_node = node.LclTranslation.GetCurveNode(anim_layer)
            if anim_curve_node:
                print(f"    Animation curve node: {anim_curve_node.GetName()}")

                # 获取动画曲线
                anim_curve_x = anim_curve_node.GetCurve(0)
                anim_curve_y = anim_curve_node.GetCurve(1)
                anim_curve_z = anim_curve_node.GetCurve(2)

                # 动画时间
                #global anim_time
                #anim_time = anim_curve_x.KeyGetTime(anim_curve_x.KeyGetCount()-1).GetSecondDouble() - anim_curve_x.KeyGetTime(0).GetSecondDouble()

                if anim_curve_x:
                    print("    X axis animation curve:")
                    for key_index in range(anim_curve_x.KeyGetCount()):
                        key = anim_curve_x.KeyGet(key_index)
                        time = key.GetTime().GetSecondDouble()
                        value = key.GetValue()
                        print(f"      Time: {time}, Value: {value}")

                if anim_curve_y:
                    print("    Y axis animation curve:")
                    for key_index in range(anim_curve_y.KeyGetCount()):
                        key = anim_curve_y.KeyGet(key_index)
                        time = key.GetTime().GetSecondDouble()
                        value = key.GetValue()
                        print(f"      Time: {time}, Value: {value}")

                if anim_curve_z:
                    print("    Z axis animation curve:")
                    for key_index in range(anim_curve_z.KeyGetCount()):
                        key = anim_curve_z.KeyGet(key_index)
                        time = key.GetTime().GetSecondDouble()
                        value = key.GetValue()
                        print(f"      Time: {time}, Value: {value}")


def get_error_list(curve):
    keys_to_remove = []
    for key_index in range(curve.KeyGetCount()):
        print(curve.KeyGetValue(key_index))
        if curve.KeyGetValue(key_index) < curve.KeyGetValue(0):
            keys_to_remove.append(key_index)
    return keys_to_remove


def linear_anim(curve, key_error_list):
    if len(key_error_list) == 0:
        return
    for index in reversed(key_error_list):
        curve.KeyRemove(index)


def linear_animation_data(node, scene):
    # 获取动画堆栈（通常只有一个）
    anim_stack_count = scene.GetSrcObjectCount(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId))
    for i in range(anim_stack_count):
        anim_stack = scene.GetSrcObject(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId), i)
        scene.SetCurrentAnimationStack(anim_stack)
        print(f"Animation stack: {anim_stack.GetName()}")

        # 获取动画层
        anim_layer_count = anim_stack.GetMemberCount()
        for j in range(anim_layer_count):
            anim_layer = anim_stack.GetMember(j)
            print(f"  Animation layer: {anim_layer.GetName()}")

            # 获取scale曲线数据
            if node.GetName() == 'Skeleton0Hips':
                anim_curve_node = node.LclScaling.GetCurveNode(anim_layer)
                anim_curve_x = anim_curve_node.GetCurve(0)
                global key_error_list
                key_error_list = get_error_list(anim_curve_x)
            # 获取动画曲线节点
            anim_curve_nodes = [node.LclTranslation.GetCurveNode(anim_layer), node.LclRotation.GetCurveNode(anim_layer), node.LclScaling.GetCurveNode(anim_layer)]
            for anim_curve_node in anim_curve_nodes:
                if anim_curve_node:
                    print(f"    Animation curve node: {anim_curve_node.GetName()}")
                    # 获取动画曲线
                    for axis in range(3):
                        key_error_list_cp = key_error_list.copy()
                        linear_anim(anim_curve_node.GetCurve(axis), key_error_list_cp)


def remove_anim(curve, start_time, end_time):
    keys_to_remove = []
    for key_index in range(curve.KeyGetCount()):
        time = curve.KeyGetTime(key_index).GetSecondDouble()
        if time > start_time and time < end_time:
            keys_to_remove.append(key_index)

    remove_length = len(keys_to_remove)
    i = curve.KeyGetCount()
    while i > keys_to_remove[-1]:
        tmp = curve.KeyGetTime(i-remove_length)
        curve.KeySetTime(i, tmp)
        i -= 1

    for index in reversed(keys_to_remove):
        curve.KeyRemove(index)


def delete_animation_data(node, scene, start_time, end_time):
    # 获取动画堆栈（通常只有一个）
    anim_stack_count = scene.GetSrcObjectCount(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId))
    for i in range(anim_stack_count):
        anim_stack = scene.GetSrcObject(fbx.FbxCriteria.ObjectType(fbx.FbxAnimStack.ClassId), i)
        scene.SetCurrentAnimationStack(anim_stack)
        print(f"Animation stack: {anim_stack.GetName()}")

        # 获取动画层
        anim_layer_count = anim_stack.GetMemberCount()
        for j in range(anim_layer_count):
            anim_layer = anim_stack.GetMember(j)
            print(f"  Animation layer: {anim_layer.GetName()}")

            # 获取动画曲线节点
            anim_curve_nodes = [node.LclTranslation.GetCurveNode(anim_layer), node.LclRotation.GetCurveNode(anim_layer), node.LclScaling.GetCurveNode(anim_layer)]
            for anim_curve_node in anim_curve_nodes:
                if anim_curve_node:
                    print(f"    Animation curve node: {anim_curve_node.GetName()}")
                    # 获取动画曲线
                    anim_curve_x = anim_curve_node.GetCurve(0)
                    anim_curve_y = anim_curve_node.GetCurve(1)
                    anim_curve_z = anim_curve_node.GetCurve(2)

                    remove_anim(anim_curve_x, start_time, end_time)
                    remove_anim(anim_curve_y, start_time, end_time)
                    remove_anim(anim_curve_z, start_time, end_time)


def traverse_nodes(node, scene):
    # 打印当前节点的名称
    print(f"Node name: {node.GetName()}")
    #get_animation_data(node, scene)
    #delete_animation_data(node, scene)
    linear_animation_data(node, scene)
    # 遍历子节点
    for i in range(node.GetChildCount()):
        traverse_nodes(node.GetChild(i), scene)


key_error_list = []

filename = r"D:\ExportedAsset2\Game\2024-07-31\Scene_1_05_Subscenes\Animation\BP_TakeRecordingExporter_Scene_1_05.FBX" # 文件路径
manager, scene = FbxCommon.InitializeSdkObjects() # 初始化
FbxCommon.LoadScene(manager, scene, filename) # 加载场景

root_node = scene.GetRootNode()
# 单位：秒
#traverse_nodes(root_node, scene, 5, 10)
traverse_nodes(root_node, scene)

export_file = r"D:\ExportedAsset2\Game\2024-07-31\Scene_1_05_Subscenes\Animation\BP_output.FBX"
FbxCommon.SaveScene(manager, scene, export_file)

manager.Destroy()