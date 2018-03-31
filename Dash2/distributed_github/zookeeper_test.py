import sys; sys.path.extend(['../../'])
from kazoo.client import KazooClient
import time
import json
import random
from heapq import heappush, heappop
from Dash2.github.git_repo import GitRepo
from Dash2.distributed_github.zk_git_repo import ZkGitRepo
from Dash2.github.git_user_agent import GitUserAgent
from zk_repo_hub import ZkRepoHub

def get_entity_path(entity_id):
    path = ""
    id = int(entity_id)
    for i in range(5, 0, -1):
        path = path + str(id / pow(10, i)) + "/"
        id = id % pow(10, i)
    path = path + str(id)
    #print path
    return path

if __name__ == "__main__":
    # zookeeper stress test (many requests)
    #get_entity_path(sys.argv[1])
    node_prefix = sys.argv[1]
    if node_prefix is None:
        node_prefix = "/test/"
    zk_hosts = '127.0.0.1:2181'
    zk = KazooClient(zk_hosts)
    zk.start()
    #zk.delete(path="/test", recursive=True)

    start_time = time.time()
    print "start time: ", start_time
    node_path = ""
    for node_id in range(0, 1000000, 1):
        node_path = node_prefix  + str(node_id)
        #zk.ensure_path(node_path)
        # 800 bytes of data:
        #zk.create(path=path_, makepath=True, ephemeral=True, value='{"id": 269793, "f": {"176974": 1, "67412": 1, "50332": 1, "84566": 1, "150357": 1, "277860": 1, "136832": 1, "1683179": 1, "452369": 1, "2310913": 1, "37075": 1, "8097": 1, "76173": 1, "654980": 1, "10180": 1, "302662": 1, "276578": 1, "182103": 1, "52151": 1, "965916": 1, "4207319": 4, "81302": 1, "668000": 1, "1926660": 1, "34429": 2, "4012243": 1, "295230": 1, "4312": 1, "2766793": 1, "317459": 1, "68268": 1, "29589": 1, "2058255": 1, "8392": 1, "3083448": 1, "20782": 2, "35459": 1, "271750": 1, "5898": 1, "2046719": 1, "352298": 1, "1138346": 1, "223928": 1, "2215": 1, "4206059": 7, "1013359": 1, "3700896": 1, "933672": 1, "2298628": 46, "3599910": 1, "3840": 1, "49163": 1, "268312": 1, "4376451": 8, "220206": 1, "545421": 1, "9798": 1, "3813987": 1, "141720": 1}}')
        # 70 bytes of data:
        #zk.create(path=path_, makepath=True, ephemeral=False, value='{"id": 269793, "f": {"176974": 1, "67412": 1, "50332": 1}}')

        lock = zk.Lock(node_path)
        lock.acquire()
        val, _ = zk.get(path=node_path)
        zk.set(path=node_path,
               value='{"id": 269793, "f": {"176974": 10, "67412": 10, "50332": 10}}'+str(val))
        lock.release()
        if node_id % 1000 == 0 and node_id > 1000:
            delta = (time.time() - start_time) / (node_id / 1000)
            print "Node is ", node_id, ', rate: ', delta
    end_time = time.time()

    print "Total time: ", (start_time - end_time)
    zk.delete(path="/test", recursive=True)
    zk.stop()
