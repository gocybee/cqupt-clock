import hanlp

level1_set = {"乡", "镇", "街道", "民族乡", "苏木"}
level2_set = {"大道", "大街", "胡同", "横路", "横街", "纵路", "纵街", "弄", "线", "路", "街", "巷", "条"}
level3_set = {"小区", "公寓", "村", "沟", "屯", "里", "坊", "横", "队", "社",
              "大厦", "商场", "商城", "公司", "宾馆", "别墅", "商店", "所"}
level4_set = {"栋", "号楼", "楼", "座", "型", "阁", "号", "组团"}
level5_set = {"#", "楼", "层", "室", "房", "组", "号"}

digit_number_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
small_chinese_number_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
big_chinese_number_list = ["零", "壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖"]
small_letter_list = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                     "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
capital_letter_list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
                       "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
connect_char_list = ["、", "-"]

number_set = set()
number_set.update(digit_number_list)
number_set.update(small_chinese_number_list)
number_set.update(big_chinese_number_list)
number_set.update(small_letter_list)
number_set.update(capital_letter_list)

single_range_set = set()
single_range_set.update(number_set)
single_range_set.update({"-"})

range_set = set()
range_set.update(number_set)
range_set.update(connect_char_list)

set_list = [set(), level1_set, level2_set, level3_set, level4_set, level5_set]

# 初始化分词模型
tok = hanlp.pipeline() \
    .append(hanlp.load(hanlp.pretrained.tok.CTB9_TOK_ELECTRA_SMALL))

# 初始化语义相似模型
sts = hanlp.pipeline() \
    .append(hanlp.load(hanlp.pretrained.sts.STS_ELECTRA_BASE_ZH))


def match_address(src_address, dst_address):
    s_end, s_begin = find_next_range_block(src_address)
    d_end, d_begin = find_next_range_block(dst_address)
    while s_begin != 0 and d_begin != 0:
        if match_range_block(src_address[s_begin:s_end + 1], dst_address[d_begin:d_end + 1]):
            dst_address = dst_address.replace(dst_address[d_begin:d_end + 1], src_address[s_begin:s_end + 1])
        s_end, s_begin = find_next_range_block(src_address[:s_begin])
        d_end, d_begin = find_next_range_block(dst_address[:d_begin])

    if sts((src_address, dst_address)) > 0.80:
        return True
    return False


def find_next_range_block(address):
    begin = len(address) - 1
    for begin in range(begin, -1, -1):
        if address[begin] in number_set:
            break

    end = begin
    for end in range(end, -1, -1):
        if not (address[end] in range_set):
            break

    if end == 0:
        end -= 1

    return begin, end + 1


def match_range_block(src_range_block, dst_range_block):
    s_begin = 0
    s_end = len(src_range_block) - 1
    d_begin = 0
    d_end = len(dst_range_block) - 1
    while s_end != 0 and d_end != 0:
        d_end = d_begin + find_next_single_range_block(dst_range_block[d_begin:])
        if match_single_range_block(src_range_block[s_begin:s_end + 1], dst_range_block[d_begin:d_end + 1]):
            return True
        d_begin = d_end + 2
    return False


def find_next_single_range_block(range_block):
    end = 0
    for end in range(end, len(range_block), 1):
        if not (range_block[end] in single_range_set):
            break

    if range_block[end] == '、':
        end -= 1

    return end


def match_single_range_block(src_single_range_block, dst_single_range_block):
    src_single_range_block = convert_number(src_single_range_block)
    dst_single_range_block = convert_number(dst_single_range_block)

    if not dst_single_range_block.__contains__('-'):
        if src_single_range_block == dst_single_range_block:
            return True
        return False

    index = dst_single_range_block.find('-')
    left_number = int(dst_single_range_block[:index])
    right_number = int(dst_single_range_block[index + 1:])
    if left_number <= int(src_single_range_block) <= right_number:
        return True
    return False


def convert_number(numbers):
    i = 0
    for i in range(i, len(numbers), 1):
        if numbers[i] in number_set:
            if numbers[i] in digit_number_list:
                continue
            if numbers[i] in small_chinese_number_list:
                numbers = numbers.replace(numbers[i], str(small_chinese_number_list.index(numbers[i])))
                continue
            elif numbers[i] in big_chinese_number_list:
                numbers = numbers.replace(numbers[i], str(big_chinese_number_list.index(numbers[i])))
                continue
            elif numbers[i] in small_letter_list:
                numbers = numbers.replace(numbers[i], str(small_letter_list.index(numbers[i])))
                continue
            elif numbers[i] in capital_letter_list:
                numbers = numbers.replace(numbers[i], str(capital_letter_list.index(numbers[i])))
                continue
            elif numbers[i] in connect_char_list:
                numbers = numbers.replace(numbers[i], str(connect_char_list.index(numbers[i])))
                continue
    return numbers
