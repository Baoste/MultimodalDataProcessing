# import unreal

# 获取资产注册表
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()

# 获取 AssetTools 实例
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

# 设置要搜索的根路径
root_search_path = "/Game/2024-08-09/"

# 获取根路径下的所有资产（递归搜索）
all_assets = asset_registry.get_assets_by_path(root_search_path, recursive=True)

# 过滤出资产
audio_assets = [asset_data for asset_data in all_assets if 'audio/' in str(asset_data.package_name).lower()]
anim_assets = [asset_data for asset_data in all_assets if 'animation/' in str(asset_data.package_name).lower()]

# 提取资产路径
audio_asset_paths = [asset_data.package_name for asset_data in audio_assets]
anim_asset_paths = [asset_data.package_name for asset_data in anim_assets]
asset_paths = audio_asset_paths + anim_asset_paths

# 设置导出路径
export_path = "D:/ExportedAsset"

# 导出资产
asset_tools.export_assets(asset_paths, export_path)