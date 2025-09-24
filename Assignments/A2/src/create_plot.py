import numpy
import matplotlib.pyplot as plt

nodes = [1, 2, 4, 8, 16]

node1_puts = [0.30568456649780273, 0.27170443534851074, 0.2843461036682129]
node1_gets = [0.2817678451538086, 0.2361757755279541, 0.26893186569213867]

node1_average_put = (node1_puts[0] + node1_puts[1] + node1_puts[2]) / 3
node1_average_get = (node1_gets[0] + node1_gets[1] + node1_gets[2]) / 3 

node1_std_dev_put = numpy.std(node1_puts)
node1_std_dev_get = numpy.std(node1_gets)



node2_puts = [0.52469801902771, 0.5558199882507324, 0.41277146339416504]
node2_gets = [0.5126934051513672, 0.5380280017852783, 0.40242433547973633]
node2_average_put = (node2_puts[0] + node2_puts[1] + node2_puts[2]) / 3
node2_average_get = (node2_gets[0] + node2_gets[1] + node2_gets[2]) / 3 

node2_std_dev_put = numpy.std(node2_puts)
node2_std_dev_get = numpy.std(node2_gets)



node4_puts = [0.691889762878418, 0.65549635887146, 0.7748928070068359]
node4_gets = [0.6803514957427979, 0.7265689373016357, 0.7540161609649658]
node4_average_put = (node4_puts[0] + node4_puts[1] + node4_puts[2]) / 3
node4_average_get = (node4_gets[0] + node4_gets[1] + node4_gets[2]) / 3 

node4_std_dev_put = numpy.std(node4_puts)
node4_std_dev_get = numpy.std(node4_gets)



node8_puts = [0.9271430969238281, 1.0919997692108154, 0.9891641139984131]
node8_gets = [1.130223274230957, 1.5038959980010986, 1.8829662799835205]
node8_average_put = (node8_puts[0] + node8_puts[1] + node8_puts[2]) / 3
node8_average_get = (node8_gets[0] + node8_gets[1] + node8_gets[2]) / 3

node8_std_dev_put = numpy.std(node8_puts)
node8_std_dev_get = numpy.std(node8_gets)



node16_puts = [1.308884859085083, 1.302492380142212, 1.2213785648345947]
node16_gets = [2.25162935256958, 2.781196117401123, 2.4858579635620117]
node16_average_put = (node16_puts[0] + node16_puts[1] + node16_puts[2]) / 3
node16_average_get = (node16_gets[0] + node16_gets[1] + node16_gets[2]) / 3

node16_std_dev_put = numpy.std(node16_puts)
node16_std_dev_get = numpy.std(node16_gets)







#CHATGPT
# Average PUT times
avg_puts = [
    node1_average_put,
    node2_average_put,
    node4_average_put,
    node8_average_put,
    node16_average_put,
]

# Average GET times
avg_gets = [
    node1_average_get,
    node2_average_get,
    node4_average_get,
    node8_average_get,
    node16_average_get,
]

# Standard deviation of PUT times
std_puts = [
    node1_std_dev_put,
    node2_std_dev_put,
    node4_std_dev_put,
    node8_std_dev_put,
    node16_std_dev_put,
]


# Standard deviation of GET times
std_gets = [
    node1_std_dev_get,
    node2_std_dev_get,
    node4_std_dev_get,
    node8_std_dev_get,
    node16_std_dev_get,
]

# Plot with error bars
plt.errorbar(nodes, avg_puts, xerr=0 , yerr=std_puts, fmt='-o', color="red", ecolor="red", capsize=5, elinewidth=1, label="PUT (avg ± std)")
plt.errorbar(nodes, avg_gets, xerr=0, yerr=std_gets, fmt='-o', color="blue", ecolor="blue", capsize=5, elinewidth=1, label="GET (avg ± std)")

plt.xlabel("Number of Nodes in network")
plt.ylabel("Time (seconds)")
plt.title("Time to PUT and GET 100 different values in DHT")
plt.legend()
plt.grid(True)
plt.show()


"""
1 node:
    Try 1:
        Time used put: 0.30568456649780273
        Time used get: 0.2817678451538086

    Try 2:
        Time used put: 0.27170443534851074
        Time used get: 0.2361757755279541
        
    Try 3:
        Time used put: 0.2843461036682129
        Time used get: 0.26893186569213867

2 nodes:
    Try 1:
        Time used put: 0.52469801902771
        Time used get: 0.5126934051513672

    Try 2:
        Time used put: 0.5558199882507324
        Time used get: 0.5380280017852783
    
    Try 3:
        Time used put: 0.41277146339416504
        Time used get: 0.40242433547973633

4 nodes:
    Try 1:
        Time used put: 0.691889762878418
        Time used get: 0.6803514957427979

    Try 2:
        Time used put: 0.65549635887146
        Time used get: 0.7265689373016357
    
    Try 3:
        Time used put: 0.7748928070068359
        Time used get: 0.7540161609649658

8 nodes:
    Try 1:
        Time used put: 0.9271430969238281
        Time used get: 1.130223274230957

    Try 2:
        Time used put: 1.0919997692108154
        Time used get: 1.5038959980010986

    Try 3:
        Time used put: 0.9891641139984131
        Time used get: 1.8829662799835205

16 nodes:
    Try 1:
        Time used put: 1.308884859085083
        Time used get: 2.25162935256958

    Try 2:
        Time used put: 1.302492380142212
        Time used get: 2.781196117401123
    
    Try 3:
        Time used put: 1.2213785648345947
        Time used get: 2.4858579635620117
"""