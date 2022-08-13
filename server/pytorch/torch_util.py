import matplotlib.pyplot as plt
import torch


def init_seeds(seed=0):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def select_device(force_cpu=False):
    cuda = False if force_cpu else torch.cuda.is_available()
    device = torch.device('cuda:0' if cuda else 'cpu')
    if not cuda:
        print('Using CPU')
    if cuda:
        mb_unit = 2 ** 20  # 单位: MB
        ng = torch.cuda.device_count()  # 显卡张数
        device_properties = [torch.cuda.get_device_properties(i) for i in range(ng)]
        print("Using CUDA device0 _CudaDeviceProperties(name='%s', total_memory=%dMB)" %
              (device_properties[0].name, device_properties[0].total_memory / mb_unit))
        if ng > 0:
            # pytorch.cuda.set_device(0)  # OPTIONAL: Set GPU ID
            for i in range(1, ng):
                print("           device%g _CudaDeviceProperties(name='%s', total_memory=%dMB)" %
                      (i, device_properties[i].name, device_properties[i].total_memory / mb_unit))
    print('')  # skip a line
    return device


# 数据可视化
def plot_result(path):
    fig = plt.figure(15)
    with open(path, "r") as f:
        import csv
        f_csv = csv.reader(f)
        epoch, acc = [], []
        for row in f_csv:
            print(row)
            epoch.append(int(row[0]))
            acc.append(float(row[1]))
        plt.plot(epoch, acc)
    plt.title("result-epoch&acc")
    plt.xlabel("epoch")
    plt.ylabel("accuracy")
    plt.show()
    fig.savefig("results.png", dpi=300)
