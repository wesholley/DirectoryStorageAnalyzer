import os
import csv
from os.path import join, getsize
import math

CSVPATH = "/Users/family/Desktop/test/usage.csv"
pathsToExclude = ['/Users/family/Pictures/Lightroom/']

# #
# Object to represent a directory and store all the status for that directory, namely:
#   -How much space each folder occupies
#   -How many files are in each folder
#   -Space taken by images
#   -Space taken by videos
#   -Space taken by other file types
#   -Percentage of images by file type
##
class DirectoryRecord(object):
    path = ""
    size = 0
    fileCount = 0
    subdirectoryCount = 0
    sizeOfImages = 0
    sizeOfVideos = 0
    sizeOfOtherFiles = 0
    percentageOfImages = 0

    def __init__(self, path, size):
        self.path = path
        self.size = size

def make_directory_record(path, size):
    directory = DirectoryRecord(path, size)
    return directory

def make_directory_record(path, size, fileCount, subdirectoryCount, sizeOfImages, sizeOfVideos, sizeOfOtherFiles):
    directory = DirectoryRecord(path, size)
    directory.fileCount = fileCount
    directory.subdirectoryCount = subdirectoryCount
    directory.sizeOfImages = sizeOfImages
    directory.sizeOfVideos = sizeOfVideos
    directory.sizeOfOtherFiles = sizeOfOtherFiles
    if size > 0:
        directory.percentageOfImages = round(((sizeOfImages + sizeOfVideos) / size) * 100, 1)
    else:
        directory.percentageOfImages = 0
    return directory


##
# Takes a size in bytes and returns it in a more readable format (KB, MB, GB, etc.)
#
# Each denomination is determined as a function of 1024^n. For bytes n=0, KB n=1, MB n=2, etc.).
# Using a logarithm, we can determine the power of 1024 to arrive at the size in bytes, then used
# to determine the right denomination to return.  The bytes / 1024^n gives the size conversion.
#
# Obtained from: https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
#
#
def readable_size(size_bytes):
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    if size_bytes == 0:
        return 0, size_name[0]
    i = int(math.floor(math.log(size_bytes, 1000)))
    p = math.pow(1000, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


##
#   Walks the directory tree starting at 'dir'
##
def walk_folder(path):
    imageExtensions = ['.aae', '.cr2', '.dcm', '.dng', '.gif', '.jpeg', '.jpg', '.nef', '.pdf', '.png', '.psd', '.srw',
                       '.thm', '.tif', '.tiff']
    videoExtensions = ['.wmv', '.mp4', '.mov', '.m4v', '.m4a', 'mov', '.avi']

    dirs_dict = {}
    record_dict = {}
    # Walk the tree bottom-up so that a directory has access to subdirectory sizes
    for root, dirs, files in os.walk(path, topdown=False):
        # Loop through every non directory file in this directory and sum their sizes
        size = sum(getsize(os.path.join(root, name)) for name in files)

        # Look at all of the subdirectories and add up their sizes from the `dirs_dict`
        subdir_size = sum(dirs_dict[os.path.join(root, d)] for d in dirs)

        # store the size of this directory (plus subdirectories) in a dict so we
        # can access it later
        my_size = dirs_dict[root] = size + subdir_size

        # ----------------- other file properties ------------------------

        fileCount = len(files)
        subDirectoryCount = len(dirs)

        # filter out non-image files
        images = list([os.path.join(root, x) for x in files if
                       os.path.splitext(os.path.join(root, x))[1].lower() in imageExtensions])
        sizeOfImages = sum(getsize(image) for image in images)

        # filter out non-video files
        videos = list([os.path.join(root, x) for x in files if
                       os.path.splitext(os.path.join(root, x))[1].lower() in videoExtensions])
        sizeOfVideos = sum(getsize(video) for video in videos)

        # size of all non-image, non-video files
        otherFiles = list([os.path.join(root, x) for x in files if
                           os.path.splitext(os.path.join(root, x))[1].lower() not in imageExtensions + videoExtensions])
        sizeOfOtherFiles = sum(getsize(otherFile) for otherFile in otherFiles)

        if my_size > 0:
            percentageOfImages = round(((sizeOfImages + sizeOfVideos) / size) * 100, 1)
        else:
            percentageOfImages = 0

        directory_record = make_directory_record(root,my_size,fileCount,subDirectoryCount,sizeOfImages,sizeOfVideos,sizeOfOtherFiles)
        record_dict[root] = directory_record

        print("results: %s: %s" % (root, readable_size(my_size)))


def main():
    walk_folder("/Users/family/Pictures/2017/04 April/Wes")
    # rootdir = "/Users/family/Movies/P90X"


if __name__ == "__main__":
    main()
