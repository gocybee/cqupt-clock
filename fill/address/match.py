level1_set = {"特别行政区", "自治区", "省"}
level2_set = {"自治州", "地区", "市", "萌"}
level3_set = {"自治县", "自治旗", "林区", "特区", "县", "区", "旗"}
level4_set = {"乡", "镇", "街道", "民族乡", "苏木"}
level5_set = {"大道", "大街", "胡同", "横路", "横街", "纵路", "纵街", "弄", "线", "路", "街", "巷", "条"}
level6_set = {"小区", "公寓", "村", "沟", "屯", "里", "坊", "横", "队", "社",
              "大厦", "商场", "商城", "公司", "宾馆", "别墅", "商店", "所"}
level7_set = {"栋", "号楼", "楼", "座", "型", "阁", "号"}
level8_set = {"#", "楼", "层", "室", "房", "组", "号"}


# TODO: 地址匹配算法
def match_address(src_address, dst_address):
    if level1_set.issubset(src_address):
        return True
    return False
