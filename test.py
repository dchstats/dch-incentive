import argparse

if __name__ == '__main__':
    argvparser = argparse.ArgumentParser()
    argvparser.add_argument('-i', '--input', help='Zip file name')
    args = argvparser.parse_args()
    print(args.input)