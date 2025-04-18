# Datasets

Currently there are the following 16 datasets listed in [Loghub](https://github.com/logpai/loghub/tree/master):
- Android (v1, v2)
- Apache
- BGL
- Hadoop
- HDFS (v1, v2, v3)
- HealthApp
- HPC
- Linux
- Mac
- OpenSSH
- OpenStack
- Proxifier
- Spark
- Thunderbird
- Windows
- Zookeeper

## 2k Datasets

[Loghub](https://github.com/logpai/loghub/tree/master) provides the first 2000 lines of each dataset for analysis purposes next to ground truth labels of events templates.
To download only the 2k datasets, just clone the repository into this directory:
```bash
git clone https://github.com/logpai/loghub.git
```

## Download Script

Use `download_datasets.sh` to download 2k datasets from [Loghub](https://github.com/logpai/loghub/tree/master) 
__and__ whole datasets from [zenodo](https://zenodo.org/records/8196385) into this directory.

On first use you may need to make the script executable:
```bash
chmod +x download_datasets.sh
```
    
Then run the script:
```bash
./download_datasets.sh
```

You will find the 2k datasets in the `loghub` directory.

### Exclude Datasets

The whole disk usage of all datasets is about 92 GB.

As they are very large, we recommend to exclude `HDFS_v2` (16 GB), `Thunderbird` (29 GB) and `Windows` (26 GB).

To exclude datasets from the download, comment out the corresponding lines in the script.
```bash
LINKS=(
    'https://zenodo.org/records/8196385/files/HDFS_v1.zip?download=1,HDFS_v1.zip'
    # 'https://zenodo.org/records/8196385/files/HDFS_v2.zip?download=1,HDFS_v2.zip'
    'https://zenodo.org/records/8196385/files/HDFS_v3_TraceBench.zip?download=1,HDFS_v3_TraceBench.zip'
    [...]
```

### Remove Datasets

To remove datasets use the script with the parameter `remove` and type `"yes"`:
```bash
./download_datasets.sh remove
```

This will only remove datasets in the list mentioned above.
Manually added folder will stay untouched.

# Public MQTT Broker

We thought about using data of a public MQTT broker as they are similar to log data of a CPS.
Using [`mosquitto_sub`](https://mosquitto.org/download/) we can subscribe to all topics and receive messages:
```bash
mosquitto_sub -h test.mosquitto.org -v -t '#' > test-mosquitto-org.txt
```

