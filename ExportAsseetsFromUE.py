# import unreal

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

# 设置要搜索的根路径
root_search_path = "/Game/2024-08-09/"

all_assets = asset_registry.get_assets_by_path(root_search_path, recursive=True)

# 过滤出资产
audio_assets = [asset_data for asset_data in all_assets if 'audio/' in str(asset_data.package_name).lower()]
anim_assets = [asset_data for asset_data in all_assets if 'animation/' in str(asset_data.package_name).lower()]

audio_asset_paths = [asset_data.package_name for asset_data in audio_assets]
anim_asset_paths = [asset_data.package_name for asset_data in anim_assets]
asset_paths = audio_asset_paths + anim_asset_paths


export_path = "D:/ExportedAsset"    # 导出路径
asset_tools.export_assets(asset_paths, export_path)