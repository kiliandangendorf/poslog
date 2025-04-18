#!/bin/bash
# Usage: ./download_datasets.sh [remove]

# List of download links and names separated by comma
LINKS=(
    'https://zenodo.org/records/8196385/files/HDFS_v1.zip?download=1,HDFS_v1.zip'
    # 'https://zenodo.org/records/8196385/files/HDFS_v2.zip?download=1,HDFS_v2.zip'
    'https://zenodo.org/records/8196385/files/HDFS_v3_TraceBench.zip?download=1,HDFS_v3_TraceBench.zip'
    'https://zenodo.org/records/8196385/files/Hadoop.zip?download=1,Hadoop.zip'
    'https://zenodo.org/records/8196385/files/Spark.tar.gz?download=1,Spark.tar.gz'
    'https://zenodo.org/records/8196385/files/Zookeeper.tar.gz?download=1,Zookeeper.tar.gz'
    'https://zenodo.org/records/8196385/files/OpenStack.tar.gz?download=1,OpenStack.tar.gz'
    'https://zenodo.org/records/8196385/files/BGL.zip?download=1,BGL.zip'
    'https://zenodo.org/records/8196385/files/HPC.zip?download=1,HPC.zip'
    # 'https://zenodo.org/records/8196385/files/Thunderbird.tar.gz?download=1,Thunderbird.tar.gz'
    # 'https://zenodo.org/records/8196385/files/Windows.tar.gz?download=1,Windows.tar.gz'
    'https://zenodo.org/records/8196385/files/Linux.tar.gz?download=1,Linux.tar.gz'
    'https://zenodo.org/records/8196385/files/Mac.tar.gz?download=1,Mac.tar.gz'
    'https://zenodo.org/records/8196385/files/Android_v1.zip?download=1,Android_v1.zip'
    'https://zenodo.org/records/8196385/files/Android_v2.zip?download=1,Android_v2.zip'
    'https://zenodo.org/records/8196385/files/HealthApp.tar.gz?download=1,HealthApp.tar.gz'
    'https://zenodo.org/records/8196385/files/Apache.tar.gz?download=1,Apache.tar.gz'
    'https://zenodo.org/records/8196385/files/SSH.tar.gz?download=1,SSH.tar.gz'
    'https://zenodo.org/records/8196385/files/Proxifier.tar.gz?download=1,Proxifier.tar.gz'
)

REMOVE_ZIP_FILES=true


# Check if 'remove' option is provided
if [ "$1" = "remove" ]; then
    # Prompt for confirmation
    read -p "Are you sure you want to remove all folders in the list? (yes/no): " answer
    if [ "$answer" = "yes" ]; then
        if [ -d "loghub" ]; then
            echo "- Removing loghub repository"
            rm -rf "loghub"
        fi

        # Remove all folders in the list
        for link in "${LINKS[@]}"; do
            filename="${link#*,}"
            folder="${filename%%.*}"
            if [ -d "$folder" ]; then
                echo "- Removing folder $folder"
                rm -rf "$folder"
            fi
        done
        echo "Done"
        exit 0
    else
        echo "Aborted. No folders will be removed."
        exit 1
    fi
fi


LINE_SEPARATOR="#############################################"

# Clone loghub repository
echo "$LINE_SEPARATOR"
echo "Cloning loghub repository"
if [ ! -d "loghub" ]; then
    git clone https://github.com/logpai/loghub.git
else
    echo "loghub repository already exists"
fi



# Download datasets
for new_link in "${LINKS[@]}"; do
    new_url="${new_link%%,*}"
    new_filename="${new_link#*,}"
    new_folder="${new_filename%%.*}"
    echo "$LINE_SEPARATOR"
    echo  "$new_folder"

    if [ ! -d "$new_folder" ]; then
        echo "Downloading $new_filename from $new_url"
        wget "$new_url" -O "$new_filename"
        echo "Unzipping $new_filename to $new_folder"

        if [[ "$new_filename" == *.zip ]]; then
            unzip "$new_filename" -d "$new_folder"
        elif [[ "$new_filename" == *.tar.gz ]]; then
            mkdir "$new_folder"
            tar -xzf "$new_filename" -C "$new_folder"
        fi

        # only remove file if unzipping was successful
        if [ $? -eq 0 ]; then
            if [ "$REMOVE_ZIP_FILES" = true ]; then
            echo "Removing zip file $new_filename"
            rm "$new_filename"
            fi
        else
            echo "Unzipping $new_filename failed"
        fi
    else
        echo "Folder $new_folder already exists, skip"
    fi
done

echo "$LINE_SEPARATOR"
echo "Done"